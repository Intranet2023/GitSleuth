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
- Keyword filter field in the GUI for quickly narrowing searches
- Searches include modern API tokens like Vercel, Hugging Face, Supabase,
  Sentry, and Rollbar
- Optional integration with Yelp's detect-secrets for advanced secret detection


- Optional session keep-alive after closing the GUI

- Automatic restoration of your OAuth login on launch


- Results table now shows a short description for each rule
- Simple dictionary and format heuristics filter out values that look like
  ordinary words, UUIDs, or dates


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
   Run the setup script to ensure all requirements are installed while network
   access is available.
   ```bash
   ./setup.sh
   ```

## Usage
### GUI
```bash
python GitSleuth_GUI.py
```
Use the **Keywords** field to limit searches to specific domains or terms.

Each result row also displays the description of the rule that matched.

#### Labeling Results
Use the **Label** column to mark each result as a **True Positive** or **False Positive**. Click **Export Labels** to save the selections to `training_labels.csv` for machine-learning.

#### Training
Open the **ML** tab and click **Train Model** to train a simple text classifier on the saved labels. Training progress is shown in the tab's output area.
The labeled data is stored in `training_labels.csv`. Models are currently kept in memory after training.
Example passwords for experimentation are provided in `training_data.csv`.
Training uses TF‑IDF text features combined with entropy and character composition metrics

(length, numeric %, alphabetic %, special %) plus simple dictionary and pattern
checks to help distinguish real secrets from placeholders.



### CLI
```bash
python GitSleuth.py
```
When starting OAuth authentication, your default browser will automatically open
to the GitHub device flow page so you can enter the provided code.

## Configuration
Edit `config.json` to adjust log level, ignored filenames, and path patterns
that should be skipped (e.g. `tests/`, `examples/`, or files containing `.sample.`).
You can also control whether placeholder terms are filtered from queries and results. When enabled the
filter removes hits where environment variables have empty or placeholder
values. You can also define `ALLOWLIST_PATTERNS` with regex strings for
known dummy secrets so matching snippets are ignored.
Enable `USE_DETECT_SECRETS` to scan snippets with the `detect-secrets`
tool and set `DETECT_SECRETS_BASELINE` to a baseline file for allowlisted
secrets.
Set `ENTROPY_THRESHOLD` (bits/char) to skip low-entropy values that
look like placeholders.
The application ships with a default GitHub OAuth client ID so it works out of
the box. Set `GITHUB_OAUTH_CLIENT_ID` to override it and define
`GITHUB_OAUTH_CLIENT_SECRET` if your OAuth app requires a secret.
By default the application requests the `public_repo` OAuth scope for
read-only access. Override this by setting `GITHUB_OAUTH_SCOPE` if you
require additional permissions.

## Automated Conflict Resolution
The repository includes `auto_resolve_conflicts.sh` to merge incoming
changes while prioritizing the new code. Run the script with the name
of the branch you want to merge:

```bash
./auto_resolve_conflicts.sh main
```
It fetches the branch from `origin`, merges it with the `theirs` strategy,
and verifies that no conflict markers remain.


## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
