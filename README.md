# canvasapi-monitor

![Example script output](https://i.imgur.com/AFQ4A7f.png)

This script monitors the Canvas API documentation and then posts any detected changes to a Slack channel.

## Configuration

Copy `settings.template.py` into `settings.py` and then fill out the `SLACK_URL` field with the URL of your Slack webhook. For more information about Slack webhooks, see their [API documentation](https://api.slack.com/incoming-webhooks).

I personally run this script as a cronjob:

```
$ crontab -e

0 9 * * * python /path/to/monitor.py
```
