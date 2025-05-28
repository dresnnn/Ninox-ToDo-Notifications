# Ninox-ToDo-Notifications

This project fetches open tasks from a Ninox database and sends a daily
summary email to each user. Configuration is done via a YAML file.

## Configuration

Copy `config_example.yaml` to `config.yaml` and adjust the values. The file
contains all required settings:

```yaml
ninox:
  api_url: "https://app.stadtbild.de/v1"
  team_id: "TEAM_ID"
  database_id: "DATABASE_ID"
  table_id: "TABLE_ID"
  api_token: "TOKEN"

smtp:
  host: "smtp.example.com"
  port: 587
  username: "user"
  password: "pass"
  from_address: "todo@example.com"

users:
  "André Bogatz":
    email: "andre@example.com"
    notify_in_debug: true
  "Philipp Kabelka":
    email: "philipp@example.com"
    notify_in_debug: false

  send_time: "09:00"  # when the internal scheduler triggers
  debug: false         # set true to avoid sending mails
```

`notify_in_debug` allows selected users to still receive mails when the
`debug` flag is enabled. In this mode the script prints additional
information about which mails are prepared or skipped.

## Usage

Create a virtual environment and install the package:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

```
ninox-notify config.yaml            # send once
ninox-notify-service config.yaml    # run as daily service
```

The script retrieves all open tasks, groups them by user and sends a
HTML email listing the tasks. Pagination is handled automatically.
`ninox-notify-service` runs indefinitely and sends mails every day at
the configured `send_time`.
