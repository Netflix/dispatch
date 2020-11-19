---
description: >-
  Want to contribute back to Dispatch? These pages describe the general
  development flow, our philosophy, the test suite, and issue tracking.
---

# Contributing

## Documentation

Dispatch documentation is managed via Gitbook.

## Doing a release

Creating a release of Dispatch requires the following steps.

### Updating sample data

If the database schema changes we will need to update the sample data accordingly.

- Run the Bash script `update-example-data.sh` in the `data` directory.
- Create a commit with any changes
- Create a pull request with the change
- Merge change

### Bumping the version number

- Update the version number in `dispatch/__about__.py`
- Create a new entry in the change log
- Create a commit with the change log changes
- Create a pull request with the change
- Merge change

### Change log

- Create a new change log with all major changes since the last release
- Update github releases: https://github.com/Netflix/dispatch/releases
- Publish the release

### Update 'latest' tag

We rely on the latest tag to identify the most current stable version. Follow the steps below to update this tag:

Delete the pervious tag:

```
git tag -d latest
```

Create a new tag:

```
git tag -a latest <commit>
```

Push the tag:

```
git push origin latest
```
