#!/usr/bin/env python
"""
Python script to generate releases notes using the GitHub CLI (gh).

Instructions on how to install gh can be found here: https://github.com/cli/cli#installation
"""
import click


@click.command()
@click.option(
    "--pull-request-number",
    "-n",
    required=True,
    type=int,
    help="Pull request number from where to generate the release notes.",
)
def release_notes(pull_request_number):
    """Simple utility function to assist with generating release notes."""
    import json
    import os

    dispatch_pr_url = "https://github.com/Netflix/dispatch/pull/"
    exclude_authors = ["dependabot"]
    gh_command = 'gh pr list -s merged --json "title,author,number,labels" -L 250'

    stream = os.popen(gh_command)
    pull_requests = json.loads(stream.read())

    sections = {
        "bug": "",
        "dependencies": "",
        "documentation": "",
        "enhancement": "",
        "feature": "",
        "tests": "",
    }

    for pull_request in pull_requests:
        author = pull_request["author"]["login"]
        title = pull_request["title"]
        number = pull_request["number"]

        if number < pull_request_number:
            break

        if author in exclude_authors:
            continue

        for label in pull_request["labels"]:
            sections[label["name"]] = (
                sections[label["name"]]
                + f"\n* {title} ([#{number}]({dispatch_pr_url}{number})) by @{author}"
            )

    print(
        f"""
Features:
    {sections["feature"]}

Enhancements:
    {sections["enhancement"]}

Bug Fixes:
    {sections["bug"]}

Tests:
    {sections["tests"]}

Documentation:
    {sections["documentation"]}
    """
    )


if __name__ == "__main__":
    release_notes()
