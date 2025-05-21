# GitSleuth

## Overview

GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI.

## Features
* Predefined and custom search queries
* Token rotation to handle API rate limits
* Export results to Excel or CSV
* Secure token storage

* Extensive search query templates in [ADVANCED_QUERIES.md](ADVANCED_QUERIES.md)

* al search templates in [SEARCH_QUERIES.md](SEARCH_QUERIES.md)

* OAuth device flow authentication
* Export results to Excel or CSV

* Token rotation to handle API rate limits
* Export results to Excel or CSV


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

## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).


CLI options allow OAuth login, running search groups, performing custom searches and adjusting settings.

Use the "OAuth Login" option to authorize and store a token.

CLI options allow setting, deleting and viewing tokens, running search groups, performing custom searches and adjusting settings.


## Pre-compiled Binary for Windows
The `dist` folder contains `GitSleuth_GUI.exe` for Windows users.

## Configuration

Edit `config.json` for log level and ignored filenames. 


## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
