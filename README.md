# GitSleuth

## Overview

GitSleuth is a comprehensive tool designed for searching GitHub repositories to identify sensitive data, credentials, or specific code patterns. It features a Graphical User Interface (GUI) for ease of use and a Command-Line Interface (CLI) for advanced users.

## Features

* Detailed GitHub Repository Search: Utilizes predefined or customizable queries for searching repositories.
* Efficient Rate Limit Management: Implements token swapping to handle GitHub API rate limits.
* User-Friendly GUI: Provides an intuitive interface for conducting and reviewing searches.
* Versatile CLI: Offers direct command-line access for automation and advanced use.
* Result Export: Enables exporting search results to Excel for further analysis.
* Secure API Token Management: Ensures the secure handling and storage of GitHub API tokens.

## Installation

### Prerequisites

* Python 3.x
* pip (Python package manager)
* Git (for cloning the repository)

### Steps

1. Clone the GitSleuth repository:
```bash
git clone [https://github.com/your-repository/GitSleuth.git](https://github.com/your-repository/GitSleuth.git): [https://github.com/your-repository/GitSleuth.git](https://github.com/your-repository/GitSleuth.git)
Use code with caution. Learn more
Navigate to the GitSleuth directory:
Bash
cd GitSleuth
Use code with caution. Learn more
Install the required Python dependencies:
pip install -r requirements.txt
Usage
Graphical User Interface (GUI)
Launch the GUI:
Bash
python GitSleuth_GUI.py
Use code with caution. Learn more
In the GUI:
Enter the search domain.
Select the category of queries.
Initiate the search and view results.
Export results and manage API tokens.
Command-Line Interface (CLI)
Start the CLI mode:
Bash
python GitSleuth.py


2. CLI Options:
    * Set, delete, and view GitHub tokens.
    * Choose and execute search groups.
    * Perform custom searches.
    * Manage application settings.

## Pre-compiled Binary for Windows

A pre-compiled binary for Windows can be found in the `dist` folder of the repository. To run the binary, simply double-click on the `GitSleuth_GUI.exe` file.

## Configuration

Configure `config.json` for settings like log level and ignored filenames. API tokens are managed securely via `Token_Manager.py` and are not stored in `config.json`.

## Contributing

Contributions to GitSleuth are welcome. Please follow standard procedures for contributing to open-source projects.

## License

GitSleuth is released under the MIT License.

## Support

For support, open an issue on the GitHub repository or contact the project maintainers.

## Support

For support, open an issue on the GitHub repository or contact the project maintainers.


Please let me know if you have any other questions.
