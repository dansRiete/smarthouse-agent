import os
from github import Github
from langchain.tools import tool

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "dansRiete/smarthouse-controller"

@tool
def read_github_file(file_path: str) -> str:
    """Useful to read a file from the main branch of the smarthouse-controller github repository."""
    if not GITHUB_TOKEN:
        return "Error: GITHUB_TOKEN environment variable not set."
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(file_path, ref="master")
        return file_content.decoded_content.decode("utf-8")
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@tool
def create_pull_request(branch_name: str, file_path: str, new_content: str, commit_msg: str, pr_title: str, pr_body: str) -> str:
    """Useful to update a file and create a Pull Request. Requires branch_name, file_path, new_content, commit_msg, pr_title, pr_body."""
    if not GITHUB_TOKEN:
        return "Error: GITHUB_TOKEN environment variable not set."
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        
        # Get master branch sha
        master_ref = repo.get_git_ref("heads/master")
        # Create new branch
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=master_ref.object.sha)
        
        # Get existing file to get its sha
        contents = repo.get_contents(file_path, ref="master")
        
        # Update the file on the new branch
        repo.update_file(contents.path, commit_msg, new_content, contents.sha, branch=branch_name)
        
        # Create PR
        pr = repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base="master")
        return f"Successfully created Pull Request: {pr.html_url}"
    except Exception as e:
        return f"Error creating PR: {str(e)}"
