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
from GitSleuth import load_config, get_headers, extract_snippets

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

        self.setGeometry(300, 300, 800, 600)

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
        headers = get_headers(config)
        ignored_filenames = config.get('IGNORED_FILENAMES', [])
        if self.search_all:
            groups = search_groups.keys()
        else:
            groups = [selected_group]

        for group in groups:
            queries = search_groups.get(group, [])
            for query in queries:
                self.execute_query(query, headers, ignored_filenames)

    def execute_query(self, query, headers, ignored_filenames):
        search_results = GitSleuth_API.search_github_code(query, headers)
        if search_results and 'items' in search_results:
            for item in search_results['items']:
                if item['path'] not in ignored_filenames:
                    self.process_search_item(item, query, headers)
        else:
            logging.info(f"No results found for query: {query}")

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
