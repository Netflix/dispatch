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
    gh_command = 'gh pr list -s closed --json "title,author,number" -L 250'

    stream = os.popen(gh_command)
    pull_requests = json.loads(stream.read())

    for pull_request in pull_requests:
        author = pull_request["author"]["login"]
        title = pull_request["title"]
        number = pull_request["number"]

        if number < pull_request_number:
            break

        if author in exclude_authors:
            continue

        print(f"* {title} by @{author} ([#{number}]({dispatch_pr_url}{number}))")


if __name__ == "__main__":
    release_notes()
