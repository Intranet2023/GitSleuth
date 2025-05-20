#GitSleuth.py
import os
import time
import pandas as pd
import json
import logging
import re
from GitSleuth_Groups import create_search_queries
import GitSleuth_API
import platform
import sys
from datetime import datetime
import requests
from prettytable import PrettyTable
from colorama import Fore, Style
from GitSleuth_API import RateLimitException
from Token_Manager import load_tokens

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

    # Load and decrypt tokens from Token Manager
    decrypted_tokens = load_tokens()
    config['GITHUB_TOKENS'] = list(decrypted_tokens.values()) if decrypted_tokens else []
    logging.debug(f"Config loaded. Tokens available: {len(config['GITHUB_TOKENS'])}")
    return config

def process_search_item(item, query, headers, all_data):
    """
    Processes a single item from GitHub search results.

    Parameters:
    - item (dict): The item from search results.
    - query (str): The query used for the search.
    - headers (dict): The headers used for API requests.
    - all_data (list): A list to store the processed data.

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
        snippets = extract_snippets(file_contents, query)
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
            headers = get_headers(config)
            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                new_result_found = True  # New results were found
                # Handle search results here
                # (You can process and log the results as needed)
            break
        except RateLimitException as e:
            logging.warning(str(e))
            if not switch_token(config):
                logging.error("All tokens exhausted and rate limit still reached.")
                return False
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

    search_groups = create_search_queries(domain)

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
                except RateLimitException:
                    logging.warning("Rate limit reached, attempting to switch token.")
                    if switch_token(config):
                        retry_count += 1
                    else:
                        logging.error("All tokens exhausted.")
                        return
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

def truncate_snippet(snippet, length=100):
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
        headers = get_headers(config)
        try:
            search_results = GitSleuth_API.search_github_code(query, headers)
            if 'items' in search_results:
                return search_results
            else:
                logging.info(f"No results found for query: {query}")
                return None
        except RateLimitException as e:
            logging.warning(str(e))
            if retry_count < max_retries - 1:
                switch_token(config)  # Rotate the token only if more retries are left
            retry_count += 1

    logging.error("Max retries reached. Unable to complete the API request.")
    return None

def process_and_display_data(data, search_term):
    """
    Formats and displays the search result data in a tabular format.

    This function constructs a table using PrettyTable to display each piece of data, 
    including the repository name, file path, search term, and found snippets. 
    Snippets are truncated for readability and the search term within them is highlighted.

    Parameters:
    - data (dict): Data of a single repository.
    - search_term (str): The search term used in the GitHub search.
    """
    table = PrettyTable()
    table.field_names = [Fore.BLUE + "Attribute" + Style.RESET_ALL, Fore.BLUE + "Value" + Style.RESET_ALL]
    table.align = "l"

    for key, value in data.items():
        if key == 'snippets':
            highlighted_snippets = [highlight_search_term(truncate_snippet(snippet), search_term) for snippet in value]
            snippets_text = '\n'.join(highlighted_snippets)
            table.add_row([key, snippets_text])
        else:
            table.add_row([key, value])

    print(table)

def process_search_results(search_results, all_data, query, headers, group_name, ignored_filenames):
    """
    Processes search results, extracting file contents and snippets.

    Iterates over search results, handles API requests for file contents,
    and extracts relevant snippets. Appends processed data to a list.

    Parameters:
    - search_results (dict): The search results from the GitHub API.
    - all_data (list): The list to append processed data to.
    - query (str): The search query used.
    - headers (dict): Headers for GitHub API requests.
    - group_name (str): The name of the search group.
    - ignored_filenames (list): List of filenames to ignore in the search.
    """
    for item in search_results['items']:
        if item['path'] not in ignored_filenames:
            repo_name = item['repository']['full_name']
            file_path = item.get('path', '')
            try:
                file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
                if file_contents:
                    snippets = extract_snippets(file_contents, query)
                    if snippets:
                        file_data = {
                            'repo': repo_name,
                            'file_path': file_path,
                            'snippets': snippets,
                            'search_term': query,
                            'group': group_name
                        }
                        all_data.append(file_data)
                        process_and_display_data(file_data, query)  # Pass query as search_term
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

def set_github_token():
    """
    Sets the GitHub tokens in the configuration file.

    Prompts the user to enter GitHub tokens one by one. The entered tokens are saved 
    to the configuration file. This allows the user to update the GitHub tokens used 
    for API requests.
    """
    tokens = []
    while True:
        token = input("Enter a GitHub token (or just press enter to finish): ")
        if not token:
            break
        tokens.append(token)
    
    if tokens:
        config = load_config()
        config['GITHUB_TOKENS'] = tokens
        save_config(config)
        logging.info("GitHub tokens set successfully.")
    else:
        logging.info("No tokens entered.")

def delete_github_token():
    """
    Deletes the stored GitHub API tokens from the configuration file after confirmation.

    Removes the GitHub tokens from the configuration file if they are present and
    the user confirms the deletion. This function is useful for clearing outdated 
    or invalid tokens.
    """
    config = load_config()
    if 'GITHUB_TOKENS' in config:
        # Display a confirmation message
        confirm = input("Are you sure you want to delete all GitHub tokens? (yes/no): ").strip().lower()
        if confirm == 'yes':
            del config['GITHUB_TOKENS']
            save_config(config)
            logging.info("GitHub tokens deleted.")
        else:
            logging.info("Token deletion cancelled.")
    else:
        logging.info("No GitHub tokens were set.")

def view_github_token():
    """
    Displays the currently stored GitHub API tokens.

    Prints the currently stored GitHub tokens to the console. This function 
    is useful for verifying which tokens are currently in use.
    """
    config = load_config()
    if 'GITHUB_TOKENS' in config:
        print("Current GitHub tokens:", config['GITHUB_TOKENS'])
    else:
        print("No GitHub tokens are currently set.")

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
        return {'Authorization': f'token {token}'}
    else:
        logging.error("No GitHub tokens are set. Check the configuration.")
        return {}


def extract_snippets(content, query):
    """
    Extracts snippets from content that contain any of the terms in the query.

    Splits the query into separate terms and searches for each term independently in the content.
    Extracts a snippet of content around each occurrence of any term.

    Parameters:
    - content (str): Content to search within.
    - query (str): Query to match against, can contain multiple terms.

    Returns:
    - list: A list of snippets that contain any of the terms in the query.
    """
    query_terms = query.split()  # Split query into individual terms
    snippets = []

    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        for match in pattern.finditer(content):
            start = max(match.start() - 30, 0)  # Reducing context to 30 characters
            end = min(match.end() + 30, len(content))
            snippet = content[start:end].replace('\n', ' ').strip()
            if snippet not in snippets:  # Avoid duplicate snippets
                snippets.append(snippet)
    return snippets

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

def switch_token(config):
    """
    Switches between the stored GitHub tokens in a round-robin fashion.
    Returns True if a new token is switched to, False otherwise.
    """
    if 'GITHUB_TOKENS' in config and len(config['GITHUB_TOKENS']) > 1:
        config['GITHUB_TOKENS'].append(config['GITHUB_TOKENS'].pop(0))
        new_token = config['GITHUB_TOKENS'][0]
        logging.info(f"Switched to next GitHub token: {new_token[:4]}****")
        return True
    else:
        logging.warning("No additional GitHub tokens available for switching.")
        return False

def perform_grouped_searches(domain):
    """
    Performs searches on GitHub based on user-selected query groups.
    Dynamically updates the search queries based on the provided domain.
    Ignores files specified in the configuration.

    Parameters:
    - domain (str): The domain to be used in the search queries.
    """
    updated_search_groups = create_search_queries(domain)
    config = load_config()
    ignored_filenames = config.get('IGNORED_FILENAMES', [])
    all_data = []  # Initialize an empty list to store all the search results

    if 'GITHUB_TOKENS' not in config or not config['GITHUB_TOKENS']:
        logging.error("GitHub tokens are not properly set. Please set them first.")
        return

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
            headers = get_headers(config)
            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                process_search_results(search_results, all_data, query, headers, group_name, ignored_filenames)
            else:
                print(f"No results found for query: {query}")

def check_and_handle_rate_limit(headers):
    """
    Checks and handles the GitHub API rate limit.

    Parameters:
    headers (dict): Headers including the current GitHub token for API requests.
    """
    remaining_limit = GitSleuth_API.check_rate_limit(headers)
    if remaining_limit <= 5:
        print("Rate limit is low. Waiting to reset...")
        time.sleep(60)  # Waits for 1 minute

def perform_custom_search(domain):
    """
    Performs a custom search on GitHub based on user input.

    Parameters:
    domain (str): The domain to be appended to the search query.
    """
    custom_query = input("Enter your custom search query: ")
    full_query = f"{custom_query} {domain}"  # Appends the domain to the search query
    config = load_config()
    headers = get_headers(config)
    search_results = GitSleuth_API.search_github_code(full_query, headers)
    all_data = []
    if search_results and 'items' in search_results:
        for item in search_results['items']:
            repo_name = item['repository']['full_name']
            file_path = item['path']
            file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
            if file_contents:
                snippets = extract_snippets(file_contents, full_query)
                if not snippets:
                    print(f"No snippets found in {file_path} for query '{full_query}'")
                    continue  # Skip to next item if no snippets are found
                file_data = {
                    'repo': repo_name,
                    'file_path': file_path,
                    'snippets': snippets,
                    'search_term': full_query
                }
                all_data.append(file_data)
                process_and_display_data(file_data, full_query)
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
            print("\n1. Set GitHub Token\n2. Delete GitHub Token\n3. View GitHub Token\n4. Perform Group Searches\n5. Perform Custom Search\n6. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                set_github_token()
            elif choice == '2':
                delete_github_token()
            elif choice == '3':
                view_github_token()
            elif choice == '4':
                perform_grouped_searches(domain)  # Ensure all_data is passed and updated
            elif choice == '5':
                perform_custom_search(domain)  # Ensure all_data is passed and updated
            elif choice == '6':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving the data collected so far...")
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{domain}_search_results_{formatted_time}.xlsx"
        save_data_to_excel(all_data, filename)
        print(f"Data saved to {filename}. Exiting the program.")
        sys.exit(0)

if __name__ == "__main__":
    main()
