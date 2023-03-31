# Core

## API

### Folder Structure

Dispatch's backend is a typical python web app. Its folder structure is a simple one and is mirrored between the backend code \(python\) and the frontend code \(javscript\).

```text
├── dispatch
│   ├── alembic
│   ├── application
│   ├── auth
│   ├── common
│   ├── conversation
│   ├── definition
...
```

Looking at the Dispatch folder structure, we try to group code by its subject. For example, all of the `definitions` code \(models, views, services\) is contained within the `definitions` folder.

### Starting the Development Server

For backend development, you will most likely want to use the `develop` command. This command starts a web server, creates a supervisor process to check for file changes, and reloads the server process when necessary.

```bash
> dispatch server develop --log-level debug
```

### Creating Models

During development, if you need to add or modify database models, there are a few things to consider:

- Is this a new model?
- Am I adding columns? Removing columns?
- Do I need to migrate any data?

Dispatch uses a combination of [SQLAlchemy](https://www.sqlalchemy.org/) models and [Alembic](https://alembic.sqlalchemy.org/en/latest/) to manage its database models.

#### Is this a new model?

When creating a new model, ensure that you are always inheriting from the `Base` Dispatch class \(`dispatch.database.Base`\). Check to see if your model requires any of the pre-existing mixins available to you in `dispatch.models` \(like `ResourceMixin` or `TimestampMixin`\).

For Alembic to see your new model, you must import the model at the bottom of the `dispatch.models` python module. This import ensures the model is available for Alembic introspection.

When you're ready, create a new migration for your model by running the following command:

```bash
> dispatch database revision --autogenerate
```

This command will generate an alembic file for you. The generated file will be automatically populated with several code pieces that enable everyday actions. If you need to migrate _data_ as part of your migration, you will have to write the data migration code yourself.

:::info
Alembic migrations are a _starting_ point and almost always need to be modified. Review the migration file before continuing.
:::

Once you're happy with the migration file, commit the modifications to the database:

```bash
> dispatch database upgrade
```

#### Am I adding columns? Am I Removing columns?

Similar to adding models, you will have to run a dispatch `revision` command to have Alembic create a new revision:

```bash
> dispatch database revision --autogenerate
```

Adding columns is relatively straightforward. It is encouraged that you do not add _and_ remove columns \(or tables\) within the same revision. Instead, it's better to add your new column on one revision and later remove/deprecate the old column once you are sure there is no code depending on that column.

#### Do I need to migrate any data?

Sometimes, a schema change necessitates some data migration. Migrating data can be a tricky operation, be careful to test this change several times \(ensuring backups are in place for worst-case scenarios\).

Alembic can help us with data migration; just like with the removal of columns, it's encouraged to create separate revisions for schema changes \(e.g., creating/deleting tables\) and modifying data itself. Staging these changes reduces the overall risk of the change.

```bash
> dispatch database revision
```

Creates a new empty revision, which you can then use to modify existing data if need be, as an example:

```python
connection = op.get_bind()
# Select all existing names that need migrating.
results = connection.execute(sa.select([
    t_users.c.id,
    t_users.c.name,
    ])).fetchall()
# Iterate over all selected data tuples.
for id_, name in results:
    # Split the existing name into first and last.
    firstname, lastname = name.rsplit(' ', 1)
    # Update the new columns.
    connection.execute(t_users.update().where(t_users.c.id == id_).values(
        lastname=lastname,
        firstname=firstname,
        ))
```

### Standards

For Dispatch's Python code base, all code style is controlled and enforced by [black](https://black.readthedocs.io/en/stable/). Additionally, we use various [flake8](https://flake8.pycqa.org/en/latest/) rules to ensure that our codebase is consistent. All settings are set in the `setup.cfg` located in the project's root directory and respected by tools locally.

When submitting a PR to Dispatch's GitHub project, code must have passing tests and no black or flake8 violations. PRs will not be evaluated if these checks are not met.

## UI

### Folder Structure

Similar to the API folder structure, we've chosen to group files based on the type of model they are related to:

```text
src
│   ├── API
│   ├── app
│   ├── application
│   ├── assets
│   ├── auth
│   ├── components
│   ├── dashboard
│   ├── definition
│   ├── document
...
```

### Starting the Development Server

From Dispatch's static directory:

```bash
> cd <path-to-static>/dispatch npm run serve
```

This command starts a local server, that again, like the API, will automatically reload itself when changes are detected. Additionally, this server acts as a proxy to the local API server, such that from the frontend's perspective, it is only talking to one server. This command helps avoid CORS-related issues and is closer to how the application is deployed \(static and API on the same hostname\).

### Standards

Similar to the Python API, we use a combination of [eslint](https://eslint.org/) and [prettier](https://prettier.io/) to give our code a consistent look and feel. We are not currently enforcing any of these checks on open PRs but plan to do so in the future.
