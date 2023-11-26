import os
import pandas as pd
import json
import logging
import time
from GitSleuth_Groups import create_search_queries
import GitSleuth_API
import platform

CONFIG_FILE = 'config.json'

def load_config():
    """
    Loads the configuration from the config file.
    Attempts to open and read the configuration file. If the file is not found,
    logs the error and returns an empty dictionary.
    Returns a configuration dictionary or an empty dict if the file is not found.
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
    Defaults to INFO level if no configuration is found.
    """
    config = load_config()
    log_level = config.get('LOG_LEVEL', 'INFO').upper()
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

def clear_screen():
    """
    Clears the terminal screen for a cleaner user experience.
    Uses system calls specific to the operating system.
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
    Extracts snippets from content that match the search query.

    This function searches through the content for occurrences of the specified query.
    It then extracts a snippet of content around each occurrence.

    Parameters:
    - content (str): Content to search within.
    - query (str): Query to match against the content.

    Returns:
    - list: A list of snippets that contain the query.
    """
    snippets = []
    lines = content.splitlines()
    for line in lines:
        if query in line:
            snippets.append(line)  # Consider including surrounding lines for context
    return snippets

def switch_token(config):
    """
    Switches between the stored GitHub tokens in a round-robin fashion.
    Parameters:
    config (dict): Configuration data including the GitHub tokens.
    Returns:
    dict: Updated configuration with the switched token.
    """
    config['GITHUB_TOKENS'].append(config['GITHUB_TOKENS'].pop(0))
    return config

def process_search_results(search_results, all_data, query, headers):
    """
    Processes and handles search results by extracting file contents and snippets.

    This function iterates over the search results, fetches file contents, extracts snippets,
    and then appends the processed data to a collective list. It logs information about 
    each file and snippet found.

    Parameters:
    - search_results (dict): The search results from the GitHub API.
    - all_data (list): The list to append the processed data to.
    - query (str): The search query used in the GitHub search.
    - headers (dict): Headers for the GitHub API requests.
    """
    for item in search_results['items']:
        repo_name = item['repository']['full_name']
        file_path = item.get('path', '')
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)

        if file_contents:
            snippets = extract_snippets(file_contents, query)
            if snippets:
                file_data = {
                    'repo': repo_name,
                    'file_path': file_path,
                    'snippets': snippets,
                    'search_term': query
                }
                all_data.append(file_data)
                process_and_display_data(file_data)
            else:
                logging.info(f"No relevant snippets found in {file_path} for query '{query}'")
        else:
            logging.info(f"No file contents found for {file_path}")


def process_and_display_data(data):
    """
    Formats and prints repository data to the console, including snippets.

    This function formats and displays each piece of data, including the repository name,
    file path, search term, and any found snippets. It ensures that the data is presented
    in a readable and organized manner.

    Parameters:
    - data (dict): Dictionary containing the data of a single repository.
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
    Returns the entered domain as a string.
    """
    return input("Enter your organization's domain for search (e.g., 'ge.com'): ")

def save_data_to_excel(data_list, filename):
    """
    Saves the search results data to an Excel file.

    This function takes a list of dictionaries, each representing search results,
    and saves it to an Excel file. The function handles cases where the data list
    might be empty, ensuring that an empty Excel file is not created unnecessarily.
    The snippets, which are lists themselves, are joined into a single string for
    better representation in the Excel file.

    Parameters:
    data_list (list of dict): List containing the data of search results.
    filename (str): The filename to save the Excel file as.

    Returns:
    None: The function doesn't return anything but creates an Excel file.
    """
    if not data_list:
        print("No data to save to Excel.")
        return

    df = pd.DataFrame(data_list)
    # Convert the list of snippets into a string for Excel compatibility
    df['snippets'] = df['snippets'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


def perform_grouped_searches(domain):
    logging.info("Initializing grouped searches")
    updated_search_groups = create_search_queries(domain)
    config = load_config()
    if 'GITHUB_TOKENS' not in config or not config['GITHUB_TOKENS']:
        logging.error("GitHub tokens are not properly set. Exiting grouped searches.")
        return

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
                logging.error("Invalid choice. Please enter a valid number.")
                return
        except ValueError:
            logging.error("Invalid input. Please enter a number.")
            return

    all_data = []
    for group_name in selected_groups:
        queries = updated_search_groups[group_name]
        logging.info(f"Starting search for group: {group_name}")
        for query in queries:
            headers = get_headers(config)
            logging.info(f"Executing search for query: {query}")
            search_results = GitSleuth_API.search_github_code(query, headers)
            if search_results and 'items' in search_results:
                logging.info(f"Processing search results for query: {query}")
                process_search_results(search_results, all_data, query, headers)
            else:
                logging.warning(f"No results found for query: {query}")
            time.sleep(10)  # Pausing between searches

    save_data_to_excel(all_data, 'group_search_results.xlsx')



def perform_search(search_function, search_groups, filename):
    config = load_config()
    if 'GITHUB_TOKENS' not in config or len(config['GITHUB_TOKENS']) < 1:
        print("GitHub tokens are not properly set. Please set them first.")
        return

    all_data = []
    for group_name, queries in search_groups.items():
        print(f"\nSearching in group: {group_name}")
        for query in queries:
            headers = get_headers(config)
            print(f"Executing search for: {query}")
            search_results = search_function(query, headers)

            if search_results and 'items' in search_results:
                for item in search_results['items']:
                    repo_name = item['repository']['full_name']
                    file_path = item.get('path', '')
                    file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
                    
                    if file_contents:
                        keyword = "relevant_keyword_from_query"  # Update this based on your query
                        snippets = extract_snippets(file_contents, keyword)
                        file_data = {
                            'repo': repo_name,
                            'file_path': file_path,
                            'snippets': snippets,
                            'search_term': query
                        }
                        all_data.append(file_data)
                        process_and_display_data(file_data)
            else:
                print(f"No results found for {query}")

            time.sleep(10)  # Pausing between searches

    save_data_to_excel(all_data, filename)

def perform_custom_search(domain):
    """
    Performs a custom search on GitHub based on user input.
    Appends the provided domain to the search query.
    Parameters:
    domain (str): The domain to be appended to the search query.
    """
    custom_query = input("Enter your custom search query: ")
    full_query = f"{custom_query} {domain}"

    config = load_config()
    headers = get_headers(config)
    search_results = GitSleuth_API.search_github_code(full_query, headers)

    all_data = []
    if search_results and 'items' in search_results:
        process_search_results(search_results, all_data, full_query, headers)
    else:
        print("No results found for your query.")

    save_data_to_excel(all_data, 'custom_search_results.xlsx')

def set_github_token():
    """
    Sets the GitHub tokens in the configuration file.
    Prompts the user to enter GitHub tokens one by one and saves them to the configuration file.
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
    Prints the currently stored GitHub tokens to the console for verification.
    """
    config = load_config()
    if 'GITHUB_TOKENS' in config:
        print("Current GitHub tokens:", config['GITHUB_TOKENS'])
    else:
        print("No GitHub tokens are currently set.")

def set_github_token():
    """
    Sets the GitHub tokens in the configuration file.
    Prompts the user to enter GitHub tokens one by one and saves them to the configuration file.
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
    Prints the currently stored GitHub tokens to the console for verification.
    """
    config = load_config()
    if 'GITHUB_TOKENS' in config:
        print("Current GitHub tokens:", config['GITHUB_TOKENS'])
    else:
        print("No GitHub tokens are currently set.")

def main():
    """
    Main function offering options to manage the API key, set the search domain, and perform searches.
    Provides a command-line interface for the user to interact with the script's functionalities.
    """
    initialize_logging()
    clear_screen()

    domain = get_domain_input()

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
