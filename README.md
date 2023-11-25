# GitSleuth

GitSleuth is a tool designed for searching sensitive information in GitHub repositories. It focuses on identifying potentially leaked or exposed data such as credentials, API keys, and private keys within an organization's domain.

## Features

- Search GitHub for sensitive data across various categories.
- Customizable search queries based on organization's domain.
- Option to perform grouped or custom searches.
- Extracts and displays snippets of found data.
- Logging functionality to track search activities and results.
- Configuration file for easy management of GitHub API tokens and logging levels.

## Installation

Clone the repository to your local machine:

```bash
git clone https://your-repository-url/GitSleuth.git
cd GitSleuth
Install the required dependencies (ensure you have Python and pip installed):

bash
Copy code
pip install -r requirements.txt
Configuration
Create a config.json file in the project root with the following content:

json
Copy code
{
  "GITHUB_TOKENS": ["your_github_token_here"],
  "LOG_LEVEL": "INFO"
}
Replace "your_github_token_here" with your actual GitHub token.

Adjust the LOG_LEVEL as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL).

Usage
Run the script:

bash
Copy code
python GitSleuth.py
Follow the on-screen prompts to perform searches.

Search Options
Set GitHub Token: Add or update GitHub API tokens.
Delete GitHub Token: Remove existing GitHub tokens.
View GitHub Token: Display currently set GitHub tokens.
Perform Group Searches: Execute predefined group searches.
Perform Custom Search: Run custom search queries.
Exit: Terminate the program.
Contributing
Contributions to GitSleuth are welcome. Please ensure to follow the coding standards and write tests for new features.
