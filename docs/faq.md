# FAQ

## Running ‘dispatch database upgrade’ seems stuck.

Most likely, the upgrade is stuck because an existing query on the database is holding onto a lock that the migration needs.

To resolve, login to your lemur database and run:

> SELECT \* FROM pg\_locks l INNER JOIN pg\_stat\_activity s ON \(l.pid = s.pid\) WHERE waiting AND NOT granted;

This will give you a list of queries that are currently waiting to be executed. From there attempt to idenity the PID of the query blocking the migration. Once found execute:

> select pg\_terminate\_backend\(&lt;blocking-pid&gt;\);

See [http://stackoverflow.com/questions/22896496/alembic-migration-stuck-with-postgresql](http://stackoverflow.com/questions/22896496/alembic-migration-stuck-with-postgresql) for more.

