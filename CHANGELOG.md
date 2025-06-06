# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]
- Documented release date for prior changes in this file
- Results label defaults to "False Positive" for LOW entropy or scores ≤ 4.0
- Added "Show High Entropy Only" checkbox to hide low-entropy results and disable ML features
- Button label changed from "Show High Entropy Only" to "Hide Low Entropy Results"
- Cleaned AGENTS.md to remove merge conflict markers and clarify instructions
- Introduced `auto_pull.sh` wrapper to run `git pull` with automatic conflict
  resolution and updated AGENTS.md accordingly
- Console table output centered for improved readability

- Added optional gitleaks scanning with `USE_GITLEAKS` and `GITLEAKS_CONFIG`

- Status bar and log window now provide detailed messages on search progress,
  exports, and training

- GUI results table centered for improved readability
- GUI secrets now display the secret text in red and preceding search terms in blue
- Added `ML_Tester.py` to train on `training_data.csv`, report accuracy, and
  analyze user-provided phrases for secrets
- ML password tester now flags all-caps words and phrases as placeholders and
  treats entropy scores above 4.0 as likely real passwords
- Added `testing_data.csv` with labeled phrases for evaluating secret detection
- Introduced `Secret_Trainer.py` CLI skeleton for model training
- Added `joblib` and `numpy` to requirements

- `ML_Tester.py` now falls back to a built-in logistic regression when
  pandas or scikit-learn are unavailable.

- Added "Train Example Model" and "Analyze Phrase" features in the ML tab for
  accuracy testing and secret detection
- Added "Test Example Model" button to evaluate the sample classifier on
  `testing_data.csv` directly from the GUI
- Removed "Train Example Model" button; testing and phrase analysis now
  train the sample classifier automatically




## 2025-05-29
### Added
- Labels export now appends to existing training_labels.csv without duplicates
- ML button renamed to "Perform Machine Learning" and automatically saves labels before training
- ML tab refreshes when exporting labels
- ML and Log tabs swapped for easier access
- Generalized `.gitignore` to ignore Python bytecode
- Consolidated duplicate token management functions
- Allowlist patterns for ignoring dummy secrets with `ALLOWLIST_PATTERNS` in configuration
- Removed custom search preset functionality and related configuration
- Optional integration with Yelp's `detect-secrets` for improved secret detection
- Added detection utilities for environment variable names and token strings
- Expanded snippet and window sizes for better context
- Default window expanded further with word-wrapped snippets and automatic row resizing
- Adjusted snippet context to 40 characters before and 100 after search terms
- Added machine learning training interface with label export
- High entropy search with entropy scores displayed in results
- Introduced entropy-based and contextual features for ML training
- Added dictionary and format heuristics to reduce false positives
- Fixed CSV export column order
- GUI results table now displays entropy scores with CSV export support
- Standardized scikit-learn imports and one-hot file type features
- Automated conflict resolution via `auto_resolve_conflicts.sh`
- README improvements covering ML workflow and compile checks
- Environment variable references filtered to avoid false positives
- Graceful handling of token decryption errors
- Fixed training error when only one label class
- Fixed training failure when file paths contain non-string values
- Fixed ML training crash when snippets contain non-string values
- Updated `AGENTS.md` to require changelog updates for every change
- Case-insensitive highlighting of search terms in snippets
- Placeholder filtering checks assigned values for key reuse and bold markup
- Enabled color highlighting of secrets by initializing colorama
- GUI results table now highlights matched terms in red
- Entropy scores computed for assigned values with placeholder filtering
- Entropy detection now matches query terms within variable names, preventing "N/A" scores
- Extracts secret values after common keywords with red highlighting and entropy displayed as 'LOW' when unknown

### Fixed
- Fixed invisible tooltips for toolbar actions and differentiated clear icons
- Dedicated toolbar with icons for clearing log/results and exporting
- Added tooltips for all buttons
- Added tooltips for dropdown selections
- Fixed OAuth token retrieval to prefer the active login token
- Search controls moved to the toolbar next to export actions
- Labels default to "False Positive" for low entropy and "True Positive" for scores above 4.0


## 2025-05-23
- Added search patterns for modern API tokens including Vercel, Hugging Face,
  Supabase, Sentry, and Rollbar.
- Updated `ADVANCED_QUERIES.md`, `SEARCH_QUERIES.md`, and
  `GitSleuth_Groups.py` to include these new queries.
- Added modern API token patterns (Vercel, Hugging Face, Supabase, Sentry, Rollbar)
  to query generator and documentation
- Consolidated Token_Manager functions and fixed header generation
- Generalized `.gitignore` to ignore Python cache files

## 2025-05-22
- Created this CHANGELOG in response to a chat request
- Added persistent OAuth login across restarts
- Introduced session keep-alive feature
- Bumped `requests` to 2.32.2
- Multiple README updates and improvements
- Added configuration option to toggle placeholder filtering in queries
- Placeholder filtering now skips results where environment variables
  have empty or placeholder values


## 2025-05-21
- Added comprehensive secret detection queries
- Improved result filtering and added rule descriptions
- Updated status bar to show rate limiting pauses
- Added keyword input for searches

## 2025-05-20
- Improved button states based on program status
- Fixed application hanging during rate limit waits
- Prevented OAuth double authentication
- Added OAuth username retrieval

## 2024-04-15
- Added setup script for offline installation
- Restored default OAuth client ID
- Improved OAuth login flow with clipboard support

## 2023-11-26
- Initial release of GitSleuth with GUI and CLI
- Created README
