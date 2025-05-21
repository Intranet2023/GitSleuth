# GitSleuth


GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI with a dark theme.

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

The GUI now defaults to a dark theme for improved readability and no longer
requires manual theme configuration. Use the **OAuth Login** button to
authenticate with GitHub. The verification code is automatically copied to your
clipboard and a browser window opens to complete the process.



### CLI
```bash
python GitSleuth.py
```
When starting OAuth authentication, your default browser will automatically open
to the GitHub device flow page so you can enter the provided code.

## Configuration
Edit `config.json` to adjust log level and ignored filenames. The
application ships with a default GitHub OAuth client ID so it works out of
the box. Set `GITHUB_OAUTH_CLIENT_ID` to override it and define
`GITHUB_OAUTH_CLIENT_SECRET` if your OAuth app requires a secret.


## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
