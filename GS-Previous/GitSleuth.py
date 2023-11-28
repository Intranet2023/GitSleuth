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
import sys
from datetime import datetime
import requests
from prettytable import PrettyTable
from colorama import Fore, Style
from GitSleuth_API import RateLimitException

# Configuration file for storing the API tokens and settings
CONFIG_FILE = 'config.json'

current_token_index = 0

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



def perform_search(domain, selected_group, config, max_retries=3):
    """
    Perform the search operation, with support for token rotation in case of rate limit.

    Parameters:
    - domain (str): The domain for the search.
    - selected_group (str): The selected search group.
    - config (dict): The configuration dictionary with GitHub tokens.
    - max_retries (int): Maximum number of retries for the search in case of rate limit.

    Returns:
    - None
    """
    search_groups = create_search_queries(domain)
    ignored_filenames = config.get('IGNORED_FILENAMES', [])
    retry_count = 0

    if selected_group == "Search All":
        groups = search_groups.keys()
    else:
        groups = [selected_group]

    for group in groups:
        queries = search_groups.get(group, [])
        for query in queries:
            while retry_count < max_retries:
                try:
                    headers = get_headers(config)
                    search_results = GitSleuth_API.search_github_code(query, headers)
                    if search_results and 'items' in search_results:
                        # Process the search results
                        for item in search_results['items']:
                            if item['path'] not in ignored_filenames:
                                process_search_item(item, query, headers)
                    else:
                        logging.info(f"No results found for query: {query}")
                    break  # Break the while loop if successful
                except RateLimitException as e:
                    logging.warning(str(e))
                    switch_token(config)  # Rotate the token
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error("Max retries reached. Moving to next query.")
                        break  # Exit the retry loop and proceed with next query

# Remember to include the switch_token and get_headers functions in the same file


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

def switch_token(config):
    config['GITHUB_TOKENS'].append(config['GITHUB_TOKENS'].pop(0))
    save_config(config)


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
    config (dict): Configuration data including the GitHub tokens.

    Returns:
    dict: Headers with the current GitHub token.
    """
    global current_token_index
    if 'GITHUB_TOKENS' in config and config['GITHUB_TOKENS']:
        headers = {'Authorization': f'token {config["GITHUB_TOKENS"][current_token_index]}'}
        current_token_index = (current_token_index + 1) % len(config['GITHUB_TOKENS'])
        return headers
    else:
        logging.error("No GitHub tokens are set.")
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
#GitSleuth_GUI.py 
import sys
import csv
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QComboBox,
                             QTableWidget, QTableWidgetItem, QStatusBar, QProgressBar,
                             QFileDialog, QTextEdit, QTabWidget, QAction, QDialog)
from PyQt5.QtCore import Qt
from Token_Manager import load_tokens, add_token, delete_token
import GitSleuth_API
from GitSleuth_Groups import create_search_queries
from GitSleuth import load_config, get_headers, extract_snippets, switch_token, perform_api_request_with_token_rotation
from GitSleuth_API import RateLimitException
class QTextEditHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_message = self.format(record)
        self.text_widget.append(log_message)

class GitSleuthGUI(QMainWindow):
    def __init__(self):
        super(GitSleuthGUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GitSleuth")

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        tab_widget = QTabWidget(self)
        search_results_tab = QWidget()
        log_tab = QWidget()
        groups_editor_tab = QWidget()

        tab_widget.addTab(search_results_tab, "Search Results")
        tab_widget.addTab(log_tab, "Log")
        tab_widget.addTab(groups_editor_tab, "Groups Editor")

        main_layout.addWidget(tab_widget)

        search_results_layout = QVBoxLayout(search_results_tab)

        input_layout = QHBoxLayout()
        self.domain_input = QLineEdit(self)
        input_layout.addWidget(QLabel("Domain:"))
        input_layout.addWidget(self.domain_input)

        self.search_group_dropdown = QComboBox(self)
        input_layout.addWidget(self.search_group_dropdown)
        self.search_group_dropdown.addItems(["Authentication and Credentials", "API Keys and Tokens",
                                             "Database and Server Configurations", "Security and Code Vulnerabilities",
                                             "Historical Data and Leakage", "Custom and Regex-Based Searches"])

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.on_search)
        input_layout.addWidget(self.search_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        input_layout.addWidget(self.stop_button)

        search_results_layout.addLayout(input_layout)

        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Repository", "File Path", "Snippets"])
        search_results_layout.addWidget(self.results_table)

            # Adjust column widths for the results table
        self.results_table.setColumnWidth(0, 200)
        self.results_table.setColumnWidth(1, 300)
        self.results_table.setColumnWidth(2, 500)

        # Status bar setup
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        search_results_layout.addWidget(self.progress_bar)

        log_tab_layout = QVBoxLayout(log_tab)
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        log_handler = QTextEditHandler(self.log_output)
        logging.root.addHandler(log_handler)
        log_tab_layout.addWidget(self.log_output)

        groups_editor_layout = QVBoxLayout(groups_editor_tab)
        self.groups_editor = QTextEdit(self)
        self.load_groups_file()
        groups_editor_layout.addWidget(self.groups_editor)

                # Adding menu for token management
        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu('Settings')
        manage_tokens_action = QAction('Manage Tokens', self)
        manage_tokens_action.triggered.connect(self.open_token_management)
        settings_menu.addAction(manage_tokens_action)

        # Adding "Load Groups" and "Save Groups" buttons to the layout
        save_button = QPushButton("Save Groups", self)
        save_button.clicked.connect(self.save_groups_file)
        groups_editor_layout.addWidget(save_button)

        self.setGeometry(300, 300, 1000, 600)
    def process_search_item(item, query, headers):
        """
        Processes an individual search item.

        Parameters:
        - item (dict): The search result item from GitHub API.
        - query (str): The search query used.
        - headers (dict): Headers for GitHub API requests.
        """
        # Extract relevant data from the item
        repo_name = item['repository']['full_name']
        file_path = item.get('path', '')
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
        if file_contents:
            # If you have a function to extract snippets from contents, use it here
            snippets = extract_snippets(file_contents, query)

            # Process snippets (e.g., displaying, storing, or further processing)
            # This part depends on your application's requirements
            print(f"Repository: {repo_name}, File: {file_path}, Snippets: {snippets}")
        else:
            logging.info(f"No file contents found for {file_path}")
# 
    def load_groups_file(self):
        try:
            with open('GitSleuth_Groups.py', 'r') as file:
                self.groups_editor.setText(file.read())
        except Exception as e:
            logging.error(f"Failed to load Groups file: {e}")

    def save_groups_file(self):
        try:
            with open('GitSleuth_Groups.py', 'w') as file:
                file.write(self.groups_editor.toPlainText())
            logging.info("Groups file saved successfully.")
            self.status_bar.showMessage("Groups file saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save Groups file: {e}")
            self.status_bar.showMessage("Error saving Groups file.")

    def open_token_management(self):
        self.token_management_dialog = TokenManagementDialog(self)
        self.token_management_dialog.show()

    def on_search(self):
        domain = self.domain_input.text().strip()
        if not domain:
            self.statusBar().showMessage("Domain is required for searching.")
            return
    
        selected_group = self.search_group_dropdown.currentText()
        self.search_all = selected_group == "Search All"
        self.statusBar().showMessage(f"Searching in {selected_group} for domain: {domain}")
        self.stop_button.setEnabled(True)
        self.search_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.perform_search(domain, selected_group)

        def perform_search(self, domain, selected_group):
            config = load_config()
            search_groups = create_search_queries(domain)
            ignored_filenames = config.get('IGNORED_FILENAMES', [])
            max_retries = 3  # Set your max retries here
        
            if selected_group == "Search All":
                groups = search_groups.keys()
            else:
                groups = [selected_group]
        
            for group in groups:
                queries = search_groups.get(group, [])
                for query in queries:
                    retry_count = 0  # Reset retry count for each new query
                    while retry_count < max_retries:
                        try:
                            headers = get_headers(config)
                            search_results = GitSleuth_API.search_github_code(query, headers)
                            if search_results and 'items' in search_results:
                                for item in search_results['items']:
                                    if item['path'] not in ignored_filenames:
                                        self.process_search_item(item, query, headers)
                                break
                            else:
                                logging.info(f"No results found for query: {query}")
                                break
                        except RateLimitException as e:
                            logging.warning(str(e))
                            if retry_count < max_retries - 1:
                                switch_token(config)
                            retry_count += 1
                            if retry_count >= max_retries:
                                logging.error("Max retries reached. Moving to next query.")
                                break

    #     def perform_search(self, domain, selected_group):
    #         """
    #         Perform the search operation for the given domain and search group.

    #         Parameters:
    #         - domain (str): The domain for the search.
    #         - selected_group (str): The selected search group.
    #         """
    #     config = load_config()  # Load the configuration
    #     search_groups = create_search_queries(domain)
    #     ignored_filenames = config.get('IGNORED_FILENAMES', [])

    #     if selected_group == "Search All":
    #         groups = search_groups.keys()
    #     else:
    #         groups = [selected_group]

    #     for group in groups:
    #         queries = search_groups.get(group, [])
    #         for query in queries:
    #             search_results = perform_api_request_with_token_rotation(query, config)
    #             if search_results:
    #                 for item in search_results['items']:
    #                     if item['path'] not in ignored_filenames:
    #                         self.process_search_item(item, query, get_headers(config))


    # def execute_query(self, query, headers, ignored_filenames):
    #     search_results = GitSleuth_API.search_github_code(query, headers)
    #     if search_results and 'items' in search_results:
    #         for item in search_results['items']:
    #             if item['path'] not in ignored_filenames:
    #                 self.process_search_item(item, query, headers)
    #     else:
    #         logging.info(f"No results found for query: {query}")

    def process_search_item(self, item, query, headers):
        repo_name = item['repository']['full_name']
        file_path = item.get('path', '')
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
        if file_contents:
            snippets = extract_snippets(file_contents, query)
            self.update_results_table(repo_name, file_path, snippets)

    def update_results_table(self, repo_name, file_path, snippets):
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)
        self.results_table.setItem(row_position, 0, QTableWidgetItem(repo_name))
        self.results_table.setItem(row_position, 1, QTableWidgetItem(file_path))
        snippet_text = '\n'.join(snippets)
        self.results_table.setItem(row_position, 2, QTableWidgetItem(snippet_text))

    def stop_search(self):
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Search stopped.")

    def close_application(self):
        self.close()

    def export_results_to_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Repository", "File Path", "Snippets"])
                    for row in range(self.results_table.rowCount()):
                        writer.writerow([
                            self.results_table.item(row, 0).text(),
                            self.results_table.item(row, 1).text(),
                            self.results_table.item(row, 2).text().replace('\n', ' ')
                        ])
                self.status_bar.showMessage("Results exported successfully to " + filename)
            except Exception as e:
                logging.error(f"Error exporting to CSV: {e}")
                self.status_bar.showMessage("Error exporting results.")

class TokenManagementDialog(QDialog):
    """
    Dialog for managing API tokens.
    """
    def __init__(self, parent=None):
        """
        Initializes the Token Management dialog.
        """
        super(TokenManagementDialog, self).__init__(parent)
        self.setWindowTitle('Token Management')
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout(self)

        self.setupUI()

    def setupUI(self):
        """
        Sets up the UI components for the token management dialog.
        """
        # Token Table
        self.token_table = QTableWidget(0, 2)
        self.token_table.setHorizontalHeaderLabels(['Token Name', 'Token Value (masked)'])
        self.layout.addWidget(self.token_table)

        # Add, Delete Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Token')
        self.add_btn.clicked.connect(self.add_token_dialog)
        btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton('Delete Token')
        self.delete_btn.clicked.connect(self.delete_token)
        btn_layout.addWidget(self.delete_btn)

        self.layout.addLayout(btn_layout)

        # Populate table with existing tokens
        self.load_tokens()

    def load_tokens(self):
        """
        Loads and displays the tokens in the table.
        """
        tokens = load_tokens()
        self.token_table.clearContents()
        self.token_table.setRowCount(len(tokens))
        for row, (name, _) in enumerate(tokens.items()):
            self.token_table.setItem(row, 0, QTableWidgetItem(name))
            self.token_table.setItem(row, 1, QTableWidgetItem("********"))  # Masked token

    def add_token_dialog(self):
        """
        Opens a dialog to add a new token.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Token")
        layout = QVBoxLayout(dialog)

        name_label = QLabel("Token Name:")
        self.name_input = QLineEdit(dialog)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        token_label = QLabel("Token Value:")
        self.token_input = QLineEdit(dialog)
        layout.addWidget(token_label)
        layout.addWidget(self.token_input)

        add_button = QPushButton("Add", dialog)
        add_button.clicked.connect(lambda: self.add_token(dialog))
        layout.addWidget(add_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_token(self, dialog):
        """
        Adds a new token to the storage.
        """
        token_name = self.name_input.text()
        token_value = self.token_input.text()
        if token_name and token_value:
            add_token(token_name, token_value)
            self.load_tokens()
            dialog.close()

    def delete_token(self):
        """
        Deletes a selected token.
        """
        selected_row = self.token_table.currentRow()
        if selected_row != -1:
            token_name = self.token_table.item(selected_row, 0).text()
            delete_token(token_name)
            self.load_tokens()
def main():
    """
    Main function to run the GitSleuth application.
    """
    app = QApplication(sys.argv)
    ex = GitSleuthGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
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

#GitSleuth_Groups.py
def create_search_queries(domain):
    """
    Creates a dictionary of search queries for different categories,
    incorporating the given domain and applying strategies to exclude common placeholders.

    Parameters:
    - domain (str): The domain to be included in the search queries.

    Returns:
    - dict: A dictionary where each key is a category, and the value is a list of search queries.
    """
    placeholders = "NOT example NOT dummy NOT test NOT sample NOT placeholder"

    return {
        "Authentication and Credentials": [
            f"filename:.npmrc _auth {domain} {placeholders}",
            f"filename:.dockercfg auth {domain} {placeholders}",
            f"extension:pem private {domain} {placeholders}",
            f"extension:ppk private {domain} {placeholders}",
            f"filename:id_rsa OR filename:id_dsa {domain} {placeholders}",
            f"filename:wp-config.php {domain} {placeholders}",
            f"filename:.htpasswd {domain} {placeholders}",
            f"filename:.env DB_USERNAME NOT homestead {domain} {placeholders}",
            f"filename:credentials aws_access_key_id {domain} {placeholders}",
            f"filename:.s3cfg {domain} {placeholders}",
            f"filename:.git-credentials {domain} {placeholders}"
        ],
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain} {placeholders}",
            f"HEROKU_API_KEY language:shell {domain} {placeholders}",
            f"HEROKU_API_KEY language:json {domain} {placeholders}",
            f"xoxp OR xoxb {domain} {placeholders}",
            f"filename:github-recovery-codes.txt {domain} {placeholders}",
            f"filename:gitlab-recovery-codes.txt {domain} {placeholders}",
            f"filename:discord_backup_codes.txt {domain} {placeholders}"
        ],
        "Database and Server Configurations": [
            f"extension:sql mysql dump {domain} {placeholders}",
            f"extension:sql mysql dump password {domain} {placeholders}",
            f"filename:config.json NOT encrypted NOT secure {domain} {placeholders}",
            f"API_BASE_URL {domain} {placeholders}",
            f"filename:azure-pipelines.yml {domain} {placeholders}",
            f"filename:.aws/config {domain} {placeholders}"
        ],
        "Security and Code Vulnerabilities": [
            f"password 'admin' {domain} {placeholders}",
            f"filename:debug.log {domain} {placeholders}",
            f"pre-shared key {domain} {placeholders}",
            f"filename:*.config \"https://internal.{domain}\" {placeholders}",
            f"language:java \"// TODO: remove before production {domain}\" {placeholders}",
            f"\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3} {domain} {placeholders}",  # IP Address patterns
            f"filename:main.tf aws_access_key_id {domain} {placeholders}"
        ],
        "Historical Data and Leakage": [
            f"\"{domain}.com email\" {placeholders}",
            f"filename:.env DB_PASSWORD NOT current {domain} {placeholders}",
            f"filename:backup.zip {domain} {placeholders}",
            f"filename:dump.sql {domain} {placeholders}",
            f"filename:old_passwords.txt {domain} {placeholders}"
        ],
        "Custom and Regex-Based Searches": [
            f"1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} login {domain} {placeholders}",
            f"SSO 1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} {domain} {placeholders}"
        ]
    }
#Token_Manager
import json
from cryptography.fernet import Fernet

TOKEN_FILE = 'tokens.json'
KEY_FILE = 'token_key.key'

def load_key():
    try:
        with open(KEY_FILE, 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
        return key

key = load_key()
cipher_suite = Fernet(key)

def encrypt_token(token):
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted):
    return cipher_suite.decrypt(token_encrypted.encode()).decode()

def load_tokens():
    try:
        with open(TOKEN_FILE, 'r') as file:
            encrypted_tokens = json.load(file)
        return {name: decrypt_token(token) for name, token in encrypted_tokens.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_tokens(tokens):
    encrypted_tokens = {name: encrypt_token(token) for name, token in tokens.items()}
    with open(TOKEN_FILE, 'w') as file:
        json.dump(encrypted_tokens, file)

def add_token(name, token):
    tokens = load_tokens()
    tokens[name] = token
    save_tokens(tokens)

def delete_token(name):
    tokens = load_tokens()
    if name in tokens:
        del tokens[name]
        save_tokens(tokens)