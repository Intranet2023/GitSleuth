# GitSleuth

## Overview

GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI.

## Features
* Predefined and custom search queries
* OAuth device flow authentication
* Export results to Excel or CSV

* Token rotation to handle API rate limits
* Export results to Excel or CSV
* Secure token storage


## Installation

### Prerequisites
* Python 3.x
* pip
* Git

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/GitSleuth.git
   cd GitSleuth
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI
```bash
python GitSleuth_GUI.py
```

Use "Manage Tokens" > "OAuth Login" to authenticate via GitHub.


### CLI
```bash
python GitSleuth.py
```


CLI options allow OAuth login, running search groups, performing custom searches and adjusting settings.

Use the "OAuth Login" option to authorize and store a token.

CLI options allow setting, deleting and viewing tokens, running search groups, performing custom searches and adjusting settings.


## Pre-compiled Binary for Windows
The `dist` folder contains `GitSleuth_GUI.exe` for Windows users.

## Configuration

Edit `config.json` for log level and ignored filenames. Set `GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` environment variables before running the tool.

Edit `config.json` for log level and ignored filenames. API tokens are managed via `Token_Manager.py`.



## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
