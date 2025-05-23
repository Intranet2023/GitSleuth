#GitSleuth_GUI.py
import sys
import os
import json
import csv
import time
import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QStatusBar,
    QProgressBar,
    QFileDialog,
    QTextEdit,
    QTabWidget,
    QAction,
    QDialog,
    QSpinBox,
    QDialogButtonBox,
    QHeaderView,
)
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QDesktopServices, QPalette, QColor

import GitSleuth_API
from GitSleuth_Groups import create_search_queries, get_query_description
from GitSleuth import extract_snippets, switch_token
from GitSleuth_API import RateLimitException, get_headers, check_rate_limit
from OAuth_Manager import oauth_login
# Token management imports are kept for future use
from Token_Manager import load_tokens, add_token, delete_token

CONFIG_FILE = 'config.json'


def apply_dark_palette(app):
    """Apply a dark palette for a sleeker appearance."""
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)


def load_config():
    """Load configuration from 'config.json'."""
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        config = {}

    logging.debug("Config loaded")
    return config


def save_config(cfg):
    """Save configuration to CONFIG_FILE."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(cfg, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving configuration: {e}")

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
        self.session_keep_alive = config.get("SESSION_KEEP_ALIVE_MINUTES", 0)
        self.exit_timer: Optional[QTimer] = None
        self.initUI()
        self.restore_oauth_session()

    def initUI(self):
        """
        Initialize the User Interface.
        """
        self.setWindowTitle("GitSleuth")

        # Menu bar with Settings action
        menu_bar = self.menuBar()
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menu_bar.addAction(settings_action)

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Tab widget setup
        tab_widget = QTabWidget(self)
        search_results_tab = QWidget()
        log_tab = QWidget()
        tab_widget.addTab(search_results_tab, "Search Results")
        tab_widget.addTab(log_tab, "Log")

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

        # Geometry setup
        # Expand the default window size for better spacing
        self.setGeometry(200, 150, 1200, 750)

    def setupSearchInputArea(self, layout):
        """Build the search input widgets and action buttons."""


        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Keywords:"))
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keywords or domain")
        # Give the keyword field a minimum width so longer terms are visible
        self.keyword_input.setMinimumWidth(250)
        form_layout.addWidget(self.keyword_input)


        self.search_group_dropdown = QComboBox(self)
        self.search_group_dropdown.addItems([
            "Authentication and Credentials",
            "API Keys and Tokens",
            "Database and Server Configurations",
            "Security and Code Vulnerabilities",
            "Historical Data and Leakage",
            "Custom and Regex-Based Searches",
        ])
        # Ensure the dropdown is wide enough for the longest entry
        self.search_group_dropdown.setMinimumWidth(300)
        form_layout.addWidget(self.search_group_dropdown)
        layout.addLayout(form_layout)
        button_layout = QHBoxLayout()

        self.search_button = QPushButton("Search", self)
        # Slightly wider buttons for clarity
        self.search_button.setFixedWidth(110)
        self.search_button.clicked.connect(self.on_search)
        layout.addWidget(self.search_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setFixedWidth(110)
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.oauth_button = QPushButton("OAuth Login", self)

        # Allow room for "Logged in as" text after authentication
        self.oauth_button.setFixedWidth(180)
        self.oauth_button.clicked.connect(self.start_oauth)
        button_layout.addWidget(self.oauth_button)


        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setFixedWidth(120)
        self.logout_button.clicked.connect(self.logout_user)
        button_layout.addWidget(self.logout_button)


        self.quit_button = QPushButton("Quit", self)
        self.quit_button.setFixedWidth(100)
        self.quit_button.clicked.connect(self.force_quit)
        button_layout.addWidget(self.quit_button)

        layout.addLayout(button_layout)




    def setupResultsTable(self, layout):
        """
        Sets up the results table in the GUI.

        Args:
            layout (QVBoxLayout): The layout to add the results table to.
        """

        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels([
            "Search Term",
            "Description",
            "Repository",
            "File Path",
            "Snippets",
        ])
        layout.addWidget(self.results_table)
        self.results_table.setColumnWidth(0, 180)
        self.results_table.setColumnWidth(1, 220)
        self.results_table.setColumnWidth(2, 180)
        self.results_table.setColumnWidth(3, 250)
        self.results_table.setColumnWidth(4, 300)
        # Stretch the snippets column to use remaining space
        self.results_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Stretch
        )

        # Create a button to export results to CSV
        self.export_button = QPushButton("Export to CSV", self)
        self.export_button.clicked.connect(self.export_results_to_csv)
        self.export_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.export_button)


    def clear_log(self):
        """
        Clears the log text in the log tab.
        """
        self.log_output.clear()

    def open_settings(self):
        """Display the settings dialog and persist choices."""
        dlg = SettingsDialog(self.session_keep_alive, self)
        if dlg.exec_() == QDialog.Accepted:
            self.session_keep_alive = dlg.get_duration()
            config["SESSION_KEEP_ALIVE_MINUTES"] = self.session_keep_alive
            save_config(config)

    def start_oauth(self):
        """Trigger OAuth device flow and update UI."""

        token, username = oauth_login()
        if token:
            os.environ["GITHUB_OAUTH_TOKEN"] = token
            if username:
                config["SAVED_USERNAME"] = username
                save_config(config)
            if hasattr(self, "oauth_btn") and username:
                self.oauth_btn.setText(f"Logged in as: {username}")
            self.status_bar.showMessage("OAuth login successful")

            if username:
                self.oauth_button.setText(f"Logged in as: {username}")
                config["SAVED_USERNAME"] = username
                save_config(config)

        else:
            self.status_bar.showMessage("OAuth login failed")

    def logout_user(self):
        """Clear stored OAuth credentials and update the UI."""
        delete_token("oauth_token")
        os.environ.pop("GITHUB_OAUTH_TOKEN", None)
        config["SAVED_USERNAME"] = ""
        save_config(config)
        self.oauth_button.setText("OAuth Login")
        self.status_bar.showMessage("Logged out")

    def restore_oauth_session(self):
        """Restore OAuth session from saved token if available."""
        tokens = load_tokens()
        token = tokens.get("oauth_token")
        saved_user = config.get("SAVED_USERNAME")
        if token:
            os.environ["GITHUB_OAUTH_TOKEN"] = token
            if saved_user:
                self.oauth_button.setText(f"Logged in as: {saved_user}")
            return True
        return False

    
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
        QApplication.processEvents()  # Ensure UI updates after stopping
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
                writer.writerow([
                    "Search Term",
                    "Description",
                    "Repository",
                    "File Path",
                    "Snippet",
                ])
                for row in range(self.results_table.rowCount()):
                    search_term = self.results_table.item(row, 0).text()
                    description = self.results_table.item(row, 1).text()
                    repo_widget = self.results_table.cellWidget(row, 2)
                    repo_text = repo_widget.text() if repo_widget else ""
                    file_widget = self.results_table.cellWidget(row, 3)
                    file_text = file_widget.text() if file_widget else ""
                    snippet_item = self.results_table.item(row, 3)
                    snippet_text = snippet_item.text().replace("\n", " ") if snippet_item else ""
                    desc_item = self.results_table.item(row, 4)
                    desc_text = desc_item.text() if desc_item else ""
                    writer.writerow([search_term, repo_text, file_text, snippet_text, desc_text])

            self.status_bar.showMessage("Results exported successfully to " + filename)
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            self.status_bar.showMessage("Error exporting results.")



    def on_search(self):
        """
        Handles the event when the search button is clicked.
        """
        # Use the entered keywords for filtering
        keywords = self.keyword_input.text().strip()
        selected_group = self.search_group_dropdown.currentText()

        self.clear_results()
        self.results_table.update()  # Force update of the results table

        self.search_active = True
        if keywords:
            self.statusBar().showMessage(
                f"Searching in {selected_group} for keywords: {keywords}"
            )
        else:
            self.statusBar().showMessage(
                f"Searching in {selected_group} with no keywords"
            )
        self.stop_button.setEnabled(True)  # Allow user to stop the search
        self.search_button.setEnabled(False)
        self.export_button.setEnabled(False)  # Explicitly disable the export button
        self.progress_bar.setValue(0)
        QApplication.processEvents()  # Refresh UI state before starting search
        self.perform_search(keywords, selected_group)

    def perform_search(self, keywords, selected_group):
        config = load_config()
        search_groups = create_search_queries(keywords)
        max_retries = 3

        if selected_group == "Search All":
            groups = search_groups.keys()
        else:
            groups = [selected_group]

        self.total_queries = sum(len(search_groups.get(g, [])) for g in groups)
        self.progress_bar.setMaximum(self.total_queries)
        self.completed_queries = 0
        QApplication.processEvents()

        for group in groups:
            queries = search_groups.get(group, [])
            for query, description in queries:
                if not self.search_active:
                    return

                description = get_query_description(query, keywords)
                self.process_query(query, max_retries, config, query, description)
                self.completed_queries += 1
                self.progress_bar.setValue(self.completed_queries)
                QApplication.processEvents()

        # Search finished normally
        if self.search_active:
            self.search_active = False
            self.search_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.check_enable_export()
            self.status_bar.showMessage("Search completed.")
            QApplication.processEvents()  # Reflect updated button states



    def check_enable_export(self):
        if self.results_table.rowCount() > 0:
            self.export_button.setEnabled(True)
        else:
            self.export_button.setEnabled(False)

    def wait_with_events(self, wait_time):
        """Sleep in small intervals while processing GUI events.

        While waiting due to hitting the API rate limit, the status bar is
        updated to inform the user and then restored to its previous text when
        the wait is over.
        """
        previous_message = self.status_bar.currentMessage()
        end_time = time.time() + wait_time

        # Display rate limit pause message and keep UI responsive
        while time.time() < end_time:
            if not self.search_active:
                break
            remaining = int(end_time - time.time())
            self.status_bar.showMessage(
                f"Paused due to rate limiting. Resuming in {remaining}s"
            )
            QApplication.processEvents()
            time.sleep(1)

        # Restore previous status if search is still active
        if self.search_active:
            self.status_bar.showMessage(previous_message)

    def process_query(self, query, max_retries, config, search_term, description):
        retry_count = 0
        while retry_count < max_retries and self.search_active:
            try:
                headers = get_headers()
                remaining, wait_time = check_rate_limit(headers)
                if remaining == 0:
                    logging.warning("Rate limit exhausted before request.")
                    if switch_token(config):
                        headers = get_headers()
                    else:
                        self.wait_with_events(wait_time or 60)
                if not self.search_active:
                    break
                search_results = GitSleuth_API.search_github_code(query, headers)
                if not self.search_active:
                    break
                self.handle_search_results(search_results, query, description, headers, search_term)
                break
            except RateLimitException as e:
                logging.warning(f"Rate limit reached for token. {str(e)}")
                if retry_count < max_retries - 1 and switch_token(config):
                    logging.info("Switched to a new token.")
                else:
                    wait_time = getattr(e, 'wait_time', 60)
                    logging.info(f"Waiting {int(wait_time)} seconds for rate limit reset.")
                    self.wait_with_events(wait_time)

                logging.warning(f"Rate limit reached: {str(e)}")
                
                retry_count += 1
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break


    def handle_search_results(self, search_results, query, description, headers, search_term):
        if self.search_active and search_results and 'items' in search_results:
            for item in search_results['items']:
                if not self.search_active:
                    break
                self.process_search_item(item, query, description, headers, search_term)

    def process_search_item(self, item, query, description, headers, search_term):

        if not self.search_active:
            return
        repo_name = item['repository']['full_name']
        # Update the status bar with the repository currently being processed
        self.status_bar.showMessage(f"Processing {repo_name}")
        QApplication.processEvents()
        file_path = item.get('path', '')
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
        if file_contents:
            snippets = extract_snippets(file_contents, query)
            self.update_results_table(repo_name, file_path, snippets, search_term, description)
    def create_clickable_link(self, text, url):
        link_label = QLabel()
        link_label.setText(f'<a href="{url}">{text}</a>')
        link_label.setOpenExternalLinks(True)
        return link_label
    
    def update_results_table(self, repo_name, file_path, snippets, search_term, description):
        if not self.search_active:
            return
        github_base_url = "https://github.com/"
        for snippet in snippets:
            if not self.search_active:
                break
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            # Filter out unwanted terms from the search term
            filtered_search_term = search_term.replace("ge.com NOT example NOT dummy NOT test NOT sample NOT placeholder", "").strip()

            # Search term column
            self.results_table.setItem(row_position, 0, QTableWidgetItem(filtered_search_term))
            # Description column
            self.results_table.setItem(row_position, 1, QTableWidgetItem(description))

            # Repository column with clickable link
            repo_url = f"{github_base_url}{repo_name}"
            repo_link_label = self.create_clickable_link(repo_name, repo_url)
            self.results_table.setCellWidget(row_position, 2, repo_link_label)

            # File path column with clickable link
            file_url = f"{repo_url}/blob/main/{file_path}"
            file_link_label = self.create_clickable_link(file_path, file_url)
            self.results_table.setCellWidget(row_position, 3, file_link_label)

            # Snippets column
            self.results_table.setItem(row_position, 4, QTableWidgetItem(snippet))
        # Enable export button if there are results
        if self.results_table.rowCount() > 0:
            self.export_button.setEnabled(True)
            self.clear_results_button.setEnabled(True)  # Enable the clear results button
            self.status_bar.showMessage("Results found.")
            logging.info("Results found.")


    def closeEvent(self, event):
        if self.session_keep_alive and self.session_keep_alive > 0:
            event.ignore()
            self.hide()
            if not self.exit_timer:
                self.status_bar.showMessage(
                    f"Continuing session for {self.session_keep_alive} minutes."
                )
                self.exit_timer = QTimer(self)
                self.exit_timer.setSingleShot(True)
                self.exit_timer.timeout.connect(QApplication.quit)
                self.exit_timer.start(self.session_keep_alive * 60 * 1000)
        else:
            event.accept()

    def force_quit(self):
        """Exit the application immediately, ignoring any keep-alive timer."""
        if self.exit_timer:
            self.exit_timer.stop()
            self.exit_timer = None
        QApplication.quit()


class SettingsDialog(QDialog):
    """Dialog for basic application settings."""

    def __init__(self, current_minutes: int, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Keep session active after closing (0 = None):"))

        self.duration_spin = QSpinBox(self)
        self.duration_spin.setRange(0, 600)
        self.duration_spin.setSingleStep(30)
        self.duration_spin.setValue(current_minutes)
        self.duration_spin.setSuffix(" min")
        layout.addWidget(self.duration_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_duration(self) -> int:
        return int(self.duration_spin.value())


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
        # Provide more space for token information
        self.setGeometry(100, 100, 500, 350)
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

        self.oauth_btn = QPushButton('OAuth Login')
        # Wider button so "Logged in as" text fits comfortably
        self.oauth_btn.setFixedWidth(180)
        self.oauth_btn.clicked.connect(self.start_oauth)

        btn_layout.addWidget(self.oauth_btn)

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

    def start_oauth(self):
        """Initiate OAuth login and refresh the token table."""

        result = oauth_login()
        if result:
            token, username = result
            os.environ["GITHUB_OAUTH_TOKEN"] = token
            if username:
                config["SAVED_USERNAME"] = username
                save_config(config)
                self.oauth_btn.setText(f"Logged in as: {username}")
                config["SAVED_USERNAME"] = username
                save_config(config)
        self.load_tokens()

def main():
    """
    Main function to run the GitSleuth application.
    """
    app = QApplication(sys.argv)
    apply_dark_palette(app)
    ex = GitSleuthGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
