#gitsleuth.py
import os
import pandas as pd
import json
import logging
import time
import re
from gitsleuth_groups import create_search_queries
import gitsleuth_api
import platform
import sys
from datetime import datetime
import requests
from prettytable import PrettyTable
from colorama import Fore, Style

# Configuration file for storing the API tokens and settings
CONFIG_FILE = 'config.json'

def load_config():
    """
    Loads the configuration from the config file.

    Tries to open and read the configuration file. If the file is not found,
    logs the error and returns an empty dictionary.

    Returns:
    dict: Configuration data including the GitHub tokens or an empty dict if the file is not found.
    """
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from configuration file: {e}")
        return {}

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
                file_contents = gitsleuth_api.get_file_contents(repo_name, file_path, headers)
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
    config (dict): Configuration data including the GitHub tokens.

    Returns:
    dict: Headers with the current GitHub token.
    """
    return {'Authorization': f'token {config["GITHUB_TOKENS"][0]}'}

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

    Parameters:
    config (dict): Configuration data including the GitHub tokens.

    Returns:
    dict: Updated configuration with the switched token.
    """
    config['GITHUB_TOKENS'].append(config['GITHUB_TOKENS'].pop(0))  # Rotate the token list
    return config

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
            search_results = gitsleuth_api.search_github_code(query, headers)
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
    remaining_limit = gitsleuth_api.check_rate_limit(headers)
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
    search_results = gitsleuth_api.search_github_code(full_query, headers)
    all_data = []
    if search_results and 'items' in search_results:
        for item in search_results['items']:
            repo_name = item['repository']['full_name']
            file_path = item['path']
            file_contents = gitsleuth_api.get_file_contents(repo_name, file_path, headers)
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
                process_and_display_data(file_data)
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
