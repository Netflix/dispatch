# Core

## API

### Folder Structure

Dispatch's backend is a fairly typical python web app. It's folder structure is a simply one and is mostly mirrored between the backend code \(python\) and the frontend code \(javscript\).

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

Looking at the Dispatch folder structure, we typically try to group code by its it subject, meaning for `definitions` all if its code \(models, views, services\) are contained within the `definitions` folder. 

### Starting the Development Server

For backend development you will most likely want to use the `develop` command. This command starts a webserver creates a supervisor process to check for file changes, reloading the server process when necessary.

```bash
> dispatch server develop --log-level debug
```

### Creating Models

If during development, you need to add or modify database models there are a few things to consider:

* Is this a new model?
* Am I adding columns? Removing columns?
* Do I need to migrate any data?

Dispatch uses a combination of [SQLAlchemy](https://www.sqlalchemy.org/) models and [Alembic](https://alembic.sqlalchemy.org/en/latest/) to manage it's database models. 

#### Is this a new model?

We creating a new model, ensure the you are always inheriting from the `Base` Dispatch class \(`dispatch.database.Base`\). Also check to see if you're model requires any of the pre-existing mixins available to you in `dispatch.models` \(like `ResourceMixin` or `TimestampMixin`\). 

In order for Alembic to see you're new model ensure that you import it at the bottom of `dispatch.models`. This import ensures the model is available for Alembic introspection. 

When you're ready, create a new migration for your model by running the following command:

```bash
> dispatch database revision --autogenerate
```

This will generate an alembic file for you, populating it with several pieces of code that allows use to modify the existing database schema, adding your new model. 

{% hint style="info" %}
Alembic migrations are a _starting_ point, and almost always need to be modified. Review the migration file before continuing.
{% endhint %}

Once you're happy with the migration file commit the modifications to the database:

```bash
> dispatch database upgrade
```

#### Am I adding columns? Removing columns?

Similar to adding models, you will have to run a dispatch `revision` command to have Alembic create a new revision:

```bash
> dispatch database revision --autogenerate
```

Adding columns is relatively straightforward, however it is **highly** encouraged that you do not both add and remove columns \(or tables\) within the same revision. Instead it's better to add your new column on one revision and later remove/deprecate the old column, once you are sure there is no code depending on that column. 

#### Do I need to migrate any data?

Sometimes, a schema change necessitates some sort of data migration. This can be a tricky operation, be careful to test this change several times \(ensuring backups are in place for worst case scenarios\). 

Again alembic can help us here and it's **highly** encouraged to create separate revisions for schema changes \(e.g. creating/deleting tables\) and modifying data itself. Staging these changes reduces the overall risk of the change. 

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

For Dispatch's Python code base, all code style is controlled and enforced by [black](https://black.readthedocs.io/en/stable/). Additionally, we use various [flake8](https://flake8.pycqa.org/en/latest/) rules to ensure that our code base is kept in a consistent manner. All settings are set in the `setup.cfg` located in the project's root directory and should be respected by tools locally. 

When submitting a PR to Dispatch's github project, code has to have passing tests and no black or flake8 violations. PRs will not be evaluated if these checks are not met. 

## UI

### Folder Structure

Similar to the API folder structure we've choose to group files based on the type of model they are related to:

```text
src
│   ├── api
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

This starts a local server, that again like the API will automatically reload itself when changes are detected. Additionally, this server acts as a proxy to the local API server such that from the frontends perspective it is only talk to one server. This is especially helpful as it avoids CORS related issues and is closer to how the application is deployed \(static and api on the same hostname\). 

### Standards

Similar to the Python API we use a combination of [eslint](https://eslint.org/) and [prettier](https://prettier.io/) to give our code a consistent look and feel. We are not currently enforcing any of these checks on open PRs but plan to do so in the future. 

