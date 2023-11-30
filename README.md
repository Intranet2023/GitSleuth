Overview
GitSleuth is a versatile tool for searching GitHub repositories to identify exposed sensitive data, credentials, or specific code patterns. It features both a Graphical User Interface (GUI) and a Command-Line Interface (CLI) for flexible usage.

Features
Search GitHub Repositories: Uses predefined or custom queries to search for sensitive data in GitHub repositories.
Rate Limit Management: Implements token swapping to manage and overcome GitHub API rate limits.
Graphical User Interface: Intuitive GUI for easy interaction with the tool.
Command-Line Interface: Alternative CLI for more direct control and scripting capabilities.
Export Functionality: Enables users to export search results into Excel format for further analysis.
Secure Token Management: Securely manages GitHub API tokens using encryption.
Installation
Clone the GitSleuth repository.
Navigate to the GitSleuth directory.
Install the required dependencies.
bash
Copy code
git clone https://github.com/your-repository/GitSleuth.git
cd GitSleuth
pip install -r requirements.txt
Usage
GUI Mode
Run GitSleuth_GUI.py to start the application in GUI mode. The GUI allows users to:

Select search domains.
Choose categories for search queries.
View and manage search results.
Export results.
Manage API tokens.
CLI Mode
Run GitSleuth.py to start the application in CLI mode. The CLI provides options to:

Set, delete, and view GitHub tokens.
Perform group searches and custom searches.
Manage search settings.
Configuration
Configure the application settings in config.json, including log level and other preferences. Ensure that config.json is correctly formatted and located in the root directory.
