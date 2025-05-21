# GitSleuth

## Overview
GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI.

## Features
- Predefined and custom search queries
- Token rotation to handle API rate limits
- OAuth device flow authentication
- Export results to Excel or CSV
- Secure token storage
- Extensive templates in [ADVANCED_QUERIES.md](ADVANCED_QUERIES.md) and [SEARCH_QUERIES.md](SEARCH_QUERIES.md)
- Sleek dark theme (GUI) without the old rule editor pane

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
