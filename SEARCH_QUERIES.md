# GitHub Code Search Query Templates

This document lists example search queries for locating secrets in public repositories. Replace `{ORG_NAME}` or `{USERNAME}` with your target organization or user.

| Purpose | Query Template | Notes |
| --- | --- | --- |
| **AWS Credentials** | `org:{ORG_NAME} "AWS_SECRET_ACCESS_KEY"` | Look for AWS secret keys. Searching for the prefix `AKIA` can also reveal access keys. |
| **Database Passwords in .env** | `org:{ORG_NAME} filename:.env DB_PASSWORD` | Finds environment files with DB credentials. |
| **Generic API Keys** | `filename:config.json auth` | Search config files for authentication sections. |
| **OAuth Client Secrets** | `client_secret extension:json` | Captures OAuth or API secrets stored in JSON. |
| **Django Secret Key** | `filename:settings.py "SECRET_KEY"` | Django applications should keep this value private. |
| **SSH Private Keys** | `(filename:id_rsa OR filename:id_dsa) "PRIVATE KEY"` | Detects committed private SSH keys. |
| **PEM Private Keys** | `extension:pem "PRIVATE KEY"` | Looks for PEM files containing private keys. |
| **Slack Tokens** | `user:{USERNAME} "xoxb-"` | Finds Slack bot tokens in a user’s repositories. |
| **Slack Webhooks** | `"hooks.slack.com/services"` | Slack incoming webhook URLs contain tokens. |
| **Stripe API Keys** | `"sk_live_"` | Matches Stripe live secret keys. |
| **Google API Keys** | `"AIza"` | Finds Google API keys. |
| **WordPress Config** | `filename:wp-config.php` | Contains database credentials and salts. |
| **Passwords in SQL** | `password extension:sql` | Searches for password fields in SQL dumps. |

| **Authentication and Credentials** | `filename:.npmrc _auth` | npm auth token |
| **Authentication and Credentials** | `filename:.dockercfg auth` | Docker credentials |
| **Authentication and Credentials** | `extension:pem private` | PEM private key |
| **Authentication and Credentials** | `extension:ppk private` | PuTTY private key |
| **Authentication and Credentials** | `filename:id_rsa OR filename:id_dsa` | SSH private key |
| **Authentication and Credentials** | `filename:.htpasswd` | htpasswd file |
| **Authentication and Credentials** | `filename:.env DB_USERNAME NOT homestead` | .env DB credentials |
| **Authentication and Credentials** | `filename:credentials aws_access_key_id` | AWS credentials file |
| **Authentication and Credentials** | `filename:.s3cfg` | S3 config |
| **Authentication and Credentials** | `filename:.git-credentials` | Git credentials |
| **API Keys and Tokens** | `extension:json api.forecast.io` | forecast.io API key |
| **API Keys and Tokens** | `HEROKU_API_KEY language:shell` | Heroku API key in shell script |
| **API Keys and Tokens** | `HEROKU_API_KEY language:json` | Heroku API key in JSON |
| **API Keys and Tokens** | `xoxp OR xoxb` | Slack token |
| **API Keys and Tokens** | `filename:github-recovery-codes.txt` | GitHub recovery codes |
| **API Keys and Tokens** | `filename:gitlab-recovery-codes.txt` | GitLab recovery codes |
| **API Keys and Tokens** | `filename:discord_backup_codes.txt` | Discord backup codes |
| **API Keys and Tokens** | `hooks.slack.com/services` | Slack webhook |
| **API Keys and Tokens** | `sk_live_` | Stripe live secret key |
| **API Keys and Tokens** | `AIza` | Google API key |
| **Database and Server Configurations** | `extension:sql mysql dump` | MySQL dump |
| **Database and Server Configurations** | `extension:sql mysql dump password` | MySQL dump with passwords |
| **Database and Server Configurations** | `filename:config.json NOT encrypted NOT secure` | Insecure config file |
| **Database and Server Configurations** | `API_BASE_URL` | API base URL |
| **Database and Server Configurations** | `filename:azure-pipelines.yml` | Azure pipeline config |
| **Database and Server Configurations** | `filename:.aws/config` | AWS CLI config |
| **Private Keys** | `"-----BEGIN RSA PRIVATE KEY-----"` | RSA private key |
| **Private Keys** | `extension:pfx` | PFX certificate |
| **Private Keys** | `extension:jks` | Java KeyStore |
| **Security and Code Vulnerabilities** | `password 'admin'` | Hardcoded admin password |
| **Security and Code Vulnerabilities** | `filename:debug.log` | Debug log |
| **Security and Code Vulnerabilities** | `pre-shared key` | Pre-shared key |
| **Security and Code Vulnerabilities** | `language:java "// TODO: remove before production "` | TODO in code |
| **Security and Code Vulnerabilities** | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | IP address pattern |
| **Security and Code Vulnerabilities** | `filename:main.tf aws_access_key_id` | Terraform with AWS key |
| **Historical Data and Leakage** | `".com email"` | Email addresses from domain |
| **Historical Data and Leakage** | `filename:.env DB_PASSWORD NOT current` | Old DB passwords |
| **Historical Data and Leakage** | `filename:backup.zip` | Backup zip |
| **Historical Data and Leakage** | `filename:dump.sql` | SQL dump |
| **Historical Data and Leakage** | `filename:old_passwords.txt` | Old passwords |
| **Custom and Regex-Based Searches** | `1[0-9]{8}|2[0-9]{8}|3[0-9]{8}|4[0-9]{8}|5[0-9]{8}|6[0-9]{8} login` | Employee login pattern |
| **Custom and Regex-Based Searches** | `SSO 1[0-9]{8}|2[0-9]{8}|3[0-9]{8}|4[0-9]{8}|5[0-9]{8}|6[0-9]{8}` | SSO login pattern |

| **Cloud Credentials (AWS, Azure, GCP)** | `filename:.env AWS_ACCESS_KEY_ID` | Searches environment files for AWS access key IDs. |
| **Cloud Credentials (AWS, Azure, GCP)** | `language:Python "AWS_SECRET_ACCESS_KEY"` | Finds AWS secret keys embedded in Python code. |
| **Cloud Credentials (AWS, Azure, GCP)** | `AWS_ACCESS_KEY_ID` | General search for AWS access key IDs. |
| **Cloud Credentials (AWS, Azure, GCP)** | `"AKIA" "AWS_SECRET_ACCESS_KEY"` | Looks for AWS key ID prefixes paired with secret keys. |
| **Cloud Credentials (AWS, Azure, GCP)** | `"DefaultEndpointsProtocol=https" "AccountKey="` | Detects Azure storage connection strings. |
| **Cloud Credentials (AWS, Azure, GCP)** | `filename:.env AZURE_CLIENT_SECRET` | Environment files with Azure client secrets. |
| **Cloud Credentials (AWS, Azure, GCP)** | `filename:*.json private_key "-----BEGIN PRIVATE KEY-----"` | JSON files containing embedded private key blocks. |
| **Cloud Credentials (AWS, Azure, GCP)** | `filename:credentials.json "type": "service_account"` | Google Cloud service account credential files. |
| **Third-Party API Keys and Tokens** | `xoxb- OR xoxp-` | Slack bot or user tokens. |
| **Third-Party API Keys and Tokens** | `hooks.slack.com/services/` | Slack webhook URLs with tokens. |
| **Third-Party API Keys and Tokens** | `SG.` | SendGrid API keys. |
| **Third-Party API Keys and Tokens** | `OPENAI_API_KEY` | OpenAI API keys. |
| **Third-Party API Keys and Tokens** | `ghp_` | GitHub personal access tokens. |
| **Third-Party API Keys and Tokens** | `TWILIO_AUTH_TOKEN` | Twilio API auth tokens. |
| **Third-Party API Keys and Tokens** | `shodan_api_key language:Python` | Shodan API keys in Python projects. |
| **Third-Party API Keys and Tokens** | `VERCEL_API_TOKEN` | Vercel deployment API tokens. |
| **Third-Party API Keys and Tokens** | `HUGGINGFACEHUB_API_TOKEN` | Hugging Face API tokens. |
| **Third-Party API Keys and Tokens** | `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role keys. |
| **Third-Party API Keys and Tokens** | `SENTRY_DSN` | Sentry DSN containing secrets. |
| **Third-Party API Keys and Tokens** | `ROLLBAR_ACCESS_TOKEN` | Rollbar access tokens. |
| **Third-Party API Keys and Tokens** | `GLPAT-` | GitLab personal access tokens. |
| **Third-Party API Keys and Tokens** | `CLOUDFLARE_API_TOKEN` | Cloudflare API tokens. |
| **Third-Party API Keys and Tokens** | `VAULT_TOKEN` | Vault tokens. |
| **Third-Party API Keys and Tokens** | `PINECONE_API_KEY` | Pinecone API keys. |

| **OAuth Credentials** | `extension:json googleusercontent client_secret` | Google OAuth client secrets in JSON. |
| **OAuth Credentials** | `filename:client_secrets.json "client_secret"` | Typical Google OAuth client_secrets.json file. |
| **OAuth Credentials** | `CLIENT_SECRET` | Files referencing a generic client secret. |
| **OAuth Credentials** | `consumer_key` | OAuth consumer key strings. |
| **OAuth Credentials** | `consumer_secret` | OAuth consumer secret strings. |
| **OAuth Credentials** | `client_secret` | Generic client secret identifier. |
| **Database Credentials & Connection Strings** | `filename:.env DB_PASSWORD` | Database passwords stored in .env files. |
| **Database Credentials & Connection Strings** | `filename:configuration.php JConfig password` | Joomla configuration file with database password. |
| **Database Credentials & Connection Strings** | `filename:config.php dbpasswd` | PHP config files exposing $dbpasswd. |
| **Database Credentials & Connection Strings** | `filename:application.properties password` | Java/Spring config with database password. |
| **Database Credentials & Connection Strings** | `extension:sql "password"` | SQL files with password strings. |
| **Database Credentials & Connection Strings** | `filename:.pgpass` | Postgres password files. |
| **Database Credentials & Connection Strings** | `jdbc:mysql://` | Hard-coded MySQL connection strings. |
| **SSH Keys and Certificates** | `extension:ppk "PRIVATE KEY"` | PuTTY private key files. |
| **SSH Keys and Certificates** | `filename:server.key` | Generic server private key files. |
| **SSH Keys and Certificates** | `filename:hub oauth_token` | Hub CLI config storing OAuth token. |
| **Email/SMTP Credentials** | `filename:.env MAIL_HOST=smtp.gmail.com` | Gmail SMTP host settings in .env files. |
| **Email/SMTP Credentials** | `filename:.env MAIL_PASSWORD` | Mail service passwords in .env files. |
| **Email/SMTP Credentials** | `EMAIL_HOST_PASSWORD` | Common variable for email account passwords. |
| **Email/SMTP Credentials** | `SMTP_PASSWORD` | SMTP password strings. |
| **Email/SMTP Credentials** | `filename:.esmtprc password` | esmtp configuration files with passwords. |
| **JWT and Application Secrets** | `filename:settings.py SECRET_KEY` | Django secret keys in settings. |
| **JWT and Application Secrets** | `filename:.env JWT_SECRET` | JWT secrets in environment files. |
| **JWT and Application Secrets** | `filename:.env APP_KEY` | Laravel application keys in .env. |
| **JWT and Application Secrets** | `JWT_SECRET` | Generic JWT secret key variable. |
| **JWT and Application Secrets** | `APP_SECRET` | Generic application secret variable. |
| **JWT and Application Secrets** | `FLASK_SECRET_KEY` | Flask application secret keys. |
| **Secrets in Infrastructure-as-Code** | `filename:terraform.tfvars` | Terraform variable files with sensitive values. |
| **Secrets in Infrastructure-as-Code** | `filename:terraform.tfstate` | Terraform state files containing secrets. |
| **Secrets in Infrastructure-as-Code** | `extension:tf aws_secret_key` | Terraform files with AWS secret keys. |
| **Secrets in Infrastructure-as-Code** | `filename:vars.yml password` | Ansible variable files with passwords. |
| **Secrets in Infrastructure-as-Code** | `filename:docker-compose.yml MYSQL_PASSWORD` | Docker Compose files exposing MySQL passwords. |
| **Secrets in Infrastructure-as-Code** | `stringData:` | Kubernetes secrets defined with plaintext stringData. |
| **Secrets in CI/CD Configurations** | `path:.github/workflows AWS_ACCESS_KEY_ID` | GitHub Actions workflows exposing AWS keys. |
| **Secrets in CI/CD Configurations** | `filename:.gitlab-ci.yml AWS_SECRET_ACCESS_KEY` | GitLab CI configuration leaking AWS secrets. |
| **Secrets in CI/CD Configurations** | `filename:Jenkinsfile password` | Passwords hard-coded in Jenkins pipelines. |
| **Secrets in CI/CD Configurations** | `CI_SECRET` | Generic CI secrets. |
| **Secrets in Commit History, Issues, or Gists** | `type:commit "API key"` | Commits mentioning API keys. |
| **Secrets in Commit History, Issues, or Gists** | `type:commit password` | Commit history referencing passwords. |
| **Secrets in Commit History, Issues, or Gists** | `type:commit "SECRET_KEY"` | Commits mentioning secret keys. |
| **Secrets in Commit History, Issues, or Gists** | `type:issue "AWS_SECRET_ACCESS_KEY"` | GitHub issues exposing AWS secret keys. |
| **Secrets in Commit History, Issues, or Gists** | `site:gist.github.com "API_KEY"` | Public gists containing API keys. |
| **Hardcoded Passwords or Bearer Tokens** | `password = language:Java` | Java code with hardcoded password assignments. |
| **Hardcoded Passwords or Bearer Tokens** | `password extension:ini` | INI files containing password entries. |
| **Hardcoded Passwords or Bearer Tokens** | `"Authorization: Bearer"` | Bearer tokens hardcoded in code. |
| **Hardcoded Passwords or Bearer Tokens** | `Authorization Bearer token` | Bearer token strings without quotes. |
| **Hardcoded Passwords or Bearer Tokens** | `authToken =` | authToken variables set in code. |
| **Internationalized Secret Keywords** | `senha` | Portuguese term for password. |
| **Internationalized Secret Keywords** | `contraseña` | Spanish term for password. |
| **Internationalized Secret Keywords** | `пароль` | Russian term for password. |
| **Internationalized Secret Keywords** | `senha =` | Assignments using Portuguese password term. |
| **Internationalized Secret Keywords** | `contraseña =` | Assignments using Spanish password term. |
| **General Configuration & Credential Files** | `filename:.npmrc _authToken` | NPM config files with auth tokens. |
| **General Configuration & Credential Files** | `filename:.bash_history` | Shell history files containing commands. |
| **General Configuration & Credential Files** | `filename:.bashrc password` | Shell rc files referencing passwords. |
| **General Configuration & Credential Files** | `filename:.netrc password` | Netrc files storing passwords. |
| **General Configuration & Credential Files** | `filename:config.json "auths"` | Docker config.json with auth tokens. |
| **General Configuration & Credential Files** | `filename:settings.py DATABASES` | Django settings with database config. |
| **General Configuration & Credential Files** | `filename:prod.secret.exs` | Phoenix/Elixir production secret files. |

## Tips for Effective Queries

- Use specific identifiers and file filters to reduce noise.
- Include company terms or domains to narrow results.
- Exclude known placeholders with the `NOT` operator.
- Combine related terms with `OR` when possible.

## Managing Rate Limits

Authenticated search requests are limited to about **30 per minute**. Space your queries or pause when the limit is reached. Adding `per_page=100` to API calls reduces the number of requests required.

