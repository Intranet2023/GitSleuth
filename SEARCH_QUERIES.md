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

## Tips for Effective Queries

- Use specific identifiers and file filters to reduce noise.
- Include company terms or domains to narrow results.
- Exclude known placeholders with the `NOT` operator.
- Combine related terms with `OR` when possible.

## Managing Rate Limits

Authenticated search requests are limited to about **30 per minute**. Space your queries or pause when the limit is reached. Adding `per_page=100` to API calls reduces the number of requests required.

