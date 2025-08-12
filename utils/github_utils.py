#!/usr/bin/env python
"""
Utility Python script to automate GitHub-related actions.

Instructions on how to install gh can be found here: https://github.com/cli/cli#installation
"""

import click
import json
import subprocess
from datetime import datetime
from time import sleep
from typing import Dict, List, NoReturn


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
    sections = {
        "bug": "",
        "dependencies": "",
        "documentation": "",
        "enhancement": "",
        "feature": "",
        "techdebt": "",
        "tests": "",
        "improvement": "",
        "docker": "",
        "security": "",
        "chore": "",
    }

    click.echo(f"Fetching list of merged PRs since #{pull_request_number}...")
    # Fetch only merged PRs for release notes
    gh_command = 'gh pr list -s merged --json "title,author,number,labels" -L 2000'
    pull_requests = json.loads(run_command(gh_command))

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

Dependencies:
    {sections["dependencies"]}

Docker:
    {sections["docker"]}

Security:
    {sections["security"]}

Tests:
    {sections["tests"]}

Documentation:
    {sections["documentation"]}
    """
    )


def fetch_pull_requests(repo: str = "Netflix/dispatch", limit: int = 2000) -> List[Dict]:
    """Fetch pull requests from repository using gh CLI."""
    gh_command = f'gh pr list --repo {repo} --state all --limit {limit} --json number,title,state,createdAt,author,url,headRefName,labels'
    output = run_command(gh_command)
    return json.loads(output)


def categorize_pull_requests(prs: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize pull requests by their type."""
    categories = {
        'Fixes': [],
        'Features': [],
        'Refactors': []
    }

    for pr in prs:
        title = pr['title']
        first_word = title.split('(')[0].split(':')[0].lower()

        if first_word in ['fix', 'fixes']:
            categories['Fixes'].append(pr)
        elif first_word in ['refactor', 'refactoring']:
            categories['Refactors'].append(pr)
        else:
            categories['Features'].append(pr)

    return categories


def clean_title(title: str) -> str:
    """Clean PR title by removing prefix and capitalizing."""
    if ':' in title:
        title = title.split(':', 1)[1].strip()
    return title[0].upper() + title[1:] if title else title


def format_deployment_prs(prs: List[Dict]) -> None:
    """Format and print pull requests for deployment announcements."""
    if not prs:
        print("No pull requests found")
        return

    today = datetime.now().strftime("%b %d")
    print(f":announcement-2549: *Dispatch deployment to production today* ({today}) at [TIME] PT. Expect brief downtime.")
    print()

    # Filter out chore PRs before categorizing
    non_chore_prs = []
    for pr in prs:
        title = pr['title']
        first_word = title.split('(')[0].split(':')[0].lower()
        if first_word not in ['chore', 'deps', 'deps-dev']:
            non_chore_prs.append(pr)

    categories = categorize_pull_requests(non_chore_prs)

    for category, pr_list in categories.items():
        if pr_list:
            print(f"*{category}*")
            for pr in pr_list:
                title = clean_title(pr['title'])
                print(f"• {title} ([#{pr['number']}]({pr['url']}))")
            print()


@cli.command()
@click.option(
    "--pr-number",
    "-n",
    required=True,
    type=int,
    help="PR number to start from (inclusive)"
)
@click.option(
    "--repo",
    default="Netflix/dispatch",
    help="Repository in format owner/repo (default: Netflix/dispatch)"
)
def deployment_notes(pr_number: int, repo: str) -> NoReturn:
    """Generate deployment notes for PRs starting from a specified PR number."""
    try:
        # Fetch all PRs
        prs = fetch_pull_requests(repo, limit=100)

        # Filter PRs with number >= pr_number
        filtered_prs = [pr for pr in prs if pr["number"] >= pr_number]

        # Sort by PR number (descending)
        filtered_prs.sort(key=lambda x: x["number"], reverse=True)

        format_deployment_prs(filtered_prs)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
