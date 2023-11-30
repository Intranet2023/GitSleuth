Sure, I can help you format the content for a README.md file in GitHub. Here's the formatted content:

```markdown
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
git clone [https://github.com/your-repository/GitSleuth.git](https://github.com/your-repository/GitSleuth.git)
```

2. Navigate to the GitSleuth directory:
```bash
cd GitSleuth
```

3. Install the required Python dependencies:
```
pip install -r requirements.txt
```

## Usage

### Graphical User Interface (GUI)

1. Launch the GUI:
```bash
python GitSleuth_GUI.py
```

2. In the GUI:
    * Enter the search domain.
    * Select the category of queries.
    * Initiate the search and view results.
    * Export results and manage API tokens.

### Command-Line Interface (CLI)

1. Start the CLI mode:
```bash
python GitSleuth.py
```

2. CLI Options:
    * Set, delete, and view GitHub tokens.
    * Choose and execute search groups.
    * Perform custom searches.
    * Manage application settings.

### Examples

#### Performing a grouped search:
```
mathematica
```
Enter your choice: 4

Enter your organization's domain for search: example.com

Available Search Groups:
1. Authentication and Credentials
2. API Keys and Tokens
...

Enter your choice (number) or 'all': 1

#### Adding a GitHub token:
```
mathematica

Enter your choice: 1

Enter a GitHub token: <your-token>

## Configuration

Configure `config.json` for settings like log level and ignored filenames. API tokens are managed securely via `Token_Manager.py` and are not stored in `config.json`.

## Contributing

Contributions to GitSleuth are welcome. Please follow standard procedures for contributing to open-source projects.

## License

GitSleuth is released under the MIT License.

## Support

For support, open an issue on the GitHub repository or contact the project maintainers.


Please let me know if you have any other questions.
