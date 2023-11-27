#gitsleuth_groups.py
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

    return {
        "Authentication and Credentials": [
            f"filename:.npmrc _auth {domain} {placeholders}",
            f"filename:.dockercfg auth {domain} {placeholders}",
            f"extension:pem private {domain} {placeholders}",
            f"extension:ppk private {domain} {placeholders}",
            f"filename:id_rsa OR filename:id_dsa {domain} {placeholders}",
            f"filename:wp-config.php {domain} {placeholders}",
            f"filename:.htpasswd {domain} {placeholders}",
            f"filename:.env DB_USERNAME NOT homestead {domain} {placeholders}",
            f"filename:credentials aws_access_key_id {domain} {placeholders}",
            f"filename:.s3cfg {domain} {placeholders}",
            f"filename:.git-credentials {domain} {placeholders}"
        ],
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain} {placeholders}",
            f"HEROKU_API_KEY language:shell {domain} {placeholders}",
            f"HEROKU_API_KEY language:json {domain} {placeholders}",
            f"xoxp OR xoxb {domain} {placeholders}",
            f"filename:github-recovery-codes.txt {domain} {placeholders}",
            f"filename:gitlab-recovery-codes.txt {domain} {placeholders}",
            f"filename:discord_backup_codes.txt {domain} {placeholders}"
        ],
        "Database and Server Configurations": [
            f"extension:sql mysql dump {domain} {placeholders}",
            f"extension:sql mysql dump password {domain} {placeholders}",
            f"filename:config.json NOT encrypted NOT secure {domain} {placeholders}",
            f"API_BASE_URL {domain} {placeholders}",
            f"filename:azure-pipelines.yml {domain} {placeholders}",
            f"filename:.aws/config {domain} {placeholders}"
        ],
        "Security and Code Vulnerabilities": [
            f"password 'admin' {domain} {placeholders}",
            f"filename:debug.log {domain} {placeholders}",
            f"pre-shared key {domain} {placeholders}",
            f"filename:*.config \"https://internal.{domain}\" {placeholders}",
            f"language:java \"// TODO: remove before production {domain}\" {placeholders}",
            f"\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3} {domain} {placeholders}",  # IP Address patterns
            f"filename:main.tf aws_access_key_id {domain} {placeholders}"
        ],
        "Historical Data and Leakage": [
            f"\"{domain}.com email\" {placeholders}",
            f"filename:.env DB_PASSWORD NOT current {domain} {placeholders}",
            f"filename:backup.zip {domain} {placeholders}",
            f"filename:dump.sql {domain} {placeholders}",
            f"filename:old_passwords.txt {domain} {placeholders}"
        ],
        "Custom and Regex-Based Searches": [
            f"1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} login {domain} {placeholders}",
            f"SSO 1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} {domain} {placeholders}"
        ]
    }
