#GitSleuth_GUI.py
import sys
import json
import csv
import time
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QComboBox,
                             QTableWidget, QTableWidgetItem, QStatusBar, QProgressBar,
                             QFileDialog, QTextEdit, QTabWidget, QAction, QDialog)
from PyQt5.QtCore import Qt
from Token_Manager import load_tokens, add_token, delete_token
import GitSleuth_API
from GitSleuth_Groups import create_search_queries
from GitSleuth import get_headers, extract_snippets, switch_token, perform_api_request_with_token_rotation
from GitSleuth_API import RateLimitException
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTableWidgetItem

CONFIG_FILE = 'config.json'


def load_config():
    """
    Loads the configuration from 'config.json' and the GitHub tokens from 'tokens.json'.
    """
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

config = load_config()
log_level = config.get("LOG_LEVEL", "DEBUG").upper()

# Configure logging with the level from config.json
logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class ClickableTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, url):
        super().__init__(text)
        self.url = url

    def setData(self, role, value):
        if role == Qt.DisplayRole and self.url:
            QDesktopServices.openUrl(QUrl(self.url))
        super().setData(role, value)

class QTextEditHandler(logging.Handler):
    """
    Custom logging handler to redirect logs to a QTextEdit widget.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        """
        Emit a record.

        Args:
            record (logging.LogRecord): The LogRecord to be emitted.
        """
        log_message = self.format(record)
        self.text_widget.append(log_message)

class GitSleuthGUI(QMainWindow):
    """
    Main class for the GitSleuth GUI application.
    """
    def __init__(self):
        """
        Initialize the GitSleuth GUI application.
        """
        super(GitSleuthGUI, self).__init__()
        self.search_active = False
        self.initUI()

    def initUI(self):
        """
        Initialize the User Interface.
        """
        self.setWindowTitle("GitSleuth")

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Tab widget setup
        tab_widget = QTabWidget(self)
        search_results_tab = QWidget()
        log_tab = QWidget()
        groups_editor_tab = QWidget()

        tab_widget.addTab(search_results_tab, "Search Results")
        tab_widget.addTab(log_tab, "Log")
        tab_widget.addTab(groups_editor_tab, "Search Editor")

        main_layout.addWidget(tab_widget)

        # Setup for the search results tab
        search_results_layout = QVBoxLayout(search_results_tab)
        input_layout = QHBoxLayout()
        self.setupSearchInputArea(input_layout)
        search_results_layout.addLayout(input_layout)
        self.setupResultsTable(search_results_layout)

        # Status bar and progress bar setup
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        search_results_layout.addWidget(self.progress_bar)

        # Log tab setup
        log_tab_layout = QVBoxLayout(log_tab)
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        log_handler = QTextEditHandler(self.log_output)
        logging.root.addHandler(log_handler)
        log_tab_layout.addWidget(self.log_output)

        # Create a button to clear the log
        self.clear_log_button = QPushButton("Clear Log", self)
        self.clear_log_button.clicked.connect(self.clear_log)
        log_tab_layout.addWidget(self.clear_log_button)

        # Create a button to clear the search results
        self.clear_results_button = QPushButton("Clear Results", self)
        self.clear_results_button.clicked.connect(self.clear_results)
        self.clear_results_button.setEnabled(False)  # Set it to initially disabled
        search_results_layout.addWidget(self.clear_results_button)

        # Groups editor tab setup
        groups_editor_layout = QVBoxLayout(groups_editor_tab)
        self.groups_editor = QTextEdit(self)
        self.load_groups_file()
        groups_editor_layout.addWidget(self.groups_editor)
        self.setupGroupEditor(groups_editor_layout)

        # Geometry setup
        self.setGeometry(300, 300, 1000, 600)

    def setupSearchInputArea(self, layout):
        """
        Sets up the search input area in the GUI.
    
        Args:
            layout (QHBoxLayout): The layout to add the search input area to.
        """
        # Add a QComboBox for domain selection
        self.domain_dropdown = QComboBox(self)
        layout.addWidget(QLabel("Domain:"))
        layout.addWidget(self.domain_dropdown)
        # Populate the dropdown with sample domains
        self.domain_dropdown.addItems(["temp.com", "example.com", "temp.com"])    
        self.search_group_dropdown = QComboBox(self)
        layout.addWidget(self.search_group_dropdown)
        self.search_group_dropdown.addItems(["Authentication and Credentials", "API Keys and Tokens",
                                                 "Database and Server Configurations", "Security and Code Vulnerabilities",
                                                 "Historical Data and Leakage", "Custom and Regex-Based Searches"])

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.on_search)
        layout.addWidget(self.search_button)
    
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
    
        # Adding a Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)  # Connects to the close method of the window
        layout.addWidget(self.quit_button)


    def setupResultsTable(self, layout):
        """
        Sets up the results table in the GUI.

        Args:
            layout (QVBoxLayout): The layout to add the results table to.
        """
        self.results_table = QTableWidget(0, 4)  # Set column count to 4
        self.results_table.setHorizontalHeaderLabels(["Search Term", "Repository", "File Path", "Snippets"])
        layout.addWidget(self.results_table)
        self.results_table.setColumnWidth(0, 200)
        self.results_table.setColumnWidth(1, 200)
        self.results_table.setColumnWidth(2, 300)
        self.results_table.setColumnWidth(3, 300)

        # Create a button to export results to CSV
        self.export_button = QPushButton("Export to CSV", self)
        self.export_button.clicked.connect(self.export_results_to_csv)
        self.export_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.export_button)


    def setupGroupEditor(self, layout):
        """
        Sets up the groups editor tab in the GUI.

        Args:
            layout (QVBoxLayout): The layout to add the groups editor to.
        """
        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu('Settings')
        manage_tokens_action = QAction('Manage Tokens', self)
        manage_tokens_action.triggered.connect(self.open_token_management)
        settings_menu.addAction(manage_tokens_action)

        save_button = QPushButton("Save Searches", self)
        save_button.clicked.connect(self.save_groups_file)
        layout.addWidget(save_button)
    
    # Function definitions within GitSleuthGUI class
    def clear_log(self):
        """
        Clears the log text in the log tab.
        """
        self.log_output.clear()
    
    def clear_results(self):
        """
        Clears the content of the search results table.
        """
        self.results_table.setRowCount(0)
        # Disable the export button after clearing results
        self.export_button.setEnabled(False)
        # Update the enabled state of the clear_results_button
        self.clear_results_button.setEnabled(False)

    def stop_search(self):
        """
        Stops the ongoing search.
        """
        self.search_active = False
        logging.info("Search stopped by user.")
        self.stop_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Search stopped.")
        self.check_enable_export()
    def export_results_to_csv(self):
        """
        Exports the search results displayed in the table to a CSV file.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if filename:
            self.write_results_to_csv(filename)

    def write_results_to_csv(self, filename):
        """
        Writes the search results to a CSV file.

        Args:
            filename (str): Name of the CSV file to write to.
        """
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Search Term", "Repository", "File Path", "Snippet"])
                for row in range(self.results_table.rowCount()):
                    search_term = self.results_table.item(row, 0).text()
                    repo_widget = self.results_table.cellWidget(row, 1)
                    repo_text = repo_widget.text() if repo_widget else ""
                    file_widget = self.results_table.cellWidget(row, 2)
                    file_text = file_widget.text() if file_widget else ""
                    snippet_item = self.results_table.item(row, 3)
                    snippet_text = snippet_item.text().replace('\n', ' ') if snippet_item else ""
                    writer.writerow([search_term, repo_text, file_text, snippet_text])
            self.status_bar.showMessage("Results exported successfully to " + filename)
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            self.status_bar.showMessage("Error exporting results.")

    def load_groups_file(self):
        """
        Loads the search groups from the file into the groups editor.
        """
        try:
            with open('GitSleuth_Groups.py', 'r') as file:
                self.groups_editor.setText(file.read())
        except Exception as e:
            logging.error(f"Failed to load Groups file: {e}")

    def save_groups_file(self):
        """
        Saves the modified search groups from the groups editor into the file.
        """
        try:
            with open('GitSleuth_Groups.py', 'w') as file:
                file.write(self.groups_editor.toPlainText())
            logging.info("Groups file saved successfully.")
            self.status_bar.showMessage("Groups file saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save Groups file: {e}")
            self.status_bar.showMessage("Error saving Groups file.")

    def open_token_management(self):
        """
        Opens the token management dialog.
        """
        self.token_management_dialog = TokenManagementDialog(self)
        self.token_management_dialog.show()

    def on_search(self):
        """
        Handles the event when the search button is clicked.
        """
        # Use the current text of the domain dropdown
        domain = self.domain_dropdown.currentText()
        if not domain:
            self.statusBar().showMessage("Domain is required for searching.")
            return

        selected_group = self.search_group_dropdown.currentText()

        self.clear_results()
        self.results_table.update()  # Force update of the results table

        self.search_active = True
        self.statusBar().showMessage(f"Searching in {selected_group} for domain: {domain}")
        self.stop_button.setEnabled(True)  # Uncomment if stop functionality is desired
        self.search_button.setEnabled(False)
        self.export_button.setEnabled(False)  # Explicitly disable the export button
        self.progress_bar.setValue(0)
        self.perform_search(domain, selected_group)
 
    def perform_search(self, domain, selected_group):
        config = load_config()
        search_groups = create_search_queries(domain)
        max_retries = 3

        if selected_group == "Search All":
            groups = search_groups.keys()
        else:
            groups = [selected_group]

        for group in groups:
            queries = search_groups.get(group, [])
            for query in queries:
                self.process_query(query, max_retries, config, query)


    def check_enable_export(self):
        if self.results_table.rowCount() > 0:
            self.export_button.setEnabled(True)
        else:
            self.export_button.setEnabled(False)

    def process_query(self, query, max_retries, config, search_term):
        retry_count = 0
        while retry_count < max_retries:
            try:
                headers = get_headers(config)
                search_results = GitSleuth_API.search_github_code(query, headers)
                self.handle_search_results(search_results, query, headers, search_term)
                break
            except RateLimitException as e:
                logging.warning(f"Rate limit reached for token. {str(e)}")
                time.sleep(60)  # Delay for 60 seconds before retrying
                if retry_count < max_retries - 1:
                    if switch_token(config):
                        logging.info("Switched to a new token.")
                    else:
                        logging.error("All tokens exhausted. Unable to proceed with the search.")
                        break
                retry_count += 1
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break


    def handle_search_results(self, search_results, query, headers, search_term):
        if search_results and 'items' in search_results:
            for item in search_results['items']:
                self.process_search_item(item, query, headers, search_term)

    def process_search_item(self, item, query, headers, search_term):
        repo_name = item['repository']['full_name']
        file_path = item.get('path', '')
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
        if file_contents:
            snippets = extract_snippets(file_contents, query)
            self.update_results_table(repo_name, file_path, snippets, search_term)
    def create_clickable_link(self, text, url):
        link_label = QLabel()
        link_label.setText(f'<a href="{url}">{text}</a>')
        link_label.setOpenExternalLinks(True)
        return link_label
    
    def update_results_table(self, repo_name, file_path, snippets, search_term):
        github_base_url = "https://github.com/"
        for snippet in snippets:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            # Filter out unwanted terms from the search term
            filtered_search_term = search_term.replace("ge.com NOT example NOT dummy NOT test NOT sample NOT placeholder", "").strip()

            # Search term column
            self.results_table.setItem(row_position, 0, QTableWidgetItem(filtered_search_term))

            # Repository column with clickable link
            repo_url = f"{github_base_url}{repo_name}"
            repo_link_label = self.create_clickable_link(repo_name, repo_url)
            self.results_table.setCellWidget(row_position, 1, repo_link_label)

            # File path column with clickable link
            file_url = f"{repo_url}/blob/main/{file_path}"
            file_link_label = self.create_clickable_link(file_path, file_url)
            self.results_table.setCellWidget(row_position, 2, file_link_label)

            # Snippets column
            self.results_table.setItem(row_position, 3, QTableWidgetItem(snippet))

        # Enable export button if there are results
        if self.results_table.rowCount() > 0:
            self.export_button.setEnabled(True)
            self.clear_results_button.setEnabled(True)  # Enable the clear results button
            self.stop_button.setEnabled(False)
            self.status_bar.showMessage("Results found.")
            logging.info("Results found.")

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
