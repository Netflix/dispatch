# FAQ

## Running ‘dispatch database upgrade’ seems stuck.

The upgrade is most likely stuck because an existing query on the database is holding onto a lock that the migration needs.

To resolve, login to your dispatch database and run:

> SELECT \* FROM pg_locks l INNER JOIN pg_stat_activity s ON \(l.pid = s.pid\) WHERE waiting AND NOT granted;

The result of this query will give you a list of queries that are currently waiting to be executed. From there, attempt to identify the PID of the query blocking the migration. Once found, execute:

> select pg_terminate_backend\(&lt;blocking-pid&gt;\);

See [http://stackoverflow.com/questions/22896496/alembic-migration-stuck-with-postgresql](http://stackoverflow.com/questions/22896496/alembic-migration-stuck-with-postgresql) for more.
