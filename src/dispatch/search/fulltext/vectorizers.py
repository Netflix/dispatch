"""
Orginially authored by:
https://github.com/kvesteri/sqlalchemy-searchable/blob/master/sqlalchemy_searchable/vectorizers.py

Vectorizers provide means for changing the way how different column types and
columns are turned into fulltext search vectors.

Type vectorizers
----------------

By default PostgreSQL only knows how to vectorize string columns. If your model
contains for example HSTORE column which you would like to fulltext index you
need to define special vectorization rule for this.

The easiest way to add a vectorization rule is by using the vectorizer
decorator. In the following example we vectorize only the values of all HSTORE
typed columns are models may have.

::

    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import HSTORE
    from sqlalchemy_searchable import vectorizer


    @vectorizer(HSTORE)
    def hstore_vectorizer(column):
        return sa.cast(sa.func.avals(column), sa.Text)


The SQLAlchemy clause construct returned by the vectorizer will be used for all
fulltext indexed columns that are of type HSTORE. Consider the following
model::


    class Article(Base):
        __tablename__ = 'article'

        id = sa.Column(sa.Integer)
        name_translations = sa.Column(HSTORE)
        content_translations = sa.Column(HSTORE)


Now SQLAlchemy-Searchable would create the following search trigger for this
model (with default configuration)

.. code-block:: sql


    CREATE FUNCTION
        textitem_search_vector_update() RETURNS TRIGGER AS $$
    BEGIN
        NEW.search_vector = to_tsvector(
            'simple',
            concat(
                regexp_replace(
                    coalesce(
                        CAST(avals(NEW.name_translations) AS TEXT),
                        ''
                    ),
                    '[-@.]', ' ', 'g'
                ),
                ' ',
                regexp_replace(
                    coalesce(
                        CAST(avals(NEW.content_translations) AS TEXT),
                        ''
                    ),
                    '[-@.]', ' ', 'g'),
                    ' '
                )
            );
        RETURN NEW;
    END
    $$ LANGUAGE 'plpgsql';


Column vectorizers
------------------

Sometimes you may want to set special vectorizer only for specific column. This
can be achieved as follows::


    class Article(Base):
        __tablename__ = 'article'

        id = sa.Column(sa.Integer)
        name_translations = sa.Column(HSTORE)


    @vectorizer(Article.name_translations)
    def name_vectorizer(column):
        return sa.cast(sa.func.avals(column), sa.Text)


.. note::

    Column vectorizers always have precedence over type vectorizers.
"""
from functools import wraps
from inspect import isclass

import sqlalchemy as sa
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.type_api import TypeEngine


class Vectorizer(object):
    def __init__(self, type_vectorizers=None, column_vectorizers=None):
        self.type_vectorizers = {} if type_vectorizers is None else type_vectorizers
        self.column_vectorizers = {} if column_vectorizers is None else column_vectorizers

    def clear(self):
        self.type_vectorizers = {}
        self.column_vectorizers = {}

    def contains_tsvector(self, tsvector_column):
        if not hasattr(tsvector_column.type, "columns"):
            return False
        return any(
            getattr(tsvector_column.table.c, column) in self
            for column in tsvector_column.type.columns
        )

    def __contains__(self, column):
        try:
            self[column]
            return True
        except KeyError:
            return False

    def __getitem__(self, column):
        if column in self.column_vectorizers:
            return self.column_vectorizers[column]
        type_class = column.type.__class__

        if type_class in self.type_vectorizers:
            return self.type_vectorizers[type_class]
        raise KeyError(column)

    def __call__(self, type_or_column):
        """
        Decorator that marks given function as vectorizer for given column or
        type.

        In the following example we add vectorizer for HSTORE type.

        ::

            from sqlalchemy.dialects.postgresql import HSTORE


            @vectorizer(HSTORE)
            def hstore_vectorizer(column):
                return sa.func.avals(column)

        """

        def outer(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            if isclass(type_or_column) and issubclass(type_or_column, TypeEngine):
                self.type_vectorizers[type_or_column] = wrapper
            elif isinstance(type_or_column, sa.Column):
                self.column_vectorizers[type_or_column] = wrapper
            elif isinstance(type_or_column, InstrumentedAttribute):
                prop = type_or_column.property
                if not isinstance(prop, sa.orm.ColumnProperty):
                    raise TypeError(
                        "Given InstrumentedAttribute does not wrap "
                        "ColumnProperty. Only instances of ColumnProperty are "
                        "supported for vectorizer."
                    )
                column = type_or_column.property.columns[0]

                self.column_vectorizers[column] = wrapper
            else:
                raise TypeError(
                    "First argument should be either valid SQLAlchemy type, "
                    "Column, ColumnProperty or InstrumentedAttribute object."
                )

            return wrapper

        return outer
