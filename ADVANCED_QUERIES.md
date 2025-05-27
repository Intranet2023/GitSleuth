# GitHub Code Search Queries for Sensitive Secrets

Below is a comprehensive list of GitHub code search query templates organized by secret type. These queries use advanced search operators (file name filters, extensions, boolean logic, and scope qualifiers) to find potential secret leaks in public repositories. **Placeholders** in curly braces should be replaced with actual values (e.g., an organization name for `{ORG_NAME}` or specific file names/extensions for `{FILENAME}`/{`{EXTENSION}`}). You can remove the `org:{ORG_NAME}` qualifier to search across all public repos, or replace it with `user:{USER_NAME}` or a specific `repo:{ORG_NAME}/{REPO_NAME}` as needed. Each query is accompanied by a brief description of what it targets.

## Cloud Provider Secrets (AWS, Azure, GCP)

Search queries to detect exposed credentials for major cloud providers like Amazon Web Services, Microsoft Azure, and Google Cloud Platform.

### AWS Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:credentials aws_access_key_id` | AWS CLI credentials file containing an AWS access key ID (and likely a secret key). |
| `filename:credentials aws_access_key_id` | Looks for the AWS CLI credentials file without restricting search scope. |
| `filename:.env AWS_ACCESS_KEY_ID` | Environment files with AWS Access Key ID (possible AWS key in `.env`). |
| `language:Python "AWS_SECRET_ACCESS_KEY"` | Finds AWS secret keys in Python source files. |
| `AWS_SECRET_ACCESS_KEY=` | Code or config defining an AWS Secret Access Key (e.g., in env assignments). |
| `AWS_ACCESS_KEY_ID=` | Occurrences of AWS Access Key ID being set in code or config. |
| `org:{ORG_NAME} AWS_ACCESS_KEY_ID` | Searches across an organization for AWS access key usage. |
| `AWS_SESSION_TOKEN=` | AWS session tokens in code (temporary credentials). |
| `AKIA` | Raw AWS Access Key IDs (which typically start with "AKIA") appearing in code. |
| `"AKIA" "AWS_SECRET_ACCESS_KEY"` | Looks for AWS key ID prefixes alongside the secret key term. |
| `filename:.s3cfg` | AWS S3 config file (contains `access_key` and `secret_key`, often for s3cmd). |
| `rds.amazonaws.com password` | Potential AWS RDS database connection strings with passwords. |

### Azure Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} AZURE_CLIENT_SECRET` | Azure client/application secrets exposed (e.g., in env vars or config). |
| `filename:.env AZURE_CLIENT_SECRET` | Azure OAuth client secrets stored in environment files. |
| `DefaultEndpointsProtocol= AND AccountKey=` | Azure Storage/Cosmos DB connection string. |
| `"DefaultEndpointsProtocol=https" "AccountKey="` | Detects Azure Storage connection strings in code. |
| `AzureWebJobsStorage` | Azure WebJobs/Functions storage connection strings (contains keys). |
| `ARM_CLIENT_SECRET` | Azure service principal (Resource Manager) client secret. |

### GCP Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:credentials.json "private_key_id"` | Google Cloud service account JSON key file. |
| `filename:credentials.json "type": "service_account"` | Any JSON file labeled as a GCP service account. |
| `filename:*.json private_key "-----BEGIN PRIVATE KEY-----"` | Detects Google Cloud service account keys by private key block. |
| `PRIVATE_KEY-----` | GCP private keys embedded in code or JSON. |
| `AIza` | Google API keys. |

## Third-Party API Keys and Tokens

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} sk_live_` | **Stripe** API secret keys. |
| `sk_live_` | Detects Stripe live secret keys. |
| `sk_test_` | Stripe API keys in test mode. |
| `xoxb- OR xoxp-` | **Slack** tokens – bot tokens or user tokens. |
| `ghp_ OR gho_ OR ghu_ OR ghs_ OR ghr_` | **GitHub** tokens. |
| `ghp_` | GitHub personal access tokens. |
| `SG.` | **SendGrid** API keys. |
| `MAILGUN_API_KEY` | **Mailgun** API keys. |
| `TWILIO_AUTH_TOKEN` | **Twilio** API secret tokens. |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (often near an auth token). |
| `HEROKU_API_KEY` | **Heroku** API keys. |
| `hooks.slack.com/services/` | Slack webhook URLs containing tokens. |
| `repo:{ORG_NAME}/{REPO_NAME} "ghp_"` | Check a specific repo for hard-coded GitHub tokens. |
| `shodan_api_key language:Python` | Shodan API keys in Python projects. |
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
| `VERCEL_API_TOKEN` | **Vercel** platform API tokens. |
| `HUGGINGFACEHUB_API_TOKEN` | **Hugging Face** API tokens. |
| `SUPABASE_SERVICE_ROLE_KEY` | **Supabase** service role keys. |
| `SENTRY_DSN` | **Sentry** DSN strings containing secrets. |
| `ROLLBAR_ACCESS_TOKEN` | **Rollbar** access tokens. |
| `GLPAT-` | **GitLab** personal access tokens. |
| `CLOUDFLARE_API_TOKEN` | **Cloudflare** API tokens. |
| `VAULT_TOKEN` | **HashiCorp Vault** tokens. |
| `PINECONE_API_KEY` | **Pinecone** API keys. |

## OAuth Client IDs and Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} GOOGLE_CLIENT_SECRET` | Google OAuth client secret. |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app client secret. |
| `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` | Facebook App ID and App Secret. |
| `TWITTER_CONSUMER_KEY` / `TWITTER_CONSUMER_SECRET` | Twitter API key and secret. |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn application client secret. |
| `extension:json "client_secret"` | JSON file containing a `client_secret` field. |
| `extension:json googleusercontent client_secret` | Google OAuth credentials in JSON files. |
| `filename:client_secrets.json "client_secret"` | Common Google OAuth credential file. |
| `CLIENT_SECRET=` | Generic search for `CLIENT_SECRET` assignments. |
| `CLIENT_SECRET` | Any occurrence of the phrase `CLIENT_SECRET`. |
| `consumer_key` | Looks for OAuth consumer key strings. |
| `consumer_secret` | Searches for OAuth consumer secret values. |
| `org:{ORG_NAME} "client_secret"` | Organization-wide search for OAuth client secrets. |
| `client_id AND client_secret` | Files containing both values. |

## Database Credentials and Connection Strings

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} DATABASE_URL=` | Environment variable for full database URI. |
| `DB_PASSWORD` | Exposed database password in environment/config. |
| `filename:.env DB_PASSWORD` | Finds database passwords in .env files. |
| `MYSQL_ROOT_PASSWORD` | MySQL root password in configs. |
| `POSTGRES_PASSWORD` | Postgres database password. |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB root user password in initialization. |
| `jdbc:mysql AND password=` | JDBC MySQL connection strings with credentials. |
| `jdbc:postgresql password=` | JDBC PostgreSQL connection string containing password. |
| `extension:sql "password"` | SQL dump files containing the word `password`. |
| `mongodb:// AND @` | MongoDB connection URI with credentials. |
| `postgres:// AND @` | PostgreSQL connection URI with credentials. |
| `mysql:// AND @` | MySQL connection URI containing credentials. |
| `repo:{ORG_NAME}/{REPO_NAME} "jdbc:mysql://"` | Repository-specific MySQL connection strings. |
| `filename:wp-config.php DB_PASSWORD NOT "password_here"` | WordPress configuration with real DB password. |
| `filename:wp-config.php` | Searches for any WordPress configuration file. |
| `filename:.my.cnf password` | MySQL client config file with a password entry. |
| `filename:.pgpass` | Postgres password file. |
| `filename:configuration.php JConfig password` | Joomla configuration file containing DB credentials. |
| `filename:config.php dbpasswd` | PHP config file containing `$dbpasswd`. |
| `filename:.env DB_USERNAME NOT homestead` | Database username in environment files, excluding defaults. |
| `filename:application.properties password` | Java/Spring configuration files with passwords. |

## Private Keys and Certificates

| Query Template | Description |
| --- | --- |
| `user:{USER_NAME} filename:id_rsa OR filename:id_dsa OR filename:id_ed25519` | Private SSH key files in user repositories. |
| `filename:id_rsa OR filename:id_dsa` | Searches for common SSH private key files. |
| `"-----BEGIN RSA PRIVATE KEY-----"` | RSA private keys in any file. |
| `"-----BEGIN DSA PRIVATE KEY-----"` | DSA private keys. |
| `"-----BEGIN EC PRIVATE KEY-----"` | Elliptic Curve private keys. |
| `"-----BEGIN OPENSSH PRIVATE KEY-----"` | OpenSSH private keys. |
| `extension:pem "PRIVATE KEY"` | PEM files containing a private key. |
| `extension:ppk` | PuTTY Private Key files. |
| `extension:ppk "PRIVATE KEY"` | PuTTY key files explicitly containing private key text. |
| `extension:pfx` | PKCS#12/PFX certificate stores. |
| `extension:p12` | PKCS#12 (.p12) files. |
| `extension:jks` | Java KeyStore files. |
| `filename:server.key` | Generic server private key files. |

## Email and SMTP Credentials

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:.env MAIL_HOST=smtp.gmail.com` | Gmail SMTP configuration in environment files. |
| `filename:.env MAIL_HOST=smtp.gmail.com` | Gmail SMTP configuration without organization filter. |
| `filename:.env MAIL_PASSWORD` | Environment files containing an email password. |
| `EMAIL_HOST_PASSWORD` | Common variable for email account passwords. |
| `SMTP_PASSWORD` | SMTP password exposure in code or config. |
| `smtp.office365.com password` | Office365 SMTP settings with a password. |
| `filename:ssmtp.conf` | SSMTP mail configuration file with credentials. |
| `filename:.esmtprc password` | esmtp configuration files containing passwords. |

## JWT Secrets and Application Secrets

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} JWT_SECRET` | JWT secret keys exposed. |
| `JWT_SECRET` | General search for JWT secrets. |
| `JWT_SECRET_KEY` | JSON Web Token secret keys (alternative). |
| `SECRET_KEY = ` | Django secret key in `settings.py`. |
| `filename:settings.py SECRET_KEY` | Django settings files containing `SECRET_KEY`. |
| `filename:.env JWT_SECRET` | Environment files with JWT secrets. |
| `filename:.env APP_KEY` | Laravel application key. |
| `secret_key_base` | Rails secret key base. |
| `TOKEN_SECRET` | Generic token secret variable. |
| `AUTH_SECRET` | Generic auth secret key name. |
| `SESSION_SECRET` | Session secret keys in various frameworks. |
| `APP_SECRET` | Generic application secret keys. |
| `FLASK_SECRET_KEY` | Flask application secret keys. |

## Configuration Files and Other Sensitive Files

| Query Template | Description |
| --- | --- |
| `org:{ORG_NAME} filename:.env DB_USERNAME NOT homestead` | Environment files containing DB credentials. |
| `repo:{ORG_NAME}/{REPO_NAME} filename:.env` | Check a specific repo for a committed `.env` file. |
| `filename:.git-credentials` | Git credential store files committed to a repository. |
| `filename:.git-credentials NOT username` | Git credentials file. |
| `filename:.git-credentials` | Searches for Git credential store files without filters. |
| `filename:.npmrc _auth` | npm configuration file with auth token. |
| `filename:.npmrc _authToken` | npm registry credentials containing an auth token. |
| `filename:.dockercfg auth` | Docker registry config with credentials. |
| `filename:.netrc password` | Netrc files storing passwords. |
| `filename:_netrc password` | Windows Netrc. |
| `filename:hub oauth_token` | Hub CLI config with OAuth token. |
| `filename:robomongo.json` | Robo 3T config with DB credentials. |
| `filename:filezilla.xml Pass` | FileZilla FTP client config with passwords. |
| `filename:recentservers.xml Pass` | FileZilla recent servers file with plain-text passwords. |
| `filename:.bash_profile AWS_ACCESS_KEY_ID` | Shell profile files containing AWS keys. |
| `filename:.bash_history` | Shell history files inadvertently committed. |
| `filename:.bashrc password` | Shell rc files with password strings. |
| `filename:config.json auths` | Docker credential store. |
| `filename:configuration.php JConfig password` | Joomla configuration with DB password. |
| `filename:config.php dbpasswd` | PHP config file containing `$dbpasswd`. |
| `filename:settings.py DATABASES` | Django settings containing database connection info. |
| `filename:prod.secret.exs` | Phoenix/Elixir production secret files. |

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
| `password = language:Java` | Hardcoded passwords assigned in Java code. |
| `password extension:ini` | Password strings in INI configuration files. |
| `password = "` | General search for password assignment. |
| `token = "` | Hardcoded token strings in code. |
| `Authorization: Bearer` | Hardcoded bearer tokens in code. |
| `Authorization Bearer token` | Bearer tokens without quotes in code. |
| `authToken =` | Looks for authToken assignments in code. |

## Secrets in Infrastructure-as-Code (Terraform, Ansible, Kubernetes, etc.)

| Query Template | Description |
| --- | --- |
| `filename:terraform.tfvars` | Terraform variable files that may contain sensitive values. |
| `filename:terraform.tfstate` | Terraform state files which often include plaintext secrets. |
| `extension:tf aws_secret_key` | Inline AWS secret keys in Terraform code. |
| `filename:vars.yml password` | Ansible variable files containing passwords. |
| `filename:docker-compose.yml MYSQL_PASSWORD` | Docker Compose files exposing MySQL passwords. |
| `stringData:` | Kubernetes secrets defined with plaintext stringData. |

## Secrets in CI/CD Configurations

| Query Template | Description |
| --- | --- |
| `path:.github/workflows AWS_ACCESS_KEY_ID` | GitHub Actions workflows with hardcoded AWS credentials. |
| `filename:.gitlab-ci.yml AWS_SECRET_ACCESS_KEY` | GitLab CI pipelines leaking AWS secret keys. |
| `filename:Jenkinsfile password` | Jenkins pipeline files containing passwords. |
| `HEROKU_API_KEY language:shell` | Heroku API keys embedded in shell scripts or CI files. |
| `repo:{ORG_NAME}/{REPO_NAME} "CI_SECRET"` | Search a specific repo for CI related secrets. |

## Secrets in Commit History, Issues, or Gists

| Query Template | Description |
| --- | --- |
| `type:commit "API key"` | Commit messages mentioning an API key. |
| `type:commit password` | Commit messages referencing passwords. |
| `org:{ORG_NAME} type:commit "SECRET_KEY"` | Organization-wide commits referring to secret keys. |
| `type:issue "AWS_SECRET_ACCESS_KEY"` | GitHub issues that may expose AWS secrets. |
| `site:gist.github.com "API_KEY"` | Public gists containing API keys (use via web search). |

## Internationalized Secret Keywords

| Query Template | Description |
| --- | --- |
| `senha` | Searches for the Portuguese word for "password". |
| `contraseña` | Searches for the Spanish word for "password". |
| `пароль` | Searches for the Russian word for "password". |
| `senha =` | Looks for assignments using the Portuguese term. |
| `contraseña =` | Looks for assignments using the Spanish term. |

