#GitSleuth_API
import requests
import base64
import logging

# Constants for GitHub API
GITHUB_API_URL = 'https://api.github.com/'
class RateLimitException(Exception):
    pass

def handle_api_response(response):
    """
    Handles the API response, checking for errors and logging appropriately.
    ... [existing documentation] ...
    """
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403 and 'rate limit' in response.text.lower():
        raise RateLimitException("GitHub API rate limit reached")
    else:
        logging.error(f"API request failed with status code {response.status_code}: {response.json()}")
        return None

def fetch_paginated_data(url, headers, max_items=100):
    """
    Fetches data from a paginated API endpoint.

    Parameters:
    - url (str): The API endpoint URL.
    - headers (dict): Headers for the GitHub API request.
    - max_items (int): Maximum number of items to fetch.

    Returns:
    - list: Aggregated data from all pages.
    """
    items = []
    while url and len(items) < max_items:
        response = requests.get(url, headers=headers)
        page_data = handle_api_response(response)
        if page_data:
            items.extend(page_data)
            url = response.links.get('next', {}).get('url', None)
        else:
            break
    return items[:max_items]

def get_headers(config):
    """
    Generates headers for GitHub API requests using the current token.

    Parameters:
    - config (dict): Configuration data including the GitHub tokens.

    Returns:
    - dict: Headers with the current GitHub token.
    """
    return {'Authorization': f'token {config["GITHUB_TOKENS"][0]}'}

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
    search_url = f"{GITHUB_API_URL}search/code?q={query}"
    response = requests.get(search_url, headers=headers)
    return handle_api_response(response)

def check_rate_limit(headers):
    """
    Checks the current rate limit for the GitHub API.

    Parameters:
    - headers (dict): Headers for the GitHub API request.

    Returns:
    - int: The number of requests remaining before hitting the rate limit.
    """
    rate_limit_url = f"{GITHUB_API_URL}rate_limit"
    response = requests.get(rate_limit_url, headers=headers)
    rate_limit_data = handle_api_response(response)
    if rate_limit_data:
        remaining = rate_limit_data['resources']['search']['remaining']
        logging.debug(f"Search API rate limit remaining: {remaining}")
        return remaining
    else:
        return 0