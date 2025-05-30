#GitSleuth_API
import base64
import logging
import os
import time
import requests
from OAuth_Manager import oauth_login
from Token_Manager import load_tokens


# Constants for GitHub API
GITHUB_API_URL = 'https://api.github.com/'
class RateLimitException(Exception):
    def __init__(self, message, wait_time=None):
        super().__init__(message)
        self.wait_time = wait_time



def handle_api_response(response):
    """
    Handles the API response, checking for errors, logging, and returning the response JSON.
    Logs the full response for debugging purposes.

    Parameters:
    - response (requests.Response): The response object from the API request.

    Returns:
    - dict or None: Parsed JSON data from the response, or None if an error occurred.
    """

    # Log the full response for debugging
    try:
        response_json = response.json()
        logging.debug(f"API Response: {response_json}")  # Log the full JSON response
    except ValueError:
        logging.error(f"Invalid JSON in response: {response.text}")
        return None

    if response.status_code == 200:
        return response_json
    elif response.status_code in (403, 429) and (
        'rate limit' in response.text.lower()
        or 'Retry-After' in response.headers
    ):
        reset = response.headers.get('X-RateLimit-Reset')
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            wait_time = int(retry_after)
        else:
            wait_time = max(int(reset) - int(time.time()), 0) if reset else None
        raise RateLimitException("GitHub API rate limit reached", wait_time)
    else:
        logging.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None


def fetch_paginated_data(url, headers, max_items=100):
    items = []
    while url and len(items) < max_items:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_data = response.json()
            items.extend(page_data)
            url = response.links.get('next', {}).get('url', None)
        else:
            logging.error(f"Failed to fetch paginated data: {response.text}")
            break
    return items[:max_items]


_OAUTH_TOKEN = None


def _choose_token(tokens: dict) -> str | None:
    """Return the preferred token from stored tokens."""
    if "oauth_token" in tokens:
        return tokens["oauth_token"]
    if tokens:
        # Use first token in dictionary order
        return list(tokens.values())[0]
    return None


def get_headers():
    """Generate headers for GitHub API requests."""

    global _OAUTH_TOKEN
    if not _OAUTH_TOKEN:
        _OAUTH_TOKEN = os.environ.get("GITHUB_OAUTH_TOKEN")
        if not _OAUTH_TOKEN:
            tokens = load_tokens()
            _OAUTH_TOKEN = _choose_token(tokens)

        if not _OAUTH_TOKEN:
            result = oauth_login()
            _OAUTH_TOKEN = result[0] if isinstance(result, tuple) else result

        if not _OAUTH_TOKEN:
            logging.error("No GitHub tokens available.")
            return {}

        os.environ["GITHUB_OAUTH_TOKEN"] = _OAUTH_TOKEN

    logging.debug("Using OAuth token")
    return {
        "Authorization": f"token {_OAUTH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",

    }

    
def get_repo_info(repo_name, headers):
    """
    Fetches basic information of a specific GitHub repository.

    Parameters:
    - repo_name (str): The full name of the repository (username/repo).
    - headers (dict): Headers to be used for the GitHub API request.

    Returns:
    - dict: Repository information if successful, None otherwise.
    """
    repo_url = f'{GITHUB_API_URL}repos/{repo_name}'
    response = requests.get(repo_url, headers=headers)
    return handle_api_response(response)

def get_commit_history(repo_name, headers, max_commits=100):
    """
    Fetches the commit history of a specific GitHub repository with pagination support.

    Parameters:
    - repo_name (str): The full name of the repository (username/repo).
    - headers (dict): Headers to be used for the GitHub API request.
    - max_commits (int): Maximum number of commits to return.

    Returns:
    - list: List of commits if successful, None otherwise.
    """
    commits_url = f'{GITHUB_API_URL}repos/{repo_name}/commits'
    return fetch_paginated_data(commits_url, headers, max_commits)

def search_github_for_repos(query, headers, max_repos=100):
    """
    Searches GitHub for repositories based on a query with pagination support.

    Parameters:
    - query (str): The search query.
    - headers (dict): Headers to be used for the GitHub API request.
    - max_repos (int): Maximum number of repositories to return.

    Returns:
    - list: A list of repository names that match the query.
    """
    search_url = f"{GITHUB_API_URL}search/repositories?q={query}&sort=updated&order=desc"
    return fetch_paginated_data(search_url, headers, max_repos)
def get_file_contents(repo_name, file_path, headers):
    """
    Fetches the content of a specific file in a repository.

    Parameters:
    - repo_name (str): Full name of the repository (username/repo).
    - file_path (str): Path to the file in the repository.
    - headers (dict): Headers for the GitHub API request.

    Returns:
    - str: Content of the file, or None if an error occurs.
    """
    file_url = f"{GITHUB_API_URL}repos/{repo_name}/contents/{file_path}"
    response = requests.get(file_url, headers=headers)
    file_data = handle_api_response(response)
    if file_data and 'content' in file_data:
        return base64.b64decode(file_data['content']).decode('utf-8')
    else:
        return None

def search_files_in_repo(repo_name, query, headers):
    """
    Searches files in a specific repository based on a query.
    
    Parameters:
    - repo_name (str): The full name of the repository (username/repo).
    - query (str): The search query for files.
    - headers (dict): Headers for the GitHub API request.
    
    Returns:
    - list: List of files matching the query.
    """
    search_url = f"{GITHUB_API_URL}search/code?q=repo:{repo_name}+{query}"
    response = requests.get(search_url, headers=headers)
    return handle_api_response(response)

def get_readme_contents(repo_name, headers):
    """
    Fetches the README content of a specific GitHub repository.

    Parameters:
    - repo_name (str): The full name of the repository (username/repo).
    - headers (dict): Headers to be used for the GitHub API request.

    Returns:
    - str: README content if successful, None otherwise.
    """
    readme_url = f'{GITHUB_API_URL}repos/{repo_name}/readme'
    response = requests.get(readme_url, headers=headers)
    readme_data = handle_api_response(response)
    if readme_data:
        return base64.b64decode(readme_data['content']).decode('utf-8')
    else:
        return None

def search_github_code(query, headers):
    """
    Searches for code snippets on GitHub based on a query.

    Parameters:
    - query (str): The search query.
    - headers (dict): Headers for the GitHub API request.

    Returns:
    - list: A list of code search results.
    """
    search_url = f"{GITHUB_API_URL}search/code?q={query}&per_page=100"
    response = requests.get(search_url, headers=headers)
    return handle_api_response(response)

def check_rate_limit(headers):
    """Return remaining search requests and wait time until reset."""
    rate_limit_url = f"{GITHUB_API_URL}rate_limit"
    response = requests.get(rate_limit_url, headers=headers)
    rate_limit_data = handle_api_response(response)
    if rate_limit_data:
        search_limit = rate_limit_data['resources']['search']
        remaining = search_limit['remaining']
        reset = search_limit.get('reset')
        wait_time = max(int(reset) - int(time.time()), 0) if reset else None
        logging.debug(
            f"Search API rate limit remaining: {remaining}, resets in {wait_time}s"
        )
        return remaining, wait_time
    return 0, None

