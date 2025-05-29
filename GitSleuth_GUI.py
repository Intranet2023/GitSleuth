#GitSleuth_GUI.py
import sys
import os
import json
import csv
import time
import logging
import re
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
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
    QInputDialog,
    QToolBar,
    QStyle,
    QCheckBox,
)
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QDesktopServices, QPalette, QColor

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np
from scipy.sparse import hstack, csr_matrix


import GitSleuth_API
from GitSleuth_Groups import (
    create_search_queries,
    get_query_description,
    PLACEHOLDERS,
)
from GitSleuth import (
    extract_snippets,
    switch_token,
    _path_is_ignored,
    _shannon_entropy,
    extract_search_terms,
    get_secret_entropy,
    PRECEDING_KEYWORDS,
)
from GitSleuth_API import RateLimitException, get_headers, check_rate_limit
from OAuth_Manager import oauth_login, fetch_username
# Token management imports are kept for future use
from Token_Manager import load_tokens, add_token, delete_token

CONFIG_FILE = 'config.json'
HIGH_ENTROPY_THRESHOLD = 4.0



def apply_dark_palette(app):
    """Apply a dark palette for a sleeker appearance."""
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
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
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

CONFIG_EXTS = {'.json', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.toml', '.env'}
SOURCE_EXTS = {
    '.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cpp', '.c', '.cs', '.swift'
}
LOG_EXTS = {'.log', '.out', '.txt'}


def _file_type_features(file_path: str) -> list[int]:
    """Return one-hot encoded file type features.

    Parameters
    ----------
    file_path : str
        Path to the file. May be empty or ``None``.
    """

    if not isinstance(file_path, str):
        file_path = ""

    ext = os.path.splitext(file_path)[1].lower()
    is_config = int(ext in CONFIG_EXTS or "config" in file_path.lower())
    is_source = int(ext in SOURCE_EXTS or "/src/" in file_path.lower())
    is_log = int(ext in LOG_EXTS or "log" in file_path.lower())
    is_other = int(not (is_config or is_source or is_log))
    return [is_config, is_source, is_log, is_other]


def _structural_features(snippet: str) -> list[int]:
    """Return simple structural features for a snippet."""
    assignment = int(bool(re.search(r"\b\w+\s*[:=]\s*\S+", snippet)))
    func_arg = int(
        bool(re.search(r"set(pass(word|phrase)?|password|token|key|secret)\s*\(", snippet, re.I))
    )
    return [assignment, func_arg]

def compute_features(text: str, file_path: str = "") -> list[float]:
    """Return entropy, composition and contextual features for a snippet."""

    if not isinstance(text, str):
        text = "" if text is None else str(text)

    if not isinstance(file_path, str):
        file_path = ""

    length = len(text)
    if length == 0:
        base = [0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        numeric = sum(ch.isdigit() for ch in text)
        alpha = sum(ch.isalpha() for ch in text)
        special = length - numeric - alpha
        entropy = _shannon_entropy(text)
        base = [entropy, float(length), numeric / length, alpha / length, special / length]

    return base + _file_type_features(file_path) + _structural_features(text)


def highlight_terms_html(text: str, query: str) -> str:
    """Return HTML text with search terms highlighted in blue and secrets in red."""
    # Highlight secrets first
    def _highlight_secret(match: re.Match) -> str:
        secret = match.group(1)
        highlighted = f'<b><span style="color:red">{secret}</span></b>'
        return match.group(0).replace(secret, highlighted)

    secret_pattern = re.compile(
        r'(?:' + '|'.join(re.escape(k) for k in PRECEDING_KEYWORDS) + r')\s*[=:]\s*[\'\"]?([^\'\"\s,;]+)[\'\"]?',
        re.IGNORECASE,
    )
    text = secret_pattern.sub(_highlight_secret, text)

    # Then highlight search terms
    terms = extract_search_terms(query)
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(
            lambda m: f'<span style="color:blue">{m.group(0)}</span>',
            text,
        )
    return text

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
        self.filter_placeholders = config.get("FILTER_PLACEHOLDERS", True)
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

        # Toolbar for commonly used actions
        toolbar = QToolBar("Tools", self)
        self.addToolBar(toolbar)

        self.clear_results_action = QAction(
            self.style().standardIcon(QStyle.SP_DialogResetButton),
            "Clear Results",
            self,
        )
        self.clear_results_action.setToolTip("Clear the search results")
        self.clear_results_action.triggered.connect(self.clear_results)
        self.clear_results_action.setEnabled(False)
        toolbar.addAction(self.clear_results_action)

        self.clear_log_action = QAction(
            self.style().standardIcon(QStyle.SP_TrashIcon),
            "Clear Log",
            self,
        )
        self.clear_log_action.setToolTip("Clear the log output")
        self.clear_log_action.triggered.connect(self.clear_log)
        toolbar.addAction(self.clear_log_action)

        self.export_action = QAction(
            self.style().standardIcon(QStyle.SP_FileIcon),
            "Export to CSV",
            self,
        )
        self.export_action.setToolTip("Export results to CSV")
        self.export_action.triggered.connect(self.export_results_to_csv)
        self.export_action.setEnabled(False)
        toolbar.addAction(self.export_action)

        self.export_labels_action = QAction(
            self.style().standardIcon(QStyle.SP_DialogSaveButton),
            "Export Labels",
            self,
        )
        self.export_labels_action.setToolTip("Export label data")
        self.export_labels_action.triggered.connect(self.export_labels_to_csv)
        self.export_labels_action.setEnabled(False)
        toolbar.addAction(self.export_labels_action)

        self.high_entropy_checkbox = QCheckBox("Hide Low Entropy Results", self)
        self.high_entropy_checkbox.setToolTip(

            "Hide results with entropy scores at or below the threshold"

        )
        self.high_entropy_checkbox.stateChanged.connect(self.apply_entropy_filter)
        toolbar.addWidget(self.high_entropy_checkbox)

        # Add search input widgets to the toolbar
        self.setupSearchInputArea(toolbar)

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Tab widget setup

        tab_widget = QTabWidget(self)
        self.tab_widget = tab_widget
        search_results_tab = QWidget()
        ml_tab = QWidget()
        log_tab = QWidget()
        tab_widget.addTab(search_results_tab, "Search Results")
        self.ml_tab_index = tab_widget.addTab(ml_tab, "ML")
        tab_widget.addTab(log_tab, "Log")

        main_layout.addWidget(self.tab_widget)

        # Setup for the search results tab
        search_results_layout = QVBoxLayout(search_results_tab)
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


        # Actions now provided in the toolbar

        # ML tab setup
        ml_tab_layout = QVBoxLayout(ml_tab)
        self.ml_output = QTextEdit(self)
        self.ml_output.setReadOnly(True)
        ml_tab_layout.addWidget(self.ml_output)

        self.train_button = QPushButton("Perform Machine Learning", self)
        self.train_button.setToolTip("Train the machine learning model")
        self.train_button.clicked.connect(self.train_model)
        ml_tab_layout.addWidget(self.train_button)

        self.load_labeled_data()

        # Geometry setup
        # Expand the default window size to accommodate larger snippets
        self.setGeometry(200, 150, 1600, 900)

    def setupSearchInputArea(self, layout):
        """Build the search input widgets and action buttons."""

        # Determine whether adding to a toolbar or a layout
        is_toolbar = isinstance(layout, QToolBar)
        def add(item):
            if is_toolbar:
                layout.addWidget(item)
            else:
                layout.addWidget(item)

        if is_toolbar:
            add(QLabel("Keywords:"))
        else:
            form_layout = QHBoxLayout()
            form_layout.addWidget(QLabel("Keywords:"))
            layout.addLayout(form_layout)
            add = form_layout.addWidget

        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keywords or domain")
        self.keyword_input.setMinimumWidth(250)
        add(self.keyword_input)

        if not is_toolbar:
            button_layout = QHBoxLayout()
            layout.addLayout(button_layout)
            add = button_layout.addWidget

        self.search_group_dropdown = QComboBox(self)
        self.search_group_dropdown.setToolTip(
            "Choose the category of secrets to search for"
        )
        add(self.search_group_dropdown)
        self.search_group_dropdown.addItems([
            "Cloud Credentials (AWS, Azure, GCP)",
            "Third-Party API Keys and Tokens",
            "OAuth Credentials",
            "Database Credentials & Connection Strings",
            "SSH Keys and Certificates",
            "Email/SMTP Credentials",
            "JWT and Application Secrets",
            "Secrets in Infrastructure-as-Code",
            "Secrets in CI/CD Configurations",
            "Secrets in Commit History, Issues, or Gists",
            "Hardcoded Passwords or Bearer Tokens",
            "Internationalized Secret Keywords",
            "General Configuration & Credential Files",
            "Search All",
        ])

        self.search_button = QPushButton("Search", self)
        self.search_button.setFixedWidth(110)
        self.search_button.setToolTip("Start the search")
        self.search_button.clicked.connect(self.on_search)
        add(self.search_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setFixedWidth(110)
        self.stop_button.setToolTip("Stop the ongoing search")
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        add(self.stop_button)

        self.oauth_button = QPushButton("OAuth Login", self)
        self.oauth_button.setFixedWidth(180)
        self.oauth_button.setToolTip("Authenticate using OAuth")
        self.oauth_button.clicked.connect(self.start_oauth)
        add(self.oauth_button)

        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setFixedWidth(120)
        self.logout_button.setToolTip("Clear OAuth credentials")
        self.logout_button.clicked.connect(self.logout_user)
        add(self.logout_button)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.setFixedWidth(100)
        self.quit_button.setToolTip("Exit the application")
        self.quit_button.clicked.connect(self.force_quit)
        add(self.quit_button)

        self.high_entropy_checkbox = QCheckBox("Hide Low Entropy Results", self)
        self.high_entropy_checkbox.setToolTip(
            "Hide results with entropy 3.5 or lower and disable ML features"
        )
        self.high_entropy_checkbox.stateChanged.connect(self.apply_entropy_filter)
        add(self.high_entropy_checkbox)




    def setupResultsTable(self, layout):
        """
        Sets up the results table in the GUI.

        Args:
            layout (QVBoxLayout): The layout to add the results table to.
        """

        self.results_table = QTableWidget(0, 7)
        self.results_table.setHorizontalHeaderLabels([
            "Search Term",
            "Description",
            "Repository",
            "File Path",
            "Snippets",
            "Entropy",
            "Label",
        ])
        self.results_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        layout.addWidget(self.results_table)
        self.results_table.setColumnWidth(0, 180)
        self.results_table.setColumnWidth(1, 220)
        self.results_table.setColumnWidth(2, 180)
        self.results_table.setColumnWidth(3, 250)
        # Provide a wider column to display longer snippets
        self.results_table.setColumnWidth(4, 450)
        self.results_table.setColumnWidth(5, 90)
        self.results_table.setColumnWidth(6, 120)
        # Stretch the snippets column to use remaining space
        self.results_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Stretch
        )

        self.results_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )


        # Export actions now available via toolbar


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
            username = fetch_username(token)
            if username:
                os.environ["GITHUB_OAUTH_TOKEN"] = token
                if saved_user:
                    self.oauth_button.setText(f"Logged in as: {saved_user}")
                else:
                    self.oauth_button.setText(f"Logged in as: {username}")
                    config["SAVED_USERNAME"] = username
                    save_config(config)
                return True
            else:
                delete_token("oauth_token")
                os.environ.pop("GITHUB_OAUTH_TOKEN", None)
                config["SAVED_USERNAME"] = ""
                save_config(config)
        return False


    
    def clear_results(self):
        """
        Clears the content of the search results table.
        """
        self.results_table.setRowCount(0)
        # Disable the export actions after clearing results
        self.export_action.setEnabled(False)
        self.export_labels_action.setEnabled(False)
        self.clear_results_action.setEnabled(False)

    def stop_search(self):
        """
        Stops the ongoing search.
        """
        self.search_active = False
        logging.info("Search stopped by user.")
        self.stop_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.progress_bar.setValue(0)
        results = self.results_table.rowCount()
        self.status_bar.showMessage(f"Search stopped. {results} results so far.")
        logging.info(f"Search stopped with {results} results.")
        self.check_enable_export()
        QApplication.processEvents()  # Ensure UI updates after stopping

    def apply_entropy_filter(self):
        """Hide low entropy rows and toggle ML features."""
        checked = self.high_entropy_checkbox.isChecked()
        self.train_button.setEnabled(not checked)
        self.tab_widget.setTabEnabled(self.ml_tab_index, not checked)
        for row in range(self.results_table.rowCount()):
            entropy_item = self.results_table.item(row, 5)
            text = entropy_item.text() if entropy_item else ""
            try:
                score = float(text)
            except ValueError:
                score = None
            hide = checked and (score is None or score < HIGH_ENTROPY_THRESHOLD)
            self.results_table.setRowHidden(row, hide)
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
                    "Entropy",
                ])
                for row in range(self.results_table.rowCount()):
                    search_term = self.results_table.item(row, 0).text()
                    description_item = self.results_table.item(row, 1)
                    description = description_item.text() if description_item else ""
                    repo_widget = self.results_table.cellWidget(row, 2)
                    repo_text = repo_widget.text() if repo_widget else ""
                    file_widget = self.results_table.cellWidget(row, 3)
                    file_text = file_widget.text() if file_widget else ""
                    snippet_item = self.results_table.item(row, 4)
                    snippet_text = (
                        snippet_item.text().replace("\n", " ") if snippet_item else ""
                    )
                    entropy_item = self.results_table.item(row, 5)
                    entropy_text = entropy_item.text() if entropy_item else ""
                    writer.writerow([
                        search_term,
                        description,
                        repo_text,
                        file_text,
                        snippet_text,
                        entropy_text,
                    ])

            self.status_bar.showMessage("Results exported successfully to " + filename)
            logging.info(
                f"Exported {self.results_table.rowCount()} results to {filename}"
            )
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            self.status_bar.showMessage("Error exporting results.")

    def export_labels_to_csv(self):
        """Export labeled results directly to training_labels.csv."""
        self.write_labels_to_csv("training_labels.csv")
        self.load_labeled_data()

    def write_labels_to_csv(self, filename):
        try:
            new_rows = []
            for row in range(self.results_table.rowCount()):
                label_widget = self.results_table.cellWidget(row, 6)
                label_text = label_widget.currentText() if label_widget else ""
                if not label_text:
                    continue
                search_term = self.results_table.item(row, 0).text()
                description = self.results_table.item(row, 1).text()
                repo_widget = self.results_table.cellWidget(row, 2)
                repo_text = repo_widget.text() if repo_widget else ""
                file_widget = self.results_table.cellWidget(row, 3)
                file_text = file_widget.text() if file_widget else ""
                snippet_item = self.results_table.item(row, 4)
                snippet_text = (
                    snippet_item.text().replace("\n", " ") if snippet_item else ""
                )
                entropy_item = self.results_table.item(row, 5)
                entropy_text = entropy_item.text() if entropy_item else ""
                new_rows.append([
                    search_term,
                    description,
                    repo_text,
                    file_text,
                    snippet_text,
                    entropy_text,
                    label_text,
                ])

            existing_rows = set()
            file_exists = os.path.exists(filename)
            if file_exists:
                with open(filename, newline="") as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader, None)  # skip header
                    for existing in reader:
                        existing_rows.add(tuple(existing))

            mode = "a" if file_exists else "w"
            with open(filename, mode, newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(
                        [
                            "Search Term",
                            "Description",
                            "Repository",
                            "File Path",
                            "Snippet",
                            "Entropy",
                            "Label",
                        ]
                    )
                for row in new_rows:
                    row_tuple = tuple(row)
                    if row_tuple not in existing_rows:
                        writer.writerow(row)
                        existing_rows.add(row_tuple)
            self.status_bar.showMessage("Labels exported successfully to " + filename)
            logging.info(
                f"Exported {len(new_rows)} labeled rows to {filename}"
            )
        except Exception as e:
            logging.error(f"Error exporting labels: {e}")
            self.status_bar.showMessage("Error exporting labels.")



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
            logging.info(
                f"Search started in {selected_group} for keywords: {keywords}"
            )
        else:
            self.statusBar().showMessage(
                f"Searching in {selected_group} with no keywords"
            )
            logging.info(f"Search started in {selected_group} with no keywords")
        self.stop_button.setEnabled(True)  # Allow user to stop the search
        self.search_button.setEnabled(False)
        self.export_action.setEnabled(False)  # Explicitly disable the export button
        self.export_labels_action.setEnabled(False)
        self.progress_bar.setValue(0)
        QApplication.processEvents()  # Refresh UI state before starting search
        self.perform_search(keywords, selected_group)

    def perform_search(self, keywords, selected_group):
        config = load_config()
        filter_placeholders = config.get("FILTER_PLACEHOLDERS", True)
        search_groups = create_search_queries(
            keywords, filter_placeholders=filter_placeholders

        )
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
            for query in queries:
                if not self.search_active:
                    return

                description = get_query_description(query, keywords)
                self.process_query(query, max_retries, config, query, description)
                self.completed_queries += 1
                self.progress_bar.setValue(self.completed_queries)
                self.status_bar.showMessage(
                    f"Completed {self.completed_queries}/{self.total_queries} queries"
                )
                logging.debug(
                    f"Completed {self.completed_queries}/{self.total_queries} queries"
                )
                QApplication.processEvents()

        # Search finished normally
        if self.search_active:
            self.search_active = False
            self.search_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.check_enable_export()
            result_count = self.results_table.rowCount()
            self.status_bar.showMessage(
                f"Search completed with {result_count} results."
            )
            logging.info(f"Search completed with {result_count} results.")
            QApplication.processEvents()  # Reflect updated button states



    def check_enable_export(self):
        if self.results_table.rowCount() > 0:
            self.export_action.setEnabled(True)
            self.export_labels_action.setEnabled(True)
        else:
            self.export_action.setEnabled(False)
            self.export_labels_action.setEnabled(False)

    def apply_entropy_filter(self):
        """Hide low entropy rows and disable ML features when filtering."""
        filter_on = self.high_entropy_checkbox.isChecked()
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 5)
            text = item.text() if item else ""
            try:
                value = float(text)
            except ValueError:
                value = None
            hide = filter_on and (value is None or value <= HIGH_ENTROPY_THRESHOLD)
            self.results_table.setRowHidden(row, hide)
        self.tab_widget.setTabEnabled(self.ml_tab_index, not filter_on)
        self.train_button.setEnabled(not filter_on)

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
                self.process_search_item(
                    item,
                    query,
                    description,
                    headers,
                    search_term,
                    self.filter_placeholders,
                )

    def process_search_item(
        self, item, query, description, headers, search_term, filter_placeholders=True
    ):

        if not self.search_active:
            return
        repo_name = item['repository']['full_name']
        # Update the status bar with the repository currently being processed
        self.status_bar.showMessage(f"Processing {repo_name}")
        QApplication.processEvents()
        file_path = item.get('path', '')
        config = load_config()
        patterns = config.get("IGNORED_PATH_PATTERNS", [])
        if _path_is_ignored(file_path, patterns):
            return
        file_contents = GitSleuth_API.get_file_contents(repo_name, file_path, headers)
        if file_contents:
            snippets = extract_snippets(
                file_contents, query, filter_placeholders=filter_placeholders
            )
            query_terms = extract_search_terms(query)
            entropies = [get_secret_entropy(s, query_terms=query_terms) for s in snippets]

            self.update_results_table(
                repo_name,
                file_path,
                snippets,
                search_term,
                description,
                entropies,
            )
    def create_clickable_link(self, text, url):
        link_label = QLabel()
        link_label.setText(f'<a href="{url}">{text}</a>')
        link_label.setOpenExternalLinks(True)
        return link_label
    
    def update_results_table(self, repo_name, file_path, snippets, search_term, description, entropies=None):
        if not self.search_active:
            return
        github_base_url = "https://github.com/"
        scores = entropies or [None] * len(snippets)
        for snippet, score in zip(snippets, scores):
            if not self.search_active:
                break
            if self.high_entropy_checkbox.isChecked() and (

                score is None or score < HIGH_ENTROPY_THRESHOLD
            ):
                continue
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)

            # Filter out unwanted terms from the search term
            filtered_search_term = search_term.replace(PLACEHOLDERS, "").strip()

            # Search term column
            search_item = QTableWidgetItem(filtered_search_term)
            search_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row_position, 0, search_item)
            # Description column
            description_item = QTableWidgetItem(description)
            description_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row_position, 1, description_item)

            # Repository column with clickable link
            repo_url = f"{github_base_url}{repo_name}"
            repo_link_label = self.create_clickable_link(repo_name, repo_url)
            repo_link_label.setAlignment(Qt.AlignCenter)
            self.results_table.setCellWidget(row_position, 2, repo_link_label)

            # File path column with clickable link
            file_url = f"{repo_url}/blob/main/{file_path}"
            file_link_label = self.create_clickable_link(file_path, file_url)
            file_link_label.setAlignment(Qt.AlignCenter)
            self.results_table.setCellWidget(row_position, 3, file_link_label)

            # Snippets column with highlighted search terms
            highlighted = highlight_terms_html(snippet, filtered_search_term)
            snippet_label = QLabel()
            snippet_label.setTextFormat(Qt.RichText)
            snippet_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            snippet_label.setWordWrap(True)
            snippet_label.setText(highlighted)
            snippet_label.setAlignment(Qt.AlignCenter)
            self.results_table.setCellWidget(row_position, 4, snippet_label)
            self.results_table.resizeRowToContents(row_position)

            # Entropy column
            if score is None:
                entropy_item = QTableWidgetItem("LOW")
            else:
                entropy_item = QTableWidgetItem(f"{score:.2f}")
            entropy_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row_position, 5, entropy_item)

            # Label column with dropdown
            label_box = QComboBox()
            label_box.setToolTip(
                "Classify the result as a true or false positive"
            )
            label_box.addItems(["", "True Positive", "False Positive"])
            label_box.setStyleSheet("QComboBox { text-align: center; }")

            if score is None or score <= HIGH_ENTROPY_THRESHOLD:

                label_box.setCurrentText("False Positive")
            elif score > HIGH_ENTROPY_THRESHOLD:
                label_box.setCurrentText("True Positive")
            self.results_table.setCellWidget(row_position, 6, label_box)

            if (
                self.high_entropy_checkbox.isChecked()
                and (score is None or score <= HIGH_ENTROPY_THRESHOLD)
            ):
                self.results_table.hideRow(row_position)
        # Enable export buttons if there are results
        if self.results_table.rowCount() > 0:
            self.export_action.setEnabled(True)
            self.export_labels_action.setEnabled(True)
            self.clear_results_action.setEnabled(True)  # Enable the clear results button
            count = self.results_table.rowCount()
            self.status_bar.showMessage(f"Results found ({count}).")
            logging.info(f"Results found ({count}).")

    def apply_entropy_filter(self, state):
        """Show only rows above the entropy threshold and toggle ML access."""
        checked = state == Qt.Checked
        if hasattr(self, "tab_widget"):
            self.tab_widget.setTabEnabled(self.ml_tab_index, not checked)
        self.train_button.setEnabled(not checked)

        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 5)
            text = item.text() if item else ""
            try:
                value = float(text)
            except ValueError:
                value = 0.0
            if checked and value <= HIGH_ENTROPY_THRESHOLD:
                self.results_table.hideRow(row)
            else:
                self.results_table.showRow(row)


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

    def load_labeled_data(self):
        """Load labeled data and display basic info on the ML tab."""
        self.ml_output.clear()
        if not os.path.exists("training_labels.csv"):
            self.ml_output.append("No labeled data found.")
            self.status_bar.showMessage("No labeled data found.")
            return
        try:
            df = pd.read_csv("training_labels.csv")
            self.ml_output.append(f"Loaded {len(df)} labeled rows.")
            self.status_bar.showMessage(
                f"Loaded {len(df)} labeled rows"
            )
        except Exception as e:
            self.ml_output.append(f"Error loading labels: {e}")
            self.status_bar.showMessage("Error loading labels")

    def train_model(self):
        """Train a simple text model on labeled data."""
        # Persist any currently labeled rows before training
        self.write_labels_to_csv("training_labels.csv")
        if not os.path.exists("training_labels.csv"):
            self.ml_output.append("No labeled data to train on.")
            self.status_bar.showMessage("No labeled data to train on.")
            return
        try:
            df = pd.read_csv("training_labels.csv")
            if df.empty:
                self.ml_output.append("No labeled data to train on.")
                self.status_bar.showMessage("No labeled data to train on.")
                return
            # Ensure snippets are strings to avoid vectorizer errors
            df["Snippet"] = df["Snippet"].astype(str).fillna("")
            vectorizer = TfidfVectorizer()
            text_features = vectorizer.fit_transform(df["Snippet"])
            paths = df.get("File Path", ["" for _ in range(len(df))])
            extra = np.array(
                [compute_features(snippet, path) for snippet, path in zip(df["Snippet"], paths)]
            )
            X = hstack([text_features, csr_matrix(extra)])

            y = df["Label"].apply(lambda x: 1 if x == "True Positive" else 0)
            if y.nunique() < 2:
                self.ml_output.append(
                    "Training requires at least two label classes."
                )
                self.status_bar.showMessage(
                    "Training requires at least two label classes."
                )
                return

            self.status_bar.showMessage("Training model...")
            logging.info("Training model started.")
            model = LogisticRegression(max_iter=1000)
            model.fit(X, y)
            self.ml_output.append(f"Model trained on {len(df)} samples.")
            self.status_bar.showMessage(
                f"Model trained on {len(df)} samples."
            )
            logging.info(f"Model trained on {len(df)} samples.")
        except Exception as e:
            self.ml_output.append(f"Training failed: {e}")
            self.status_bar.showMessage("Training failed")
            logging.error(f"Training failed: {e}")


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
        buttons.button(QDialogButtonBox.Ok).setToolTip("Save settings")
        buttons.button(QDialogButtonBox.Cancel).setToolTip("Cancel")
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
        self.setGeometry(100, 100, 600, 400)
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
        self.add_btn.setToolTip('Add a new token')
        self.add_btn.clicked.connect(self.add_token_dialog)
        btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton('Delete Token')
        self.delete_btn.setToolTip('Delete the selected token')
        self.delete_btn.clicked.connect(self.delete_token)
        btn_layout.addWidget(self.delete_btn)

        self.oauth_btn = QPushButton('OAuth Login')
        # Wider button so "Logged in as" text fits comfortably
        self.oauth_btn.setFixedWidth(180)
        self.oauth_btn.setToolTip('Authenticate using OAuth')
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
        add_button.setToolTip("Add token")
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
