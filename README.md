# GitSleuth

## Overview

GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI.

## Features
* Predefined and custom search queries
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

### CLI
```bash
python GitSleuth.py
```

CLI options allow setting, deleting and viewing tokens, running search groups, performing custom searches and adjusting settings.

## Pre-compiled Binary for Windows
The `dist` folder contains `GitSleuth_GUI.exe` for Windows users.

## Configuration
Edit `config.json` for log level and ignored filenames. API tokens are managed via `Token_Manager.py`.

## OAuth Authentication
GitSleuth can obtain an access token using GitHub's device flow. Set the `GITHUB_OAUTH_CLIENT_ID` environment variable to the Client ID of your GitHub OAuth app and choose **OAuth Login** from the CLI or click **OAuth Login** in the GUI's token manager. Follow the displayed instructions and the retrieved token will be saved in `tokens.json`.

## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
