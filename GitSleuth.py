#GitSleuth.py
import os
import time
import pandas as pd
import json
import logging
import re
from GitSleuth_Groups import (
    create_search_queries,
    get_query_description,
    is_placeholder_snippet,
)
from GitSleuth_API import get_file_contents, search_github_code, check_rate_limit, get_headers
from OAuth_Manager import oauth_login

import GitSleuth_API
import platform
import sys
from datetime import datetime
import requests
from prettytable import PrettyTable
from colorama import Fore, Style
from GitSleuth_API import RateLimitException
from Token_Manager import load_tokens, switch_token as rotate_token
from Secret_Scanner import snippet_has_secret
import math




# Configuration file for storing the API tokens and settings
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from ``config.json`` and available GitHub tokens."""
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        config = {}

    logging.debug("Config loaded")
    return config

def oauth_login_flow():
    """Obtain an OAuth token and store it for API requests."""
    token = oauth_login()
    if token:
        os.environ["GITHUB_OAUTH_TOKEN"] = token
        print("OAuth login successful.")
    else:
        print("OAuth login failed.")

def process_search_item(item, query, headers, all_data, filter_placeholders=True):
    """
    Processes a single item from GitHub search results.

    Parameters:
    - item (dict): The item from search results.
    - query (str): The query used for the search.
    - headers (dict): The headers used for API requests.
    - all_data (list): A list to store the processed data.
    - filter_placeholders (bool): Whether to ignore placeholder snippets.

    This function extracts relevant information from the item, such as repository name,
    file path, and file contents. It then extracts snippets from the contents based
    on the search query and adds this data to 'all_data'.
    """
    repo_name = item['repository']['full_name']
    file_path = item.get('path', '')
    
    # Fetching file contents
    file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
    
    if file_contents:
        # Extracting snippets based on the query
        cfg = load_config()
        placeholders = cfg.get("FILTER_PLACEHOLDERS", True)
        allowlist = cfg.get("ALLOWLIST_PATTERNS", [])
        snippets = extract_snippets(
            file_contents,
            query,
            filter_placeholders=placeholders,
            allowlist_patterns=allowlist,
        )
        logging.info(f"Processed {len(snippets)} snippets from {repo_name}/{file_path}")

        # Adding data to all_data list
        item_data = {
            'repository': repo_name,
            'file_path': file_path,
            'snippets': snippets
        }
        all_data.append(item_data)
    else:
        logging.info(f"No content found for file: {repo_name}/{file_path}")

def process_query(query, max_retries, config, search_timeout, start_time):
    """
    Processes each query, handling retries, rate limit exceptions, and timeouts.
    Returns True if new results were found, False otherwise.

    Parameters:
    - query (str): The search query to be processed.
    - max_retries (int): Maximum number of retries for the query.
    - config (dict): Configuration settings including GitHub tokens.
    - search_timeout (int): Maximum time (in seconds) to spend on a search query.
    - start_time (float): The start time of the search process.

    Returns:
    - bool: True if new results were found for the query, False otherwise.

    This function performs a GitHub code search for the given query and handles
    any exceptions related to rate limits. It retries the query if rate limits
    are hit and rotates the GitHub token if available.
    """
    retry_count = 0
    new_result_found = False
    while retry_count < max_retries and time.time() - start_time < search_timeout:
        try:
            headers = GitSleuth_API.get_headers()
            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                new_result_found = True  # New results were found
                # Handle search results here
                # (You can process and log the results as needed)
            break
        except RateLimitException as e:
            logging.warning(str(e))
            if not switch_token(config):
                wait_time = getattr(e, 'wait_time', 60)
                logging.info(f"Waiting {int(wait_time)} seconds for rate limit reset.")
                time.sleep(wait_time)

            retry_count += 1
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")
            break

    if time.time() - start_time >= search_timeout:
        logging.warning("Search timeout reached, stopping search.")

    return new_result_found


def perform_search(domain, selected_group, config, max_retries=3, search_timeout=300):
    """
    Performs the search operation, managing rate limits and token switching.

    Parameters:
    - domain (str): The domain for the search.
    - selected_group (str): The selected search group.
    - config (dict): Configuration with GitHub tokens.
    - max_retries (int): Max retries for search queries.
    - search_timeout (int): Search operation timeout.
    """

    start_time = time.time()  # Start time of the search
    last_result_time = start_time  # Last result found time

    filter_placeholders = config.get("FILTER_PLACEHOLDERS", True)
    search_groups = create_search_queries(domain, filter_placeholders=filter_placeholders)

    for group in (search_groups if selected_group == "Search All" else [selected_group]):
        for query in search_groups.get(group, []):
            if time.time() - start_time >= search_timeout:
                logging.warning("Search timeout reached.")
                return

            retry_count = 0
            while retry_count < max_retries:
                try:
                    search_results = process_query(query, max_retries, config, search_timeout, start_time)
                    if search_results:
                        last_result_time = time.time()  # Update last result time
                        # Process the search results as required
                    break

                except RateLimitException as e:
                    logging.warning("Rate limit reached, attempting to switch token.")
                    if switch_token(config):
                        retry_count += 1
                    else:
                        wait_time = getattr(e, 'wait_time', 60)
                        logging.info(f"Waiting {int(wait_time)} seconds for rate limit reset.")
                        time.sleep(wait_time)

                except RateLimitException:
                    logging.warning("Rate limit reached.")
                    retry_count += 1

                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    break

            if time.time() - last_result_time >= 60:
                logging.warning("No results found in the last 60 seconds.")
                break

    logging.info("Search completed for the selected group.")




def get_domain_input():
    """
    Prompts the user to enter their organization's domain for search.
    
    Returns:
    str: The entered domain.
    """
    return input("Enter your organization's domain for search (e.g., 'google.com'): ")

def truncate_snippet(snippet, length=200):
    """
    Truncates a snippet to a specified maximum length.

    Parameters:
    - snippet (str): The text snippet to be truncated.
    - length (int): The maximum length of the truncated snippet.

    Returns:
    - str: The truncated snippet with an ellipsis if it exceeds the specified length.
    """
    return (snippet[:length] + '...') if len(snippet) > length else snippet

def highlight_search_term(snippet, search_term, color=Fore.RED):
    """
    Highlights the search term within a snippet.

    Parameters:
    - snippet (str): The text snippet where the search term is to be highlighted.
    - search_term (str): The term within the snippet to highlight.
    - description (str): Description of the query.
    - color (colorama.Fore): The color to use for highlighting the search term.

    Returns:
    - str: The snippet with the search term highlighted.
    """
    return snippet.replace(search_term, color + search_term + Style.RESET_ALL)
# GitSleuth.py

def perform_api_request_with_token_rotation(query, config, max_retries=3):
    """
    Performs a GitHub API request with token rotation in case of rate limiting.

    Parameters:
    - query (str): The search query for the GitHub API.
    - config (dict): The configuration dictionary with GitHub tokens.
    - max_retries (int): Maximum number of retries for the request in case of rate limit.

    Returns:
    - dict or None: The API response, or None if unsuccessful after retries.
    """
    retry_count = 0
    while retry_count < max_retries:
        headers = GitSleuth_API.get_headers()
        try:
            search_results = GitSleuth_API.search_github_code(query, headers)
            if 'items' in search_results:
                return search_results
            else:
                logging.info(f"No results found for query: {query}")
                return None
        except RateLimitException as e:
            logging.warning(str(e))

            if retry_count < max_retries - 1 and switch_token(config):
                retry_count += 1
            else:
                wait_time = getattr(e, 'wait_time', 60)
                logging.info(f"Waiting {int(wait_time)} seconds for rate limit reset.")
                time.sleep(wait_time)
                retry_count += 1
            retry_count += 1


    logging.error("Max retries reached. Unable to complete the API request.")
    return None

def process_and_display_data(data, search_term, description=""):
    """
    Formats and displays the search result data in a tabular format.

    This function constructs a table using PrettyTable to display each piece of data, 
    including the repository name, file path, search term, and found snippets. 
    Snippets are truncated for readability and the search term within them is highlighted.

    Parameters:
    - data (dict): Data of a single repository.
    - search_term (str): The search term used in the GitHub search.
    - description (str): Description of the query.
    """
    table = PrettyTable()
    table.field_names = [Fore.BLUE + "Attribute" + Style.RESET_ALL, Fore.BLUE + "Value" + Style.RESET_ALL]
    table.align = "l"
    if description:
        table.add_row(["description", description])

    for key, value in data.items():
        if key == 'snippets':
            highlighted_snippets = [highlight_search_term(truncate_snippet(snippet), search_term) for snippet in value]
            snippets_text = '\n'.join(highlighted_snippets)
            table.add_row([key, snippets_text])
        else:
            table.add_row([key, value])

    print(table)

def process_search_results(search_results, all_data, query, headers, group_name, ignored_filenames, domain, filter_placeholders=True):
    """
    Processes search results, extracting file contents and snippets.

    Iterates over search results, handles API requests for file contents,
    and extracts relevant snippets. Appends processed data to a list.

    Parameters:
    - search_results (dict): The search results from the GitHub API.
    - all_data (list): The list to append processed data to.
    - query (str): The search query used.
    - domain (str): Domain used in the query.
    - headers (dict): Headers for GitHub API requests.
    - group_name (str): The name of the search group.
    - ignored_filenames (list): List of filenames to ignore in the search.
    - filter_placeholders (bool): Whether to ignore placeholder snippets.
    """
    description = get_query_description(query, domain)
    config = load_config()
    ignored_patterns = config.get("IGNORED_PATH_PATTERNS", [])
    for item in search_results['items']:
        file_path = item.get('path', '')
        if file_path in ignored_filenames or _path_is_ignored(file_path, ignored_patterns):
            continue
        repo_name = item['repository']['full_name']
        try:
            file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
            if file_contents:
                allowlist = config.get("ALLOWLIST_PATTERNS", [])
                snippets = extract_snippets(
                    file_contents,
                    query,
                    filter_placeholders=filter_placeholders,
                    allowlist_patterns=allowlist,
                )
                if snippets:
                    file_data = {
                        'repo': repo_name,
                        'file_path': file_path,
                        'snippets': snippets,
                        'search_term': query,
                        'group': group_name,
                        'description': description,
                    }
                    all_data.append(file_data)
                    process_and_display_data(file_data, query, description)  # Pass query as search_term
                else:
                    logging.info(f"No relevant snippets found in {file_path} for query '{query}'")
            else:
                logging.info(f"No file contents found for {file_path}")
        except requests.RequestException as e:
            logging.error(f"Failed to fetch file contents: {e}")

def initialize_logging():
    """
    Initializes the logging system based on settings from the configuration file.

    Reads the logging level from the configuration file and sets the logging level accordingly.
    If no configuration is found, defaults to INFO level.
    """
    config = load_config()
    log_level = config.get('LOG_LEVEL', 'ERROR').upper()
    logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(levelname)s - %(message)s')

def save_config(config):
    """
    Saves the configuration to the config file.

    Attempts to write the provided configuration dictionary to the config file in JSON format.
    Logs an error if the operation fails.

    Parameters:
    config (dict): Configuration data including the GitHub tokens.
    """
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file)
    except IOError as e:
        logging.error(f"Error saving configuration to file: {e}")


def authenticate_via_oauth():
    """Obtain a GitHub access token using OAuth device flow."""
    oauth_login()

def clear_screen():
    """
    Clears the terminal screen for a cleaner user experience.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def get_headers(config):
    """
    Retrieves the headers for GitHub API requests with the current token.

    Parameters:
    - config (dict): Configuration data including the GitHub tokens.

    Returns:
    - dict: Headers with the current GitHub token, or an empty dict if no valid token is found.
    """
    if 'GITHUB_TOKENS' in config and config['GITHUB_TOKENS']:
        token = config['GITHUB_TOKENS'][0]  # Using the first token in the list
        logging.debug(f"Using GitHub token: {token[:4]}****")
        return {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    else:
        logging.error("No GitHub tokens are set. Check the configuration.")
        return {}



def set_github_token():
    """Interactively add new GitHub tokens."""
    while True:
        name = input("Token name (or press Enter to finish): ").strip()
        if not name:
            break
        value = input("Token value: ").strip()
        if value:
            add_token(name, value)
            print(f"Token '{name}' added.")


def delete_github_token():
    """Remove a stored GitHub token."""
    tokens = load_tokens()
    if not tokens:
        print("No tokens stored.")
        return
    for idx, name in enumerate(tokens, start=1):
        print(f"{idx}. {name}")
    choice = input("Select a token number to delete: ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(tokens):
            delete_token(list(tokens.keys())[idx])
            print("Token deleted.")


def view_github_token():
    """Display stored token names."""
    tokens = load_tokens()
    if tokens:
        print("Stored tokens:", ", ".join(tokens.keys()))
    else:
        print("No tokens stored.")


def switch_token(config=None):
    """Rotate the current OAuth token using saved tokens."""
    return rotate_token(config)




def extract_search_terms(query):
    """Return the list of search terms contained in a query string.

    The GitHub search queries contain qualifiers such as ``filename:`` or
    logical operators like ``NOT``. This helper parses the query and extracts
    only the terms that are expected to be present in the file contents so that
    snippets can be validated against the rule that triggered the hit.
    """

    tokens = re.findall(r'"[^"]+"|\S+', query)
    search_terms = []
    skip_next = False

    qualifiers = {
        'filename', 'path', 'repo', 'org', 'extension', 'language', 'type'
    }

    for token in tokens:
        if skip_next:
            skip_next = False
            continue

        clean = token.strip('"')

        upper = clean.upper()
        if upper in {'AND', 'OR'}:
            continue
        if upper == 'NOT':
            skip_next = True
            continue

        if ':' in clean:
            qualifier = clean.split(':', 1)[0]
            if qualifier in qualifiers:
                continue

        search_terms.append(clean)

    return search_terms


PLACEHOLDER_VALUES = {
    "",
    "null",
    "None",
    "none",
    "placeholder",
    "example",
    "sample",
    "test",
}

# Default entropy threshold to determine whether a value looks random enough
# to be considered a real secret.
DEFAULT_ENTROPY_THRESHOLD = 3.5

# Inline pragma used by detect-secrets to suppress findings
ALLOWLIST_PRAGMA_RE = re.compile(r"#\s*pragma:\s*allowlist secret", re.I)

ENV_ASSIGN_RE = re.compile(r"\b([A-Z0-9_]+)=\s*(\S*)")


def _shannon_entropy(data: str) -> float:
    """Return the Shannon entropy of *data* in bits per character."""
    if not data:
        return 0.0
    freq = {}
    for ch in data:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def _has_allowlist_comment(content: str, start: int, end: int) -> bool:
    """Return True if an allowlist pragma appears near the snippet."""
    context_start = max(0, start - 100)
    context_end = min(len(content), end + 100)
    return bool(ALLOWLIST_PRAGMA_RE.search(content[context_start:context_end]))


def _path_is_ignored(file_path: str, patterns: list[str]) -> bool:
    """Return True if file_path matches any ignore pattern."""
    return any(re.search(p, file_path) for p in patterns)


def _is_placeholder_snippet(snippet, query_terms=None, entropy_threshold=DEFAULT_ENTROPY_THRESHOLD):
    """Return True if the snippet only contains placeholder assignments.

    Parameters
    ----------
    snippet : str
        The code snippet to inspect.
    query_terms : list[str] or None, optional
        Search terms extracted from the query that produced this snippet.
        When provided, only assignments whose variable name matches one of
        these terms are considered when determining if the snippet is a
        placeholder. This helps avoid false positives caused by unrelated
        variables with real values in the same snippet.
    """

    if re.search(r"<[^>]+>", snippet):
        return True
    if re.search(r"\${[^}]+}", snippet):
        return True

    assignments = ENV_ASSIGN_RE.findall(snippet)
    if not assignments:
        return False

    query_vars = {t.upper() for t in query_terms} if query_terms else None
    found = False

    for var, val in assignments:
        if query_vars and var.upper() not in query_vars:
            continue
        found = True
        clean = val.strip('"\'')
        if clean and clean not in PLACEHOLDER_VALUES and not clean.isdigit():
            if _shannon_entropy(clean) > entropy_threshold:
                return False

    return found

def extract_snippets(content, query, filter_placeholders=True, allowlist_patterns=None):
    """Extract and verify snippets that triggered a search rule.

    Parameters
    ----------
    content : str
        File content to scan.
    query : str
        Query string that produced the hit.
    filter_placeholders : bool, optional
        If True, drop snippets that only contain placeholder values or
        environment variable references.
    allowlist_patterns : list[str] or None, optional
        Patterns that identify allowed or dummy secrets. If a snippet
        matches any of these patterns it will be ignored.
    """

    query_terms = extract_search_terms(query)
    snippets = []
    config = load_config()
    use_scanner = config.get("USE_DETECT_SECRETS", False)
    baseline = config.get("DETECT_SECRETS_BASELINE") or None
    entropy_threshold = config.get("ENTROPY_THRESHOLD", DEFAULT_ENTROPY_THRESHOLD)

    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        for match in pattern.finditer(content):
            # Grab a larger snippet around the search term for more context
            start = max(match.start() - 60, 0)
            end = min(match.end() + 60, len(content))
            snippet = content[start:end].replace('\n', ' ').strip()
            if snippet not in snippets and not _has_allowlist_comment(content, start, end):
                snippets.append(snippet)

    verified = []
    for snippet in snippets:
        if any(re.search(re.escape(t), snippet, re.IGNORECASE) for t in query_terms):
            if allowlist_patterns and any(re.search(p, snippet, re.I) for p in allowlist_patterns):
                continue
            if use_scanner and not snippet_has_secret(snippet, baseline_file=baseline):
                continue
            if not filter_placeholders or not _is_placeholder_snippet(snippet, query_terms=query_terms, entropy_threshold=entropy_threshold):
                verified.append(snippet)

    return verified

def save_data_to_excel(data_list, domain):
    """
    Saves the search results data to an Excel file with a filename that includes
    the domain name and the current date and time.

    Parameters:
    data_list (list of dict): List containing the data of search results.
    domain (str): The domain name used in the search.
    """
    if not data_list:
        print("No data to save to Excel.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{domain}_search_results_{timestamp}.xlsx"

    df = pd.DataFrame(data_list)
    # Convert the list of snippets into a string for Excel compatibility
    df['snippets'] = df['snippets'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


def perform_grouped_searches(domain):
    """
    Performs searches on GitHub based on user-selected query groups.
    Dynamically updates the search queries based on the provided domain.
    Ignores files specified in the configuration.

    Parameters:
    - domain (str): The domain to be used in the search queries.
    """
    config = load_config()
    filter_placeholders = config.get("FILTER_PLACEHOLDERS", True)
    updated_search_groups = create_search_queries(domain, filter_placeholders=filter_placeholders)
    ignored_filenames = config.get('IGNORED_FILENAMES', [])
    all_data = []  # Initialize an empty list to store all the search results


    # Display available search groups with numbers
    print("Available Search Groups:")
    for i, group_name in enumerate(updated_search_groups, start=1):
        print(f"{i}. {group_name}")
    print("Type 'all' to Perform All Searches")

    # Get user choice and process it
    choice = input("Enter your choice (number) or 'all': ").strip()
    selected_groups = []
    if choice.lower() == 'all':
        selected_groups = updated_search_groups.keys()
    elif choice.isdigit():
        choice_num = int(choice)
        if choice_num in range(1, len(updated_search_groups) + 1):
            selected_group_name = list(updated_search_groups.keys())[choice_num - 1]
            selected_groups = [selected_group_name]
        else:
            print("Invalid choice. Please enter a valid number or 'all'.")
            return
    else:
        print("Invalid choice. Please enter a number or 'all'.")
        return

    # Execute searches for each selected group
    for group_name in selected_groups:
        print(f"\nSearching in group: {group_name}")
        queries = updated_search_groups[group_name]
        for query in queries:
            print(f"Executing search for: {query}")
            headers = GitSleuth_API.get_headers()
            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                process_search_results(
                    search_results,
                    all_data,
                    query,
                    headers,
                    group_name,
                    ignored_filenames,
                    domain,
                    filter_placeholders,
                )
            else:
                print(f"No results found for query: {query}")

def check_and_handle_rate_limit(headers):
    """
    Checks and handles the GitHub API rate limit.

    Parameters:
    headers (dict): Headers including the current GitHub token for API requests.
    """
    remaining_limit, wait_time = GitSleuth_API.check_rate_limit(headers)
    if remaining_limit <= 5:
        wait_time = wait_time or 60
        print("Rate limit is low. Waiting to reset...")
        time.sleep(wait_time)

def perform_custom_search(domain):
    """
    Performs a custom search on GitHub based on user input.

    Parameters:
    domain (str): The domain to be appended to the search query.
    """
    custom_query = input("Enter your custom search query: ")
    full_query = f"{custom_query} {domain}"  # Appends the domain to the search query
    config = load_config()
    headers = GitSleuth_API.get_headers()
    filter_placeholders = config.get("FILTER_PLACEHOLDERS", True)
    search_results = GitSleuth_API.search_github_code(full_query, headers)
    description = get_query_description(full_query, domain)
    all_data = []
    if search_results and 'items' in search_results:
        for item in search_results['items']:
            repo_name = item['repository']['full_name']
            file_path = item['path']
            file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
            if file_contents:
                allowlist = config.get("ALLOWLIST_PATTERNS", [])
                snippets = extract_snippets(
                    file_contents,
                    full_query,
                    filter_placeholders=config.get("FILTER_PLACEHOLDERS", True),
                    allowlist_patterns=allowlist,
                )
                if not snippets:
                    print(f"No snippets found in {file_path} for query '{full_query}'")
                    continue  # Skip to next item if no snippets are found
                file_data = {
                    'repo': repo_name,
                    'file_path': file_path,
                    'snippets': snippets,
                    'search_term': full_query,
                    'description': description
                }
                all_data.append(file_data)
                process_and_display_data(file_data, full_query, description)
            else:
                print(f"No file contents found for {file_path}")
    else:
        print("No results found for your query.")
    save_data_to_excel(all_data, 'custom_search_results.xlsx')

def main():
    """
    The main function for running the gitsleuth application.
    Provides a command line interface for setting up the GitHub token, 
    performing searches, and managing the configuration.
    """
    initialize_logging()
    clear_screen()
    domain = get_domain_input()
    all_data = []  # Initialize outside the loop to collect data from all searches

    try:
        while True:

            print("\n1. OAuth Login\n2. Perform Group Searches\n3. Perform Custom Search\n4. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                oauth_login_flow()
            elif choice == '2':
                perform_grouped_searches(domain)
            elif choice == '3':
                perform_custom_search(domain)
            elif choice == '4':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 4.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving the data collected so far...")
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{domain}_search_results_{formatted_time}.xlsx"
        save_data_to_excel(all_data, filename)
        print(f"Data saved to {filename}. Exiting the program.")
        sys.exit(0)

if __name__ == "__main__":
    main()
