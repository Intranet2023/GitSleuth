# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]
### Added
- Modern API token searches for Vercel, Hugging Face, Supabase, Sentry, Rollbar,
  GitLab, Cloudflare, Vault and Pinecone
- Generalized `.gitignore` to ignore Python bytecode
- Consolidated duplicate token management functions
- Allowlist patterns for ignoring dummy secrets with `ALLOWLIST_PATTERNS` in configuration
- Optional integration with Yelp's `detect-secrets` for improved secret detection


## 2025-05-23
- Added search patterns for modern API tokens including Vercel, Hugging Face,
  Supabase, Sentry, and Rollbar.
- Updated `ADVANCED_QUERIES.md`, `SEARCH_QUERIES.md`, and
  `GitSleuth_Groups.py` to include these new queries.

## 2025-05-22
- Created this CHANGELOG in response to a chat request
- Added persistent OAuth login across restarts
- Introduced session keep-alive feature
- Bumped `requests` to 2.32.2
- Multiple README updates and improvements
- Added configuration option to toggle placeholder filtering in queries
- Placeholder filtering now skips results where environment variables
  have empty or placeholder values

## 2025-05-23
- Added modern API token patterns (Vercel, Hugging Face, Supabase, Sentry, Rollbar)
  to query generator and documentation
- Consolidated Token_Manager functions and fixed header generation
- Generalized `.gitignore` to ignore Python cache files


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
