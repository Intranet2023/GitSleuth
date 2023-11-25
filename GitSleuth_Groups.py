#GetSleuth_Groups.py 
def create_search_queries(domain):
    """
    Creates a dictionary of search queries for different categories, incorporating the given domain.

    Parameters:
    domain (str): The domain to be included in the search queries.

    Returns:
    dict: A dictionary where each key is a category and the value is a list of search queries.
    """
    return {
        "Authentication Data": [
            f"filename:.npmrc _auth {domain}",
            f"filename:.dockercfg auth {domain}"
        ],
        "Private Keys": [
            f"extension:pem private {domain}",
            f"extension:ppk private {domain}",
            f"filename:id_rsa OR filename:id_dsa {domain}"
        ],
        "Configuration Files": [
            f"filename:wp-config.php {domain}",
            f"filename:.htpasswd {domain}",
            f"filename:.env DB_USERNAME NOT homestead {domain}"
        ],
        "Credentials": [
            f"filename:credentials aws_access_key_id {domain}",
            f"filename:.s3cfg {domain}",
            f"filename:.git-credentials {domain}"
        ],
        "Database Related": [
            f"extension:sql mysql dump {domain}",
            f"extension:sql mysql dump password {domain}"
        ],
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain}",
            f"HEROKU_API_KEY language:shell {domain}",
            f"HEROKU_API_KEY language:json {domain}"
        ],
        "Recovery Keys": [
            f"filename:github-recovery-codes.txt {domain}",
            f"filename:gitlab-recovery-codes.txt {domain}",
            f"filename:discord_backup_codes.txt {domain}"
        ],
        "Unencrypted Configuration Files": [
            f"filename:config.json NOT encrypted NOT secure {domain}"
        ],
        "Exposed API Endpoints": [
            f"API_BASE_URL {domain}"
        ],
        "Default Passwords in Code": [
            f"password 'admin' {domain}"
        ],
        "Leaked Tokens": [
            f"xoxp OR xoxb {domain}"
        ],
        "Debug Information": [
            f"filename:debug.log {domain}"
        ],
        "Custom Search": [
            f"pre-shared key NOT example NOT placeholder {domain}"
        ]
    }
