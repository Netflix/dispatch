"""
Originally authoried by:
https://github.com/kvesteri/sqlalchemy-searchable/blob/master/sqlalchemy_searchable
"""
import os
from functools import reduce

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.base import RESERVED_WORDS
from sqlalchemy.schema import DDL
from sqlalchemy_utils import TSVectorType

from .vectorizers import Vectorizer


vectorizer = Vectorizer()


class SearchQueryMixin(object):
    def search(self, search_query, vector=None, regconfig=None, sort=False):
        """
        Search given query with full text search.

        :param search_query: the search query
        :param vector: search vector to use
        :param regconfig: postgresql regconfig to be used
        :param sort: order results by relevance (quality of hit)
        """
        return search(self, search_query, vector=vector, regconfig=regconfig, sort=sort)


def inspect_search_vectors(entity):
    return [
        getattr(entity, key).property.columns[0]
        for key, column in sa.inspect(entity).columns.items()
        if isinstance(column.type, TSVectorType)
    ]


def search(query, search_query, vector=None, regconfig=None, sort=False):
    """
    Search given query with full text search.

    :param search_query: the search query
    :param vector: search vector to use
    :param regconfig: postgresql regconfig to be used
    :param sort: order results by relevance (quality of hit)
    """
    if not search_query.strip():
        return query

    if vector is None:
        entity = query._entities[0].entity_zero.class_
        search_vectors = inspect_search_vectors(entity)
        vector = search_vectors[0]

    if regconfig is None:
        regconfig = search_manager.options["regconfig"]

    query = query.filter(vector.op("@@")(sa.func.tsq_parse(regconfig, search_query)))
    if sort:
        query = query.order_by(sa.desc(sa.func.ts_rank_cd(vector, sa.func.tsq_parse(search_query))))

    return query.params(term=search_query)


def quote_identifier(identifier):
    """Adds double quotes to given identifier. Since PostgreSQL is the only
    supported dialect we don't need dialect specific stuff here"""
    return '"%s"' % identifier


class SQLConstruct(object):
    def __init__(self, tsvector_column, conn=None, indexed_columns=None, options=None):
        self.table = tsvector_column.table
        self.tsvector_column = tsvector_column
        self.conn = conn
        self.options = self.init_options(options)
        if indexed_columns:
            self.indexed_columns = list(indexed_columns)
        elif hasattr(self.tsvector_column.type, "columns"):
            self.indexed_columns = list(self.tsvector_column.type.columns)
        else:
            self.indexed_columns = None
        self.params = {}

    def init_options(self, options=None):
        if not options:
            options = {}
        for key, value in SearchManager.default_options.items():
            try:
                option = self.tsvector_column.type.options[key]
            except (KeyError, AttributeError):
                option = value
            options.setdefault(key, option)
        return options

    @property
    def table_name(self):
        if self.table.schema:
            return '%s."%s"' % (self.table.schema, self.table.name)
        else:
            return '"' + self.table.name + '"'

    @property
    def search_function_name(self):
        return self.options["search_trigger_function_name"].format(
            table=self.table.name, column=self.tsvector_column.name
        )

    @property
    def search_trigger_name(self):
        return self.options["search_trigger_name"].format(
            table=self.table.name, column=self.tsvector_column.name
        )

    def column_vector(self, column):
        if column.name in RESERVED_WORDS:
            column.name = quote_identifier(column.name)
        value = sa.text("NEW.{column}".format(column=column.name))
        try:
            vectorizer_func = vectorizer[column]
        except KeyError:
            pass
        else:
            value = vectorizer_func(value)
        value = sa.func.coalesce(value, sa.text("''"))
        value = sa.func.to_tsvector(self.options["regconfig"], value)
        if column.name in self.options["weights"]:
            weight = self.options["weights"][column.name]
            value = sa.func.setweight(value, weight)
        return value

    @property
    def search_vector(self):
        vectors = (
            self.column_vector(getattr(self.table.c, column_name))
            for column_name in self.indexed_columns
        )
        concatenated = reduce(lambda x, y: x.op("||")(y), vectors)
        compiled = concatenated.compile(self.conn)
        self.params = compiled.params
        return compiled


class CreateSearchFunctionSQL(SQLConstruct):
    def __str__(self):
        return (
            """CREATE OR REPLACE FUNCTION
                {search_trigger_function_name}() RETURNS TRIGGER AS $$
            BEGIN
                NEW.{search_vector_name} = {ts_vector};
                RETURN NEW;
            END
            $$ LANGUAGE 'plpgsql';
            """
        ).format(
            search_trigger_function_name=self.search_function_name,
            search_vector_name=self.tsvector_column.name,
            ts_vector=self.search_vector,
        )


class CreateSearchTriggerSQL(SQLConstruct):
    @property
    def search_trigger_function_with_trigger_args(self):
        if self.options["weights"] or any(
            getattr(self.table.c, column) in vectorizer for column in self.indexed_columns
        ):
            return self.search_function_name + "()"
        return "tsvector_update_trigger({arguments})".format(
            arguments=", ".join(
                [self.tsvector_column.name, "'%s'" % self.options["regconfig"]]
                + self.indexed_columns
            )
        )

    def __str__(self):
        return (
            "CREATE TRIGGER {search_trigger_name}"
            " BEFORE UPDATE OR INSERT ON {table}"
            " FOR EACH ROW EXECUTE PROCEDURE"
            " {procedure_ddl}".format(
                search_trigger_name=self.search_trigger_name,
                table=self.table_name,
                procedure_ddl=(self.search_trigger_function_with_trigger_args),
            )
        )


class DropSearchFunctionSQL(SQLConstruct):
    def __str__(self):
        return "DROP FUNCTION IF EXISTS %s()" % self.search_function_name


class DropSearchTriggerSQL(SQLConstruct):
    def __str__(self):
        return "DROP TRIGGER IF EXISTS %s ON %s" % (self.search_trigger_name, self.table_name)


class SearchManager:
    default_options = {
        "search_trigger_name": "{table}_{column}_trigger",
        "search_trigger_function_name": "{table}_{column}_update",
        "regconfig": "pg_catalog.english",
        "weights": (),
    }

    def __init__(self, options={}):
        self.options = self.default_options
        self.options.update(options)
        self.processed_columns = []
        self.classes = set()
        self.listeners = []

    def option(self, column, name):
        try:
            return column.type.options[name]
        except (AttributeError, KeyError):
            return self.options[name]

    def search_function_ddl(self, column):
        def after_create(target, connection, **kw):
            clause = CreateSearchFunctionSQL(column, conn=connection)
            connection.execute(str(clause), **clause.params)

        return after_create

    def search_trigger_ddl(self, column):
        """
        Returns the ddl for creating an automatically updated search trigger.

        :param column: TSVectorType typed SQLAlchemy column object
        """
        return DDL(str(CreateSearchTriggerSQL(column)))

    def inspect_columns(self, table):
        """
        Inspects all searchable columns for given class.

        :param table: SQLAlchemy Table
        """
        return [column for column in table.c if isinstance(column.type, TSVectorType)]

    def append_index(self, cls, column):
        sa.Index("_".join(("ix", column.table.name, column.name)), column, postgresql_using="gin")

    def process_mapper(self, mapper, cls):
        columns = self.inspect_columns(mapper.persist_selectable)
        for column in columns:
            if column in self.processed_columns:
                continue

            self.append_index(cls, column)

            self.processed_columns.append(column)

    def add_listener(self, args):
        self.listeners.append(args)
        event.listen(*args)

    def remove_listeners(self):
        for listener in self.listeners:
            event.remove(*listener)
        self.listeners = []

    def attach_ddl_listeners(self):
        # Remove all previously added listeners, so that same listener don't
        # get added twice in situations where class configuration happens in
        # multiple phases (issue #31).
        self.remove_listeners()

        for column in self.processed_columns:
            # This sets up the trigger that keeps the tsvector column up to
            # date.
            if column.type.columns:
                table = column.table
                if self.option(column, "weights") or vectorizer.contains_tsvector(column):
                    self.add_listener((table, "after_create", self.search_function_ddl(column)))
                    self.add_listener(
                        (table, "after_drop", DDL(str(DropSearchFunctionSQL(column))))
                    )
                self.add_listener((table, "after_create", self.search_trigger_ddl(column)))


search_manager = SearchManager()


def sync_trigger(conn, table_name, tsvector_column, indexed_columns, metadata=None, options=None):
    """
    Synchronizes search trigger and trigger function for given table and given
    search index column. Internally this function executes the following SQL
    queries:

    * Drops search trigger for given table (if it exists)
    * Drops search function for given table (if it exists)
    * Creates search function for given table
    * Creates search trigger for given table
    * Updates all rows for given search vector by running a column=column
      update query for given table.


    Example::

        from sqlalchemy_searchable import sync_trigger


        sync_trigger(
            conn,
            'article',
            'search_vector',
            ['name', 'content']
        )


    This function is especially useful when working with alembic migrations.
    In the following example we add a content column to article table and then
    sync the trigger to contain this new column. ::


        from alembic import op
        from sqlalchemy_searchable import sync_trigger


        def upgrade():
            conn = op.get_bind()
            op.add_column('article', sa.Column('content', sa.Text))

            sync_trigger(conn, 'article', 'search_vector', ['name', 'content'])

        # ... same for downgrade


    If you are using vectorizers you need to initialize them in your migration
    file and pass them to this function. ::


        import sqlalchemy as sa
        from alembic import op
        from sqlalchemy.dialects.postgresql import HSTORE
        from sqlalchemy_searchable import sync_trigger, vectorizer


        def upgrade():
            vectorizer.clear()

            conn = op.get_bind()
            op.add_column('article', sa.Column('name_translations', HSTORE))

            metadata = sa.MetaData(bind=conn)
            articles = sa.Table('article', metadata, autoload=True)

            @vectorizer(articles.c.name_translations)
            def hstore_vectorizer(column):
                return sa.cast(sa.func.avals(column), sa.Text)

            op.add_column('article', sa.Column('content', sa.Text))
            sync_trigger(
                conn,
                'article',
                'search_vector',
                ['name_translations', 'content'],
                metadata=metadata
            )

        # ... same for downgrade

    :param conn: SQLAlchemy Connection object
    :param table_name: name of the table to apply search trigger syncing
    :param tsvector_column:
        TSVector typed column which is used as the search index column
    :param indexed_columns:
        Full text indexed column names as a list
    :param metadata:
        Optional SQLAlchemy metadata object that is being used for autoloaded
        Table. If None is given then new MetaData object is initialized within
        this function.
    :param options: Dictionary of configuration options
    """
    if metadata is None:
        metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload=True, autoload_with=conn)
    params = dict(
        tsvector_column=getattr(table.c, tsvector_column),
        indexed_columns=indexed_columns,
        options=options,
        conn=conn,
    )
    classes = [
        DropSearchTriggerSQL,
        DropSearchFunctionSQL,
        CreateSearchFunctionSQL,
        CreateSearchTriggerSQL,
    ]
    for class_ in classes:
        sql = class_(**params)
        conn.execute(str(sql), **sql.params)
    update_sql = table.update().values({indexed_columns[0]: sa.text(indexed_columns[0])})
    conn.execute(update_sql)


def drop_trigger(conn, table_name, tsvector_column, metadata=None, options=None):
    """
    * Drops search trigger for given table (if it exists)
    * Drops search function for given table (if it exists)


    Example::

        from alembic import op
        from sqlalchemy_searchable import drop_trigger


        def downgrade():
            conn = op.get_bind()

            drop_trigger(conn, 'article', 'search_vector')
            op.drop_index('ix_article_search_vector', table_name='article')
            op.drop_column('article', 'search_vector')

    :param conn: SQLAlchemy Connection object
    :param table_name: name of the table to apply search trigger dropping
    :param tsvector_column:
        TSVector typed column which is used as the search index column
    :param metadata:
        Optional SQLAlchemy metadata object that is being used for autoloaded
        Table. If None is given then new MetaData object is initialized within
        this function.
    :param options: Dictionary of configuration options
    """
    if metadata is None:
        metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload=True, autoload_with=conn)
    params = dict(tsvector_column=getattr(table.c, tsvector_column), options=options, conn=conn)
    classes = [
        DropSearchTriggerSQL,
        DropSearchFunctionSQL,
    ]
    for class_ in classes:
        sql = class_(**params)
        conn.execute(str(sql), **sql.params)


path = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(path, "expressions.sql")) as file:
    sql_expressions = DDL(file.read())


def make_searchable(metadata, mapper=sa.orm.mapper, manager=search_manager, options={}):
    manager.options.update(options)
    event.listen(mapper, "instrument_class", manager.process_mapper)
    # event.listen(mapper, "after_configured", manager.attach_ddl_listeners)
    event.listen(metadata, "before_create", sql_expressions)


def remove_listeners(metadata, manager=search_manager, mapper=sa.orm.mapper):
    event.remove(mapper, "instrument_class", manager.process_mapper)
    # event.remove(mapper, "after_configured", manager.attach_ddl_listeners)
    manager.remove_listeners()
    event.remove(metadata, "before_create", sql_expressions)
