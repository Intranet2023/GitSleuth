import os
import re

PLACEHOLDERS = "NOT example NOT dummy NOT test NOT sample NOT placeholder"


def load_query_descriptions():
    descriptions = {}
    path = os.path.join(os.path.dirname(__file__), "SEARCH_QUERIES.md")
    if not os.path.exists(path):
        return descriptions
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("| **") or line.startswith("| `"):
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 3:
                    query = parts[1]
                    if query.startswith('`') and query.endswith('`'):
                        query = query[1:-1]
                    descriptions[query] = parts[2]
    return descriptions

QUERY_DESCRIPTIONS = load_query_descriptions()


def get_query_description(query, domain=""):
    base = query.replace(f'"{domain}"', "").replace(domain, "")
    base = base.replace(PLACEHOLDERS, "").strip()
    base = " ".join(base.split())
    return QUERY_DESCRIPTIONS.get(base, "")


def create_search_queries(keywords):
    """
    Creates a dictionary of search queries for different categories,
    incorporating the provided keywords and applying strategies to exclude
    common placeholders.

    Parameters:
    - keywords (str): Keywords or domain terms to include in the search
      queries.

    Returns:
    - dict: A dictionary where each key is a category, and the value is a list of search queries.
    """
    placeholders = PLACEHOLDERS

    domain_filter = f'"{keywords}"' if keywords else ""
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
            f"filename:.npmrc _auth {domain} {placeholders}",
            f"filename:.dockercfg auth {domain} {placeholders}",
            f"extension:pem private {domain} {placeholders}",
            f"extension:ppk private {domain} {placeholders}",
            f"filename:id_rsa OR filename:id_dsa {domain} {placeholders}",
            f"filename:wp-config.php {domain} {placeholders}",
            f"filename:settings.py \"SECRET_KEY\" {domain} {placeholders}",
            f"filename:.htpasswd {domain} {placeholders}",
            f"filename:.env DB_USERNAME NOT homestead {domain} {placeholders}",
            f"filename:credentials aws_access_key_id {domain} {placeholders}",
            f"filename:.s3cfg {domain} {placeholders}",
            f"filename:.git-credentials {domain} {placeholders}",
            f"\"AWS_SECRET_ACCESS_KEY\" {domain} {placeholders}",
            f"AKIA {domain} {placeholders}",
        ],
        "Cloud Provider Secrets": [
            f"AWS_SECRET_ACCESS_KEY {domain} {placeholders}",
            f"AWS_ACCESS_KEY_ID {domain} {placeholders}",
            f"AZURE_CLIENT_SECRET {domain} {placeholders}",
            f"filename:credentials.json \"private_key_id\" {domain} {placeholders}"
        ],
        "Third-Party API Keys": [
            f"sk_live_ {domain} {placeholders}",
            f"xoxb- OR xoxp- {domain} {placeholders}",
            f"SG. {domain} {placeholders}"
        ],
        "API Keys and Tokens": [
            f"extension:json api.forecast.io {domain} {placeholders}",
            f"HEROKU_API_KEY language:shell {domain} {placeholders}",
            f"HEROKU_API_KEY language:json {domain} {placeholders}",
            f"xoxp OR xoxb {domain} {placeholders}",
            f"filename:github-recovery-codes.txt {domain} {placeholders}",
            f"filename:gitlab-recovery-codes.txt {domain} {placeholders}",
            f"filename:discord_backup_codes.txt {domain} {placeholders}",
            f"\"hooks.slack.com/services\" {domain} {placeholders}",
            f"sk_live_ {domain} {placeholders}",
            f"AIza {domain} {placeholders}",
            f"client_secret extension:json {domain} {placeholders}",
        ],
        "Database and Server Configurations": [
            f"extension:sql mysql dump {domain} {placeholders}",
            f"extension:sql mysql dump password {domain} {placeholders}",
            f"password extension:sql {domain} {placeholders}",
            f"filename:config.json NOT encrypted NOT secure {domain} {placeholders}",
            f"API_BASE_URL {domain} {placeholders}",
            f"filename:azure-pipelines.yml {domain} {placeholders}",
            f"filename:.aws/config {domain} {placeholders}"
        ],
        "Private Keys": [
            f"\"-----BEGIN RSA PRIVATE KEY-----\" {placeholders}",
            f"extension:pfx {placeholders}",
            f"extension:jks {placeholders}"
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
