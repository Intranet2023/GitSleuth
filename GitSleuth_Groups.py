#GitSleuth_Groups.py
def create_search_queries(domain):
    """
    Creates a dictionary of search queries for different categories,
    incorporating the given domain and applying strategies to exclude common placeholders.

    Parameters:
    - domain (str): The domain to be included in the search queries.

    Returns:
    - dict: A dictionary where each key is a category, and the value is a list of search queries.
    """
    placeholders = "NOT example NOT dummy NOT test NOT sample NOT placeholder"

    domain_filter = f'"{domain}"' if domain else ""
    return {
        "Authentication and Credentials": [
            f"filename:.npmrc _auth {domain_filter} {placeholders}",
            f"filename:.dockercfg auth {domain_filter} {placeholders}",
            f"extension:pem private {domain_filter} {placeholders}",
            f"extension:ppk private {domain_filter} {placeholders}",
            f"filename:id_rsa OR filename:id_dsa {domain_filter} {placeholders}",
            f"filename:wp-config.php {domain_filter} {placeholders}",
            f"filename:.htpasswd {domain_filter} {placeholders}",
            f"filename:.env DB_USERNAME NOT homestead {domain_filter} {placeholders}",
            f"filename:credentials aws_access_key_id {domain_filter} {placeholders}",
            f"filename:.s3cfg {domain_filter} {placeholders}",
            f"filename:.git-credentials {domain_filter} {placeholders}"
        ],
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain_filter} {placeholders}",
            f"HEROKU_API_KEY language:shell {domain_filter} {placeholders}",
            f"HEROKU_API_KEY language:json {domain_filter} {placeholders}",
            f"xoxp OR xoxb {domain_filter} {placeholders}",
            f"filename:github-recovery-codes.txt {domain_filter} {placeholders}",
            f"filename:gitlab-recovery-codes.txt {domain_filter} {placeholders}",
            f"filename:discord_backup_codes.txt {domain_filter} {placeholders}"
        ],
        "Database and Server Configurations": [
            f"extension:sql mysql dump {domain_filter} {placeholders}",
            f"extension:sql mysql dump password {domain_filter} {placeholders}",
            f"filename:config.json NOT encrypted NOT secure {domain_filter} {placeholders}",
            f"API_BASE_URL {domain_filter} {placeholders}",
            f"filename:azure-pipelines.yml {domain_filter} {placeholders}",
            f"filename:.aws/config {domain_filter} {placeholders}"
        ],
        "Security and Code Vulnerabilities": [
            f"password 'admin' {domain_filter} {placeholders}",
            f"filename:debug.log {domain_filter} {placeholders}",
            f"pre-shared key {domain_filter} {placeholders}",
            f"filename:*.config \"https://internal.{domain}\" {placeholders}",
            f"language:java \"// TODO: remove before production {domain}\" {placeholders}",
            f"\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3} {domain_filter} {placeholders}",  # IP Address patterns
            f"filename:main.tf aws_access_key_id {domain_filter} {placeholders}"
        ],
        "Historical Data and Leakage": [
            f"\"{domain_filter}.com email\" {placeholders}",
            f"filename:.env DB_PASSWORD NOT current {domain_filter} {placeholders}",
            f"filename:backup.zip {domain_filter} {placeholders}",
            f"filename:dump.sql {domain_filter} {placeholders}",
            f"filename:old_passwords.txt {domain_filter} {placeholders}"
        ],
        "Custom and Regex-Based Searches": [
            f"1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} login {domain_filter} {placeholders}",
            f"SSO 1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} {domain_filter} {placeholders}"
        ]
    }
