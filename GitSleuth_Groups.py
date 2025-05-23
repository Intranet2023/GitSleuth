# GitSleuth_Groups.py

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
    """Return categorized GitHub search queries.

    Parameters
    ----------
    keywords : str
        Extra keywords or a domain to narrow the search.

    Returns
    -------
    dict
        Mapping of group name to list of query strings.
    """

    placeholders = "NOT example NOT dummy NOT test NOT sample NOT placeholder"
    domain_filter = f'"{keywords}"' if keywords else ""

    return {
        "Cloud Credentials (AWS, Azure, GCP)": [
            f"filename:.env AWS_ACCESS_KEY_ID {domain_filter} {placeholders}",
            f"filename:credentials aws_access_key_id {domain_filter} {placeholders}",
            f"language:Python \"AWS_SECRET_ACCESS_KEY\" {domain_filter} {placeholders}",
            f"org:{keywords} AWS_ACCESS_KEY_ID" if keywords else "AWS_ACCESS_KEY_ID",
            f"\"AKIA\" \"AWS_SECRET_ACCESS_KEY\" {domain_filter} {placeholders}",
            f"\"DefaultEndpointsProtocol=https\" \"AccountKey=\" {domain_filter} {placeholders}",
            f"filename:.env AZURE_CLIENT_SECRET {domain_filter} {placeholders}",
            f"filename:*.json private_key \"-----BEGIN PRIVATE KEY-----\" {domain_filter} {placeholders}",
            f"filename:credentials.json \"type\": \"service_account\" {domain_filter} {placeholders}",
            f"AIza {domain_filter} {placeholders}",
        ],
        "Third-Party API Keys and Tokens": [
            f"sk_live_ {domain_filter} {placeholders}",
            f"xoxb- OR xoxp- {domain_filter} {placeholders}",
            f"hooks.slack.com/services/ {domain_filter} {placeholders}",
            f"SG. {domain_filter} {placeholders}",
            f"OPENAI_API_KEY {domain_filter} {placeholders}",
            f"ghp_ {domain_filter} {placeholders}",
            f"TWILIO_AUTH_TOKEN {domain_filter} {placeholders}",
            f"org:{keywords} \"sk_live_\"" if keywords else "sk_live_",
            f"repo:{keywords}/{keywords} \"ghp_\"" if keywords and '/' in keywords else "ghp_",
            f"shodan_api_key language:Python {domain_filter} {placeholders}",
        ],
        "OAuth Credentials": [
            f"extension:json googleusercontent client_secret {domain_filter} {placeholders}",
            f"filename:client_secrets.json \"client_secret\" {domain_filter} {placeholders}",
            f"CLIENT_SECRET {domain_filter} {placeholders}",
            f"consumer_key {domain_filter} {placeholders}",
            f"consumer_secret {domain_filter} {placeholders}",
            f"org:{keywords} \"client_secret\"" if keywords else "client_secret",
        ],
        "Database Credentials & Connection Strings": [
            f"filename:.env DB_PASSWORD {domain_filter} {placeholders}",
            f"filename:.env DB_USERNAME NOT homestead {domain_filter} {placeholders}",
            f"filename:wp-config.php {domain_filter} {placeholders}",
            f"filename:configuration.php JConfig password {domain_filter} {placeholders}",
            f"filename:config.php dbpasswd {domain_filter} {placeholders}",
            f"filename:application.properties password {domain_filter} {placeholders}",
            f"extension:sql \"password\" {domain_filter} {placeholders}",
            f"filename:.pgpass {domain_filter} {placeholders}",
            f"repo:{keywords}/{keywords} \"jdbc:mysql://\"" if keywords and '/' in keywords else "jdbc:mysql://",
        ],
        "SSH Keys and Certificates": [
            f"filename:id_rsa OR filename:id_dsa {domain_filter} {placeholders}",
            f"extension:pem \"PRIVATE KEY\" {domain_filter} {placeholders}",
            f"extension:ppk \"PRIVATE KEY\" {domain_filter} {placeholders}",
            f"filename:server.key {domain_filter} {placeholders}",
            f"filename:hub oauth_token {domain_filter} {placeholders}",
        ],
        "Email/SMTP Credentials": [
            f"filename:.env MAIL_HOST=smtp.gmail.com {domain_filter} {placeholders}",
            f"filename:.env MAIL_PASSWORD {domain_filter} {placeholders}",
            f"EMAIL_HOST_PASSWORD {domain_filter} {placeholders}",
            f"SMTP_PASSWORD {domain_filter} {placeholders}",
            f"filename:.esmtprc password {domain_filter} {placeholders}",
        ],
        "JWT and Application Secrets": [
            f"filename:settings.py SECRET_KEY {domain_filter} {placeholders}",
            f"filename:.env JWT_SECRET {domain_filter} {placeholders}",
            f"filename:.env APP_KEY {domain_filter} {placeholders}",
            f"JWT_SECRET {domain_filter} {placeholders}",
            f"APP_SECRET {domain_filter} {placeholders}",
            f"FLASK_SECRET_KEY {domain_filter} {placeholders}",
        ],
        "Secrets in Infrastructure-as-Code": [
            f"filename:terraform.tfvars {domain_filter} {placeholders}",
            f"filename:terraform.tfstate {domain_filter} {placeholders}",
            f"extension:tf aws_secret_key {domain_filter} {placeholders}",
            f"filename:vars.yml password {domain_filter} {placeholders}",
            f"filename:docker-compose.yml MYSQL_PASSWORD {domain_filter} {placeholders}",
            f"stringData: {domain_filter} {placeholders}",
        ],
        "Secrets in CI/CD Configurations": [
            f"path:.github/workflows AWS_ACCESS_KEY_ID {domain_filter} {placeholders}",
            f"filename:.gitlab-ci.yml AWS_SECRET_ACCESS_KEY {domain_filter} {placeholders}",
            f"filename:Jenkinsfile password {domain_filter} {placeholders}",
            f"HEROKU_API_KEY language:shell {domain_filter} {placeholders}",
            f"repo:{keywords}/{keywords} \"CI_SECRET\"" if keywords and '/' in keywords else "CI_SECRET",
        ],
        "Secrets in Commit History, Issues, or Gists": [
            f"type:commit \"API key\" {domain_filter} {placeholders}",
            f"type:commit password {domain_filter} {placeholders}",
            f"org:{keywords} type:commit \"SECRET_KEY\"" if keywords else "type:commit \"SECRET_KEY\"",
            f"type:issue \"AWS_SECRET_ACCESS_KEY\" {domain_filter} {placeholders}",
            f"site:gist.github.com \"API_KEY\"",
        ],
        "Hardcoded Passwords or Bearer Tokens": [
            f"password = language:Java {domain_filter} {placeholders}",
            f"password extension:ini {domain_filter} {placeholders}",
            f"\"Authorization: Bearer\" {domain_filter} {placeholders}",
            f"Authorization Bearer token {domain_filter} {placeholders}",
            f"authToken = {domain_filter} {placeholders}",
        ],
        "Internationalized Secret Keywords": [
            f"senha {domain_filter} {placeholders}",
            f"contrase\u00f1a {domain_filter} {placeholders}",
            f"\u043f\u0430\u0440\u043e\u043b\u044c {domain_filter} {placeholders}",
            f"senha = {domain_filter} {placeholders}",
            f"contrase\u00f1a = {domain_filter} {placeholders}",
        ],
        "General Configuration & Credential Files": [
            f"filename:.git-credentials {domain_filter} {placeholders}",
            f"filename:.npmrc _authToken {domain_filter} {placeholders}",
            f"filename:.bash_history {domain_filter} {placeholders}",
            f"filename:.bashrc password {domain_filter} {placeholders}",
            f"filename:.netrc password {domain_filter} {placeholders}",
            f"filename:config.json \"auths\" {domain_filter} {placeholders}",
            f"filename:settings.py DATABASES {domain_filter} {placeholders}",
            f"filename:prod.secret.exs {domain_filter} {placeholders}",
        ],

    }
