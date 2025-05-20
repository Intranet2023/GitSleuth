# GitHub Code Search Queries for Sensitive Secrets

Below is a comprehensive list of GitHub code search query templates organized by secret type. These queries use advanced search operators (file name filters, extensions, boolean logic, and scope qualifiers) to find potential secret leaks in public repositories. **Placeholders** in curly braces should be replaced with actual values (e.g., an organization name for `{ORG_NAME}` or specific file names/extensions for `{FILENAME}`/{`{EXTENSION}`}). You can remove the `org:{ORG_NAME}` qualifier to search across all public repos, or replace it with `user:{USER_NAME}` or a specific `repo:{ORG_NAME}/{REPO_NAME}` as needed. Each query is accompanied by a brief description of what it targets.

## Cloud Provider Secrets (AWS, Azure, GCP)

Search queries to detect exposed credentials for major cloud providers like Amazon Web Services, Microsoft Azure, and Google Cloud Platform.

### AWS Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:credentials aws_access_key_id` | AWS CLI credentials file containing an AWS access key ID (and likely a secret key). |
| `filename:.env AWS_ACCESS_KEY_ID` | Environment files with AWS Access Key ID (possible AWS key in `.env`). |
| `AWS_SECRET_ACCESS_KEY=` | Code or config defining an AWS Secret Access Key (e.g., in env assignments). |
| `AWS_ACCESS_KEY_ID=` | Occurrences of AWS Access Key ID being set in code or config. |
| `AWS_SESSION_TOKEN=` | AWS session tokens in code (temporary credentials). |
| `AKIA` | Raw AWS Access Key IDs (which typically start with "AKIA") appearing in code. |
| `filename:.s3cfg` | AWS S3 config file (contains `access_key` and `secret_key`, often for s3cmd). |
| `rds.amazonaws.com password` | Potential AWS RDS database connection strings with passwords. |

### Azure Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} AZURE_CLIENT_SECRET` | Azure client/application secrets exposed (e.g., in env vars or config). |
| `DefaultEndpointsProtocol= AND AccountKey=` | Azure Storage/Cosmos DB connection string. |
| `AzureWebJobsStorage` | Azure WebJobs/Functions storage connection strings (contains keys). |
| `ARM_CLIENT_SECRET` | Azure service principal (Resource Manager) client secret. |

### GCP Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:credentials.json "private_key_id"` | Google Cloud service account JSON key file. |
| `filename:credentials.json "type": "service_account"` | Any JSON file labeled as a GCP service account. |
| `PRIVATE_KEY-----` | GCP private keys embedded in code or JSON. |
| `AIza` | Google API keys. |

## Third-Party API Keys and Tokens

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} sk_live_` | **Stripe** API secret keys. |
| `sk_test_` | Stripe API keys in test mode. |
| `xoxb- OR xoxp-` | **Slack** tokens – bot tokens or user tokens. |
| `ghp_ OR gho_ OR ghu_ OR ghs_ OR ghr_` | **GitHub** tokens. |
| `SG.` | **SendGrid** API keys. |
| `MAILGUN_API_KEY` | **Mailgun** API keys. |
| `TWILIO_AUTH_TOKEN` | **Twilio** API secret tokens. |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (often near an auth token). |
| `HEROKU_API_KEY` | **Heroku** API keys. |
| `SENDINBLUE_API_KEY` | **Sendinblue** API key leaks. |
| `FACEBOOK_APP_SECRET` | **Facebook** app secret keys. |
| `TWITTER_CONSUMER_SECRET` | **Twitter** API consumer secret. |
| `GOOGLE_API_KEY` | **Google** API keys named in code. |
| `OPENAI_API_KEY` | **OpenAI** API keys. |
| `DATADOG_API_KEY` | **Datadog** API keys. |
| `DATADOG_APP_KEY` | Datadog Application keys. |
| `NPM_TOKEN` | **npm** registry tokens. |
| `SLACK_API_TOKEN` | Slack API tokens or legacy Slack bot tokens. |
| `API_KEY` | Generic usage of "API_KEY" in code. |

## OAuth Client IDs and Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} GOOGLE_CLIENT_SECRET` | Google OAuth client secret. |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app client secret. |
| `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` | Facebook App ID and App Secret. |
| `TWITTER_CONSUMER_KEY` / `TWITTER_CONSUMER_SECRET` | Twitter API key and secret. |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn application client secret. |
| `extension:json "client_secret"` | JSON file containing a `client_secret` field. |
| `CLIENT_SECRET=` | Generic search for `CLIENT_SECRET` assignments. |
| `client_id AND client_secret` | Files containing both values. |

## Database Credentials and Connection Strings

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} DATABASE_URL=` | Environment variable for full database URI. |
| `DB_PASSWORD` | Exposed database password in environment/config. |
| `MYSQL_ROOT_PASSWORD` | MySQL root password in configs. |
| `POSTGRES_PASSWORD` | Postgres database password. |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB root user password in initialization. |
| `jdbc:mysql AND password=` | JDBC MySQL connection strings with credentials. |
| `jdbc:postgresql password=` | JDBC PostgreSQL connection string containing password. |
| `mongodb:// AND @` | MongoDB connection URI with credentials. |
| `postgres:// AND @` | PostgreSQL connection URI with credentials. |
| `mysql:// AND @` | MySQL connection URI containing credentials. |
| `filename:wp-config.php DB_PASSWORD NOT "password_here"` | WordPress configuration with real DB password. |
| `filename:.my.cnf password` | MySQL client config file with a password entry. |
| `filename:.pgpass` | Postgres password file. |
| `filename:configuration.php JConfig password` | Joomla configuration file containing DB credentials. |
| `filename:config.php dbpasswd` | PHP config file containing `$dbpasswd`. |

## Private Keys and Certificates

| Query Template | Description |
| --- | --- |
| `user:{USER_NAME} filename:id_rsa OR filename:id_dsa OR filename:id_ed25519` | Private SSH key files in user repositories. |
| `"-----BEGIN RSA PRIVATE KEY-----"` | RSA private keys in any file. |
| `"-----BEGIN DSA PRIVATE KEY-----"` | DSA private keys. |
| `"-----BEGIN EC PRIVATE KEY-----"` | Elliptic Curve private keys. |
| `"-----BEGIN OPENSSH PRIVATE KEY-----"` | OpenSSH private keys. |
| `extension:pem "PRIVATE KEY"` | PEM files containing a private key. |
| `extension:ppk` | PuTTY Private Key files. |
| `extension:pfx` | PKCS#12/PFX certificate stores. |
| `extension:p12` | PKCS#12 (.p12) files. |
| `extension:jks` | Java KeyStore files. |

## Email and SMTP Credentials

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:.env MAIL_HOST=smtp.gmail.com` | Gmail SMTP configuration in environment files. |
| `filename:.env MAIL_PASSWORD` | Environment files containing an email password. |
| `SMTP_PASSWORD` | SMTP password exposure in code or config. |
| `smtp.office365.com password` | Office365 SMTP settings with a password. |
| `filename:ssmtp.conf` | SSMTP mail configuration file with credentials. |

## JWT Secrets and Application Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} JWT_SECRET` | JWT secret keys exposed. |
| `JWT_SECRET_KEY` | JSON Web Token secret keys (alternative). |
| `SECRET_KEY = ` | Django secret key in `settings.py`. |
| `secret_key_base` | Rails secret key base. |
| `TOKEN_SECRET` | Generic token secret variable. |
| `AUTH_SECRET` | Generic auth secret key name. |
| `SESSION_SECRET` | Session secret keys in various frameworks. |

## Configuration Files and Other Sensitive Files

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:.env DB_USERNAME NOT homestead` | Environment files containing DB credentials. |
| `repo:{ORG_NAME}/{REPO_NAME} filename:.env` | Check a specific repo for a committed `.env` file. |
| `filename:.git-credentials NOT username` | Git credentials file. |
| `filename:.npmrc _auth` | npm configuration file with auth token. |
| `filename:.dockercfg auth` | Docker registry config with credentials. |
| `filename:.netrc password` | Netrc files storing passwords. |
| `filename:_netrc password` | Windows Netrc. |
| `filename:hub oauth_token` | Hub CLI config with OAuth token. |
| `filename:robomongo.json` | Robo 3T config with DB credentials. |
| `filename:filezilla.xml Pass` | FileZilla FTP client config with passwords. |
| `filename:recentservers.xml Pass` | FileZilla recent servers file with plain-text passwords. |
| `filename:.bash_profile AWS_ACCESS_KEY_ID` | Shell profile files containing AWS keys. |
| `filename:.bashrc password` | Shell rc files with password strings. |
| `filename:config.json auths` | Docker credential store. |
| `filename:configuration.php JConfig password` | Joomla configuration with DB password. |
| `filename:config.php dbpasswd` | PHP config file containing `$dbpasswd`. |

## Hardcoded Passwords and Tokens in Code

| Query Template | Description |
| --- | --- |
| `extension:py password = ` | Hardcoded password assignments in Python code. |
| `extension:js password =` | Hardcoded passwords in JavaScript code. |
| `extension:java password =` | Hardcoded passwords in Java source files. |
| `extension:yaml OR extension:yml password:` | Passwords in YAML configuration files. |
| `extension:json "password":` | Password strings in JSON files. |
| `extension:properties password=` | Hardcoded passwords in `.properties` config files. |
| `extension:ini password=` | Passwords in .ini files. |
| `password = "` | General search for password assignment. |
| `token = "` | Hardcoded token strings in code. |
| `Authorization: Bearer` | Hardcoded bearer tokens in code. |

