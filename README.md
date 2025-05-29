# GitSleuth


GitSleuth searches GitHub repositories for sensitive data. It provides both a command-line interface and a PyQt5 GUI with a dark theme.

## Features

- Predefined and custom search queries using templates in [ADVANCED_QUERIES.md](ADVANCED_QUERIES.md) and [SEARCH_QUERIES.md](SEARCH_QUERIES.md)
- OAuth device flow authentication with secure token storage and rotation
- Optional session keep-alive after closing the GUI with automatic login restoration
- Dark-themed GUI and CLI with a keyword filter to narrow searches
- Searches include tokens for Vercel, Hugging Face, Supabase, Sentry, Rollbar, GitLab, Cloudflare, Vault and Pinecone
- Status bar shows rate limit pauses and tokens rotate automatically
- Export results to Excel or CSV
- Machine learning tab to label results and train a classifier using entropy and context features
- Optional integration with Yelp's `detect-secrets` for advanced scanning
- Results table includes rule descriptions
- Dictionary and format heuristics filter out common words, UUIDs or dates
- Pattern detection identifies environment variable names and token strings
- Snippets referencing environment variables (e.g. `os.environ` or `process.env`) are ignored
- Allowlist patterns skip known dummy secrets via `ALLOWLIST_PATTERNS`
- Placeholder filtering now detects values repeating the key name or wrapped in bold markup
- `auto_resolve_conflicts.sh` script merges branches while keeping incoming changes
- `setup.sh` allows installing dependencies before network access is disabled

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
Open the **ML** tab and click **Perform Machine Learning** to train a simple text classifier on the saved labels. Any newly labeled rows are automatically appended to `training_labels.csv` before training begins to ensure no data is lost. Training progress is shown in the tab's output area.
The labeled data is stored in `training_labels.csv`. Models are currently kept in memory after training.
Example passwords for experimentation are provided in `training_data.csv`.
Training uses TF‑IDF text features combined with entropy and character composition metrics

Ensure your labeled dataset includes both **True Positive** and **False Positive** examples,
otherwise model training will fail with a single-class error.

(length, numeric %, alphabetic %, special %) plus simple dictionary and pattern
checks to help distinguish real secrets from placeholders. Additional features
also encode the file type (config, source, log, other) and simple structural
context such as assignments or secret-setting function calls.

#### ML Workflow
1. After running a search, mark each result row as **True Positive** or **False Positive** using the **Label** column.
2. (Optional) Click **Export Labels** to manually save selections. Training also saves any labels automatically.
3. Switch to the **ML** tab and click **Perform Machine Learning**. The application reads `training_labels.csv`, extracts text and entropy features and trains a logistic regression classifier.
4. When training completes, the tab displays how many samples were used and the model remains in memory for the current session.



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
values, and ignores snippets that retrieve values from environment variables.
You can also define `ALLOWLIST_PATTERNS` with regex strings for
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


## Checks
Before committing, ensure the main modules compile:

```bash
python -m py_compile GitSleuth_GUI.py OAuth_Manager.py Token_Manager.py GitSleuth.py GitSleuth_API.py
```

## Contributing
Contributions are welcome. Please follow standard open-source practices.

## License
Released under the MIT License. See [LICENSE](LICENSE).

## Support
For support, open an issue on GitHub or contact david.mclaughlin@dsmcl.com.
