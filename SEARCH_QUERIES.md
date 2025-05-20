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

## Tips for Effective Queries

- Use specific identifiers and file filters to reduce noise.
- Include company terms or domains to narrow results.
- Exclude known placeholders with the `NOT` operator.
- Combine related terms with `OR` when possible.

## Managing Rate Limits

Authenticated search requests are limited to about **30 per minute**. Space your queries or pause when the limit is reached. Adding `per_page=100` to API calls reduces the number of requests required.
