from typing import Any

from github import Github, GithubException
from github.ContentFile import ContentFile
from github.PullRequest import PullRequest
from github.Repository import Repository

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases.version_control import VesionControlPlugin

from ._version import __version__
from .config import GithubConfiguration


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class GithubVersionControlPlugin(VesionControlPlugin):
    title = "Github Plugin - Version Control"
    slug = "github-version-control"
    description = "Allows for interaction with Github Enterprise Server."
    version = __version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self) -> None:
        self.configuration_schema: type[GithubConfiguration] = GithubConfiguration
        self.github_client: Github | None = None

    def _initialize_client(self) -> None:
        if not self.github_client:
            token: str = self.configuration.pat.get_secret_value()
            base_url: str = str(self.configuration.base_url)
            self.github_client = Github(base_url=base_url, login_or_token=token)

    def get_repo(self, repo_name: str) -> Repository:
        """Get a repository object."""
        self._initialize_client()
        try:
            return self.github_client.get_repo(repo_name)
        except GithubException as e:
            raise Exception(f"Failed to get repository: {str(e)}") from e

    def get_file_content(self, repo_name: str, file_path: str, ref: str = "main") -> str:
        """Get the content of a file from a repository."""
        self._initialize_client()
        repo: Repository = self.get_repo(repo_name)

        try:
            content_file: ContentFile = repo.get_contents(file_path, ref=ref)
            return content_file.decoded_content.decode("utf-8")
        except GithubException as e:
            raise Exception(f"Failed to get file content: {str(e)}") from e

    def create_pr(
        self,
        repo_name: str,
        branch_name: str,
        base_branch: str,
        title: str,
        body: str,
        file_path: str,
        file_content: str,
    ) -> int:
        """Create a pull request with detection tuning changes."""
        self._initialize_client()
        repo: Repository = self.get_repo(repo_name)

        try:
            # Create a new branch
            source_branch = repo.get_branch(base_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_branch.commit.sha)

            # Create or update file in the new branch
            repo.create_file(
                path=file_path,
                message=f"Update detection rules: {title}",
                content=file_content,
                branch=branch_name,
            )

            # Create pull request
            pr: PullRequest = repo.create_pull(
                title=title, body=body, head=branch_name, base=base_branch
            )

            return pr.number

        except GithubException as e:
            raise Exception(f"Failed to create pull request: {str(e)}") from e

    def close_pr(self, repo_name: str, pr_number: int) -> bool:
        """Close a pull request."""
        self._initialize_client()
        repo: Repository = self.get_repo(repo_name)

        try:
            pr: PullRequest = repo.get_pull(pr_number)
            pr.edit(state="closed")
            return True
        except GithubException as e:
            raise Exception(f"Failed to close pull request: {str(e)}") from e

    def update_pr(
        self, repo_name: str, pr_number: int, file_path: str, file_content: str, commit_message: str
    ) -> bool:
        """Update an existing pull request with new changes."""
        self._initialize_client()
        repo: Repository = self.get_repo(repo_name)

        try:
            pr: PullRequest = repo.get_pull(pr_number)
            branch_name: str = pr.head.ref

            # Update file in the PR's branch
            contents: ContentFile = repo.get_contents(file_path, ref=branch_name)
            repo.update_file(
                path=file_path,
                message=commit_message,
                content=file_content,
                sha=contents.sha,
                branch=branch_name,
            )

            return True
        except GithubException as e:
            raise Exception(f"Failed to update pull request: {str(e)}") from e

    def get_pr_status(self, repo_name: str, pr_number: int) -> dict[str, Any]:
        """Get the status of a pull request."""
        self._initialize_client()
        repo: Repository = self.get_repo(repo_name)

        try:
            pr: PullRequest = repo.get_pull(pr_number)
            return {
                "state": pr.state,
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
            }
        except GithubException as e:
            raise Exception(f"Failed to get pull request status: {str(e)}") from e
