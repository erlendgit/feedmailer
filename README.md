# Feedmailer

A Python tool that monitors RSS/Atom feeds and sends new items via email.

## Description

Feedmailer checks configured RSS/Atom feeds for new items and automatically sends them via email. The tool remembers which items have already been seen, so only new updates are sent.

## Requirements

- Python 3.x
- `sendmail` installed and configured (if using sendmail backend)
- Or access to an SMTP server (if using SMTP backend)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd feedmailer
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

Or use the included setup script:
```bash
./bin/setup.sh
```

## Configuration

Create a JSON configuration file. See example configurations:
- `config.example.sendmail.json` - For local sendmail
- `config.example.smtp.json` - For SMTP servers

### Basic Configuration (Sendmail)

```json
{
  "urls": [
    "https://example.com/feed.xml",
    "https://another-blog.com/rss"
  ],
  "from": "feedmailer@example.com",
  "to": "recipient@example.com",
  "mail_backend": "sendmail"
}
```

### SMTP Configuration

```json
{
  "urls": [
    "https://example.com/feed.xml",
    "https://another-blog.com/rss"
  ],
  "from": "feedmailer@example.com",
  "to": "recipient@example.com",
  "mail_backend": "smtp",
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "use_tls": true
  }
}
```

### Configuration parameters:

- `urls`: List of RSS/Atom feed URLs to monitor
- `from`: Sender email address
- `to`: Recipient email address
- `mail_backend`: (optional) `"sendmail"` (default) or `"smtp"`
- `smtp`: (optional) SMTP server configuration (only needed if `mail_backend` is `"smtp"`)
  - `host`: SMTP server hostname
  - `port`: SMTP server port (default: 587)
  - `username`: SMTP username (optional)
  - `password`: SMTP password (optional)
  - `use_tls`: Use TLS encryption (default: true)

**📖 For detailed mail backend configuration, see [MAIL_BACKENDS.md](MAIL_BACKENDS.md)**

## Usage

### Basic usage

```bash
python main.py <config-file> <status-file>
```

Example:
```bash
python main.py config.json status.json
```

### Using the shell script

```bash
./feedmailer.sh <config-file> <status-file>
```

### Parameters:

- `config-file`: Path to the JSON configuration file
- `status-file`: Path to the file where status is stored (created automatically)

## Automation with Cron

Add an entry to your crontab to run feedmailer periodically:

```bash
# Check feeds every hour
0 * * * * /path/to/feedmailer/feedmailer.sh /path/to/config.json /path/to/status.json
```

Or check twice daily:
```bash
0 9,18 * * * /path/to/feedmailer/feedmailer.sh /path/to/config.json /path/to/status.json
```

## Development

### Running tests

```bash
./bin/test.sh
```

Or directly with pytest:
```bash
pytest
```

### Installing development dependencies

```bash
pip install -r requirements-dev.txt
```

## How it works

1. **Load**: The application loads the configuration and previously seen items from the status file
2. **Fetch**: All configured feeds are fetched and parsed
3. **Filter**: New items (not in the status) are selected
4. **Send**: If there are new items, an email is sent with the updates in Markdown format
5. **Save**: The status is updated with the new items

## Email format

New feed items are sent as a Markdown list:

```
Subject: Feed Updates

* [Article Title 1](https://example.com/article1)
* [Article Title 2](https://example.com/article2)
```

## License

This work has been dedicated to the public domain under the [CC0 1.0 Universal (CC0 1.0) Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

## Author

Erlend ter Maat
