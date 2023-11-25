#GitSleuth.py

import os
import pandas as pd
import json
import logging
import time
import re
from GitSleuth_Groups import create_search_queries
import GitSleuth_API
import platform

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
            return json.load(file)
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from configuration file: {e}")
        return {}

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

# ... (Previous code from Part 1)

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
    Deletes the stored GitHub API tokens from the configuration file.

    Removes the GitHub tokens from the configuration file if they are present.
    This function is useful for clearing outdated or invalid tokens.
    """
    config = load_config()
    if 'GITHUB_TOKENS' in config:
        del config['GITHUB_TOKENS']
        save_config(config)
        logging.info("GitHub tokens deleted.")
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
    Extracts snippets from content that match the search query using regex.

    Parameters:
    content (str): The content to search within.
    query (str): The query to match.

    Returns:
    list: A list of snippets that match the query.
    """
    if query not in content:  # Quick check if query is present
        logging.info(f"Query '{query}' not found in content.")
        return []

    snippets = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    for match in pattern.finditer(content):
        start = max(match.start() - 100, 0)  # Grabbing some context around the match
        end = min(match.end() + 100, len(content))
        snippet = content[start:end].replace('\n', ' ').strip()
        snippets.append(snippet)
    return snippets

def save_data_to_excel(data_list, filename):
    """
    Saves the search results data to an Excel file.

    Parameters:
    data_list (list of dict): List containing the data of search results.
    filename (str): The filename to save the Excel file as.
    """
    if not data_list:
        print("No data to save to Excel.")
        return

    df = pd.DataFrame(data_list)
    # If the snippets are lists, convert them to strings for Excel compatibility
    df['snippets'] = df['snippets'].apply(lambda x: '\n'.join(x))
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

def perform_search(search_function, search_groups, filename):
    """
    Performs a search on GitHub using a specified function and search groups,
    and saves the results to an Excel file.
    
    Parameters:
    - search_function (function): The search function to use (grouped or custom).
    - search_groups (dict): Dictionary of search groups with queries.
    - filename (str): Filename for the Excel output.
    """
    # Load the configuration to get GitHub tokens
    config = load_config()
    if 'GITHUB_TOKENS' not in config or len(config['GITHUB_TOKENS']) < 1:
        print("GitHub tokens are not properly set. Please set them first.")
        return

    all_data = []  # Initialize a list to store all search results

    # Iterate over each search group and its queries
    for group_name, queries in search_groups.items():
        print(f"\nSearching in group: {group_name}")
        for query in queries:
            # Prepare headers for the GitHub API request
            headers = get_headers(config)
            print(f"Executing search for: {query}")  # Log the search term
            search_results = search_function(query, headers)

            # Check if the search results are valid and have items
            if search_results and 'items' in search_results:
                for item in search_results['items']:
                    try:
                        # Extract repository name and file path from each item
                        repo_name = item['repository']['full_name']
                        file_path = item.get('path', '')
                        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)

                        if file_contents:
                            # Extract snippets from file contents based on the query
                            snippets = extract_snippets(file_contents, query)
                            file_data = {
                                'repo': repo_name,
                                'file_path': file_path,
                                'snippets': snippets,
                                'search_term': query
                            }
                            all_data.append(file_data)
                            
                            # Call to process and display data
                            process_and_display_data(file_data)                    
                    except KeyError as e:
                        # Log any key errors encountered during data processing
                        logging.error(f"Key error processing search result item: {e}")

            else:
                print(f"No results found for {query}")

            # Delay to avoid hitting rate limits
            time.sleep(10)

    # Save all collected data to an Excel file
    save_data_to_excel(all_data, filename)

# Rest of your code...

def process_and_display_data(data):
    """
    Formats and prints repository data to the console, including decoded README contents.
    Parameters:
    data (dict): Dictionary containing the data of a single repository.
    """
    print("\nRepository Details:")
    for key, value in data.items():
        if key == 'snippets' and value:
            print(f"Snippets:")
            for snippet in value:
                print(f" - {snippet}")
        else:
            print(f"{key}: {value}")
    print("--------------------------------------------")


def get_domain_input():
    """
    Prompts the user to enter their organization's domain for search.
    Returns:
    str: The entered domain.
    """
    return input("Enter your organization's domain for search (e.g., 'ge.com'): ")

# def perform_grouped_searches(domain):
#     """
#     Performs searches on GitHub based on predefined query groups,
#     dynamically updating the search queries based on the provided domain.
    
#     Iterates through each group of search queries, executes them, and processes
#     the results to extract relevant information, including snippets of content
#     around the search terms found in the files of the repositories.

#     Parameters:
#     domain (str): The domain to be used in the search queries.
#     """
#     updated_search_groups = create_search_queries(domain)
#     config = load_config()
#     if 'GITHUB_TOKENS' not in config or not config['GITHUB_TOKENS']:
#         logging.error("GitHub tokens are not properly set. Please set them first.")
#         return

#     all_data = []
#     for group_name, queries in updated_search_groups.items():
#         logging.info(f"Searching for {group_name}")
#         for query in queries:
#             headers = get_headers(config)
#             check_and_handle_rate_limit(headers)

#             search_results = GitSleuth_API.search_github_code(query, headers)
#             if search_results and 'items' in search_results:
#                 for item in search_results['items']:
#                     repo_name = item['repository']['full_name']
#                     file_path = item.get('path', '')
#                     file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)

#                     if file_contents:
#                         logging.info(f"Checking file: {file_path}")
#                         logging.info(f"File contents: {file_contents[:500]}...")  # Debugging

#                         snippets = extract_snippets(file_contents, "ge.com")  # Ensure correct query
#                         if not snippets:
#                             logging.info(f"No snippets extracted for file: {file_path}")

#                         file_data = {
#                             'repo': repo_name,
#                             'file_path': file_path,
#                             'snippets': snippets,
#                             'search_term': query
#                         }
#                         all_data.append(file_data)
#                         process_and_display_data(file_data)
#             else:
#                 logging.info(f"No results found for {query}")

#             # Rotate the token if needed
#             config = switch_token(config)
#             save_config(config)

#     save_data_to_excel(all_data, 'group_search_results.xlsx')
def perform_grouped_searches(domain):
    """
    Performs searches on GitHub based on user-selected query groups,
    dynamically updating the search queries based on the provided domain.

    Parameters:
    domain (str): The domain to be used in the search queries.
    """
    updated_search_groups = create_search_queries(domain)
    config = load_config()
    if 'GITHUB_TOKENS' not in config or not config['GITHUB_TOKENS']:
        logging.error("GitHub tokens are not properly set. Please set them first.")
        return

    # Display a menu with the search groups
    print("Available Search Groups:")
    for i, group_name in enumerate(updated_search_groups.keys(), start=1):
        print(f"{i}. {group_name}")
    print(f"{i+1}. Perform All Searches")

    choice = input("Enter your choice (number) or 'all' to perform all searches: ").strip()
    
    selected_groups = []
    if choice.lower() == 'all':
        selected_groups = updated_search_groups.keys()
    else:
        try:
            choice = int(choice)
            if 1 <= choice <= len(updated_search_groups):
                selected_group_name = list(updated_search_groups.keys())[choice - 1]
                selected_groups = [selected_group_name]
            else:
                print("Invalid choice. Please enter a valid number.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

    all_data = []
    for group_name in selected_groups:
        queries = updated_search_groups[group_name]
        logging.info(f"Searching for {group_name}")
        for query in queries:
            headers = get_headers(config)
            check_and_handle_rate_limit(headers)

            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                for item in search_results['items']:
                    repo_name = item['repository']['full_name']
                    file_path = item.get('path', '')
                    file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)

                    if file_contents:
                        logging.info(f"Checking file: {file_path}")
                        logging.info(f"File contents: {file_contents[:500]}...")  # Debugging

                        snippets = extract_snippets(file_contents, "ge.com")  # Ensure correct query
                        if not snippets:
                            logging.info(f"No snippets extracted for file: {file_path}")

                        file_data = {
                            'repo': repo_name,
                            'file_path': file_path,
                            'snippets': snippets,
                            'search_term': query
                        }
                        all_data.append(file_data)
                        process_and_display_data(file_data)
            else:
                logging.info(f"No results found for {query}")

            # Rotate the token if needed
            config = switch_token(config)
            save_config(config)

    save_data_to_excel(all_data, 'group_search_results.xlsx')


def check_and_handle_rate_limit(headers):
    """
    Checks the current rate limit for GitHub API requests and handles it.

    If the rate limit is close to being reached, it pauses the execution for a while, allowing
    the rate limit to reset. This ensures the script does not hit GitHub's rate limit.

    Parameters:
    headers (dict): Headers including the current GitHub token for API requests.
    """
    remaining_limit = GitSleuth_API.check_rate_limit(headers)
    if remaining_limit <= 5:
        logging.warning("Rate limit is low. Waiting to reset...")
        time.sleep(60)  # Waits for 1 minute

def perform_grouped_searches(domain):
    """
    Performs searches on GitHub based on user-selected query groups,
    dynamically updating the search queries based on the provided domain.

    Parameters:
    domain (str): The domain to be used in the search queries.
    """
    updated_search_groups = create_search_queries(domain)
    config = load_config()
    if 'GITHUB_TOKENS' not in config or not config['GITHUB_TOKENS']:
        logging.error("GitHub tokens are not properly set. Please set them first.")
        return

    # Display a menu with the search groups
    print("Available Search Groups:")
    for i, group_name in enumerate(updated_search_groups.keys(), start=1):
        print(f"{i}. {group_name}")
    print(f"{i+1}. Perform All Searches")

    choice = input("Enter your choice (number) or 'all' to perform all searches: ").strip()
    
    selected_groups = []
    if choice.lower() == 'all':
        selected_groups = updated_search_groups.keys()
    else:
        try:
            choice = int(choice)
            if 1 <= choice <= len(updated_search_groups):
                selected_group_name = list(updated_search_groups.keys())[choice - 1]
                selected_groups = [selected_group_name]
            else:
                print("Invalid choice. Please enter a valid number.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

    all_data = []
    for group_name in selected_groups:
        queries = updated_search_groups[group_name]
        logging.info(f"Searching for {group_name}")
        for query in queries:
            headers = get_headers(config)
            check_and_handle_rate_limit(headers)

            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                for item in search_results['items']:
                    repo_name = item['repository']['full_name']
                    file_path = item.get('path', '')
                    file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)

                    if file_contents:
                        logging.info(f"Checking file: {file_path}")
                        logging.info(f"File contents: {file_contents[:500]}...")  # Debugging

                        snippets = extract_snippets(file_contents, "ge.com")  # Ensure correct query
                        if not snippets:
                            logging.info(f"No snippets extracted for file: {file_path}")

                        file_data = {
                            'repo': repo_name,
                            'file_path': file_path,
                            'snippets': snippets,
                            'search_term': query
                        }
                        all_data.append(file_data)
                        process_and_display_data(file_data)
            else:
                logging.info(f"No results found for {query}")

            # Rotate the token if needed
            config = switch_token(config)
            save_config(config)

    save_data_to_excel(all_data, 'group_search_results.xlsx')

def perform_custom_search(domain):
    """
    Performs a custom search on GitHub based on user input,
    appending the provided domain to the search query.

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
                process_and_display_data(file_data)
            else:
                print(f"No file contents found for {file_path}")
    else:
        print("No results found for your query.")

    # Save the data to an Excel file
    save_data_to_excel(all_data, 'custom_search_results.xlsx')


def main():
    """
    Main function offering options to manage the API key, set the search domain, and perform searches.

    Provides a command-line interface for the user to interact with the script's functionalities,
    including managing GitHub tokens, setting the search domain, and executing custom or grouped searches.
    """
    initialize_logging()  # Initialize logging based on config file
    clear_screen()

    domain = get_domain_input()  # Retrieve domain input from the user
    updated_search_groups = create_search_queries(domain)

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
            perform_grouped_searches(domain)
        elif choice == '5':
            perform_custom_search(domain)
        elif choice == '6':
            logging.info("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main()