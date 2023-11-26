# GetSleuth_Groups.py

def create_search_queries(domain):
    """
    Creates a dictionary of search queries for different categories, incorporating the given domain.

    Parameters:
    domain (str): The domain to be included in the search queries.

    Returns:
    dict: A dictionary where each key is a category, and the value is a list of search queries.
    """
    
    # Define search queries in various categories
    return {
        # Authentication data like npm or Docker configurations which might contain sensitive data
        "Authentication Data": [
            f"filename:.npmrc _auth {domain}",
            f"filename:.dockercfg auth {domain}"
        ],

        # Private key files that should not be exposed
        "Private Keys": [
            f"extension:pem private {domain}",
            f"extension:ppk private {domain}",
            f"filename:id_rsa OR filename:id_dsa {domain}"
        ],

        # Configuration files that might contain sensitive information
        "Configuration Files": [
            f"filename:wp-config.php {domain}",
            f"filename:.htpasswd {domain}",
            f"filename:.env DB_USERNAME NOT homestead {domain}"
        ],

        # Credentials, particularly for AWS services
        "Credentials": [
            f"filename:credentials aws_access_key_id {domain}",
            f"filename:.s3cfg {domain}",
            f"filename:.git-credentials {domain}"
        ],

        # Queries targeting database dumps which might contain sensitive data
        "Database Related": [
            f"extension:sql mysql dump {domain}",
            f"extension:sql mysql dump password {domain}"
        ],

        # API keys and tokens which might be exposed in files
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain}",
            f"HEROKU_API_KEY language:shell {domain}",
            f"HEROKU_API_KEY language:json {domain}"
        ],

        # Recovery keys for various services
        "Recovery Keys": [
            f"filename:github-recovery-codes.txt {domain}",
            f"filename:gitlab-recovery-codes.txt {domain}",
            f"filename:discord_backup_codes.txt {domain}"
        ],

        # Unencrypted configuration files can expose sensitive settings
        "Unencrypted Configuration Files": [
            f"filename:config.json NOT encrypted NOT secure {domain}"
        ],

        # Exposed API endpoints could be a security risk
        "Exposed API Endpoints": [
            f"API_BASE_URL {domain}"
        ],

        # Default passwords hardcoded in the code
        "Default Passwords in Code": [
            f"password 'admin' {domain}"
        ],

        # Tokens such as Slack tokens that should not be exposed
        "Leaked Tokens": [
            f"xoxp OR xoxb {domain}"
        ],

        # Debug information can inadvertently expose sensitive data
        "Debug Information": [
            f"filename:debug.log {domain}"
        ],

        # Custom searches for pre-shared keys avoiding examples and placeholders
        "Custom Search": [
            f"pre-shared key NOT example NOT placeholder {domain}"
        ],

        # Additional searches based on insights from GitHub's Blackbird search engine

        # Searching for cloud service configuration files
        "Cloud Service Configurations": [
            f"filename:azure-pipelines.yml {domain}",
            f"filename:.aws/config {domain}"
        ],

        # Searching for hardcoded sensitive URLs
        "Hardcoded Sensitive URLs": [
            f"filename:*.config \"https://internal.{domain}\""
        ],

        # Searching for email patterns which might be exposed
        "Email Patterns": [
            f"\"{domain}.com email\""
        ],

        # Regular expression based searches for specific patterns
        "Regex Based Searches": [
            # Add regex-based search patterns specific to your organization here
        ],

        # Searching in Infrastructure as Code files for sensitive data
        "IaC Files": [
            f"filename:main.tf aws_access_key_id {domain}"
        ],

        # Searching for sensitive comments left in code
        "Sensitive Comments": [
            f"language:java \"// TODO: remove before production {domain}\""
        ],

        # Historical search for old credentials in .env files
        "Historical Credential Searches": [
            f"filename:.env DB_PASSWORD NOT current {domain}"
        ]
    }

