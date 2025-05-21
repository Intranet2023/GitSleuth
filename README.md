# GitSleuth

GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI with a dark theme.

## Features
- Predefined and custom search queries
- OAuth device flow authentication
- Token rotation with secure storage
- Export results to Excel or CSV
- Extensive query templates in [SEARCH_QUERIES.md](SEARCH_QUERIES.md) and [ADVANCED_QUERIES.md](ADVANCED_QUERIES.md)

## Installation
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

Edit `config.json` for log level and ignored filenames.

## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
