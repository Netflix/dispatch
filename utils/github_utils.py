#!/usr/bin/env python
"""
Utility Python script to automate GitHub-related actions.

Instructions on how to install gh can be found here: https://github.com/cli/cli#installation
"""
import click
import json
import subprocess
from time import sleep
from typing import NoReturn


@click.group()
def cli():
    pass


def run_command(command: str) -> str:
    """Utility function to run commands."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    return output.decode("utf-8")


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
    gh_pr_list_command = f"gh pr list -s open -l {label} --json title,number"
    gh_pr_bulk_merge_command = "gh pr merge -s -d --admin"

    click.echo(f"Fetching open PRs with {label} label...")
    pull_requests = json.loads(run_command(gh_pr_list_command))

    if not pull_requests:
        click.echo(f"No open PRs with {label} label found.")
        return

    for pull_request in pull_requests:
        number = pull_request["number"]
        title = pull_request["title"]
        click.echo(f"Merging PR #{number} {title}...")
        run_command(f"{gh_pr_bulk_merge_command} {number}")
        sleep(
            5
        )  # NOTE: Needed to avoid error "Base branch was modified. Review and try the merge again"

    click.echo(f"Open PRs with {label} label merged.")


def is_excluded_label(label: str, exclude_labels: list) -> bool:
    """Checks if label is in the excluded labels list."""
    return label["name"] in exclude_labels


def is_excluded_author(pull_request: dict, exclude_bot_authors: bool) -> bool:
    """Checks if author is a bot."""
    return exclude_bot_authors and pull_request["author"]["is_bot"]


def update_section(
    pull_request: dict, sections: dict, label_name: str, dispatch_pr_url: str
) -> NoReturn:
    """Updates release notes section."""
    title = pull_request["title"]
    number = pull_request["number"]
    author = pull_request["author"]["login"]
    sections[label_name] += f"\n* {title} ([#{number}]({dispatch_pr_url}{number})) by @{author}"


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
    gh_pr_list_merged_command = 'gh pr list -s merged --json "title,author,number,labels" -L 2000'
    sections = {
        "bug": "",
        "dependencies": "",
        "documentation": "",
        "enhancement": "",
        "feature": "",
        "techdebt": "",
        "tests": "",
        "improvement": "",
    }

    click.echo(f"Fetching list of merged PRs since #{pull_request_number}...")
    pull_requests = json.loads(run_command(gh_pr_list_merged_command))

    if not pull_requests:
        click.echo(f"No PRs merged since #{pull_request_number}.")

    for pull_request in pull_requests:
        number = pull_request["number"]

        if number < pull_request_number:
            break

        if is_excluded_author(pull_request, exclude_bot_authors):
            continue

        for label in pull_request["labels"]:
            if is_excluded_label(label, exclude_labels):
                continue

            update_section(pull_request, sections, label["name"], dispatch_pr_url)

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
