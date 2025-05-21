# GitSleuth

## Overview
GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI.

## Features
- Predefined and custom search queries with extensive templates from
  [ADVANCED_QUERIES.md](ADVANCED_QUERIES.md) and
  [SEARCH_QUERIES.md](SEARCH_QUERIES.md)
- OAuth device flow authentication with token rotation and secure token
  storage to handle API rate limits
- Export results to Excel or CSV
- Sleek dark theme for the GUI

## Installation
### Prerequisites
- Python 3.x
- pip
- Git

### Steps
1. Clone the repository
   ```bash
   git clone https://github.com/your-repository/GitSleuth.git
   cd GitSleuth
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### GUI
```bash
python GitSleuth_GUI.py
```
The GUI opens with a dark theme for improved readability. Use the **OAuth Login** button to authenticate; the button updates to show your GitHub username after login.

### CLI
```bash
python GitSleuth.py
```

## Configuration
Edit `config.json` to adjust log level and ignored filenames.

## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
