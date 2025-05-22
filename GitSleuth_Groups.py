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

    placeholders = "NOT example NOT dummy NOT test NOT sample NOT placeholder"
    filter_part = f'"{keywords}"' if keywords else ""


    return {
        "Authentication and Credentials": [
            (f"filename:.npmrc _auth {filter_part} {placeholders}", "npm auth token"),
            (f"filename:.dockercfg auth {filter_part} {placeholders}", "Docker credentials"),
            (f"extension:pem private {filter_part} {placeholders}", "PEM private key"),
            (f"extension:ppk private {filter_part} {placeholders}", "PuTTY private key"),
            (
                f"filename:id_rsa OR filename:id_dsa {filter_part} {placeholders}",
                "SSH private key",
            ),
            (f"filename:wp-config.php {filter_part} {placeholders}", "WordPress config"),
            (f"filename:.htpasswd {filter_part} {placeholders}", "htpasswd file"),
            (
                f"filename:.env DB_USERNAME NOT homestead {filter_part} {placeholders}",
                ".env DB credentials",
            ),
            (
                f"filename:credentials aws_access_key_id {filter_part} {placeholders}",
                "AWS credentials file",
            ),
            (f"filename:.s3cfg {filter_part} {placeholders}", "S3 config"),
            (f"filename:.git-credentials {filter_part} {placeholders}", "Git credentials"),
        ],
        "API Keys and Tokens": [
            (
                f"extension:json api.forecast.io {filter_part} {placeholders}",
                "forecast.io API key",
            ),
            (
                f"HEROKU_API_KEY language:shell {filter_part} {placeholders}",
                "Heroku API key in shell script",
            ),
            (
                f"HEROKU_API_KEY language:json {filter_part} {placeholders}",
                "Heroku API key in JSON",
            ),
            (f"xoxp OR xoxb {filter_part} {placeholders}", "Slack token"),
            (
                f"filename:github-recovery-codes.txt {filter_part} {placeholders}",
                "GitHub recovery codes",
            ),
            (
                f"filename:gitlab-recovery-codes.txt {filter_part} {placeholders}",
                "GitLab recovery codes",
            ),
            (
                f"filename:discord_backup_codes.txt {filter_part} {placeholders}",
                "Discord backup codes",
            ),
            (f"hooks.slack.com/services {filter_part} {placeholders}", "Slack webhook"),
            (f"sk_live_ {filter_part} {placeholders}", "Stripe live secret key"),
            (f"AIza {filter_part} {placeholders}", "Google API key"),
            (
                f"client_secret extension:json {filter_part} {placeholders}",
                "OAuth client secret in JSON",
            ),
        ],
        "Database and Server Configurations": [
            (f"extension:sql mysql dump {filter_part} {placeholders}", "MySQL dump"),
            (
                f"extension:sql mysql dump password {filter_part} {placeholders}",
                "MySQL dump with passwords",
            ),
            (
                f"password extension:sql {filter_part} {placeholders}",
                "SQL file with password",
            ),
            (
                f"filename:config.json NOT encrypted NOT secure {filter_part} {placeholders}",
                "Insecure config file",
            ),
            (f"API_BASE_URL {filter_part} {placeholders}", "API base URL"),
            (
                f"filename:azure-pipelines.yml {filter_part} {placeholders}",
                "Azure pipeline config",
            ),
            (f"filename:.aws/config {filter_part} {placeholders}", "AWS CLI config"),
        ],
        "Private Keys": [
            (f"\"-----BEGIN RSA PRIVATE KEY-----\" {placeholders}", "RSA private key"),
            (f"extension:pfx {placeholders}", "PFX certificate"),
            (f"extension:jks {placeholders}", "Java KeyStore"),
        ],
        "Security and Code Vulnerabilities": [
            (
                f"password 'admin' {filter_part} {placeholders}",
                "Hardcoded admin password",
            ),
            (f"filename:debug.log {filter_part} {placeholders}", "Debug log"),
            (f"pre-shared key {filter_part} {placeholders}", "Pre-shared key"),
            (
                f"language:java \"// TODO: remove before production {keywords}\" {placeholders}",
                "TODO in code",
            ),
            (
                f"\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}} {filter_part} {placeholders}",
                "IP address pattern",
            ),
            (
                f"filename:main.tf aws_access_key_id {filter_part} {placeholders}",
                "Terraform with AWS key",
            ),
        ],
        "Historical Data and Leakage": [
            (
                f"\"{filter_part}.com email\" {placeholders}",
                "Email addresses from domain",
            ),
            (
                f"filename:.env DB_PASSWORD NOT current {filter_part} {placeholders}",
                "Old DB passwords",
            ),
            (f"filename:backup.zip {filter_part} {placeholders}", "Backup zip"),
            (f"filename:dump.sql {filter_part} {placeholders}", "SQL dump"),
            (f"filename:old_passwords.txt {filter_part} {placeholders}", "Old passwords"),
        ],
        "Custom and Regex-Based Searches": [
            (
                f"1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} login {filter_part} {placeholders}",
                "Employee login pattern",
            ),
            (
                f"SSO 1[0-9]{{8}}|2[0-9]{{8}}|3[0-9]{{8}}|4[0-9]{{8}}|5[0-9]{{8}}|6[0-9]{{8}} {filter_part} {placeholders}",
                "SSO login pattern",
            ),
        ],
    }
