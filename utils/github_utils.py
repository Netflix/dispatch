#!/usr/bin/env python
"""
Utility Python script to automate GitHub-related actions.

Instructions on how to install gh can be found here: https://github.com/cli/cli#installation
"""
import json
import os
import click
from typing import NoReturn


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--label",
    "-l",
    required=True,
    type=str,
    help="Label used for filtering pull requests.",
)
def bulk_merge(label: str) -> NoReturn:
    """Utility function to assist with bulk merging pull requests."""
    gh_pr_list_command = f"gh pr list -s open -l {label} --json number"
    gh_pr_bulk_merge_command = "gh pr merge -s -d"

    stream = os.popen(gh_pr_list_command)
    pull_requests = json.loads(stream.read())

    for pull_request in pull_requests:
        stream = os.popen(f"{gh_pr_bulk_merge_command} {pull_request['number']}")


@cli.command()
@click.option(
    "--pull-request-number",
    "-n",
    required=True,
    type=int,
    help="Pull request number from where to generate draft release notes.",
)
def release_notes(pull_request_number: int) -> NoReturn:
    """Utility function to assist with generating release notes."""
    dispatch_pr_url = "https://github.com/Netflix/dispatch/pull/"
    exclude_bot_authors = True
    exclude_labels = ["skip-changelog", "UI/UX", "javascript"]
    gh_pr_list_merged_command = 'gh pr list -s merged --json "title,author,number,labels" -L 250'

    stream = os.popen(gh_pr_list_merged_command)
    pull_requests = json.loads(stream.read())

    sections = {
        "bug": "",
        "dependencies": "",
        "documentation": "",
        "enhancement": "",
        "feature": "",
        "techdebt": "",
        "tests": "",
    }

    for pull_request in pull_requests:
        author = pull_request["author"]["login"]
        is_bot_author = pull_request["author"]["is_bot"]
        title = pull_request["title"]
        number = pull_request["number"]

        if number < pull_request_number:
            break

        if exclude_bot_authors and is_bot_author:
            continue

        for label in pull_request["labels"]:
            label_name = label["name"]
            if label_name in exclude_labels:
                continue

            sections[label_name] = (
                sections[label_name]
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

Tech Debt:
    {sections["techdebt"]}

Tests:
    {sections["tests"]}

Documentation:
    {sections["documentation"]}
    """
    )


if __name__ == "__main__":
    cli()
