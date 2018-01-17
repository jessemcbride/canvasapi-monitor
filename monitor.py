import logging
import os

import requests
from bs4 import BeautifulSoup
from slackweb import Slack

# Configure logging
logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('monitor.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)

try:
    from settings import SLACK_URL
except ImportError:
    logger.error("Unable to load `SLACK_URL` from settings.py. Does it exist?")

# Build the Slack client
slack = Slack(url=SLACK_URL)

path = os.path.split(os.path.abspath(__file__))[0]
url = "https://canvas.instructure.com/doc/api/all_resources.html"
cache_location = os.path.join(path, 'cache')

try:
    first_run = bool(os.listdir(cache_location))
except OSError:
    os.mkdir(cache_location)
    first_run = True

changes = []

# Fetch the API docs
response = requests.get(url)

# Parse it
soup = BeautifulSoup(response.text, 'html.parser')

methods = soup.find_all('div', {'class': 'method_details'})

for method in methods:
    try:
        name = method.find_all('h2', {'class': 'api_method_name'})[0]

        # Sanitize name
        name = name.find_all('a')[0].text.strip()

        identifier = method.find_all(
            'h2', {'class': 'api_method_name'}
        )[0]['name']

        method_url = url + method.find_all('a', href=True)[0]['href']
    except IndexError:
        logger.warning(
            "Couldn't find method name for method:\n%s" % method
        )

    path = os.path.join(cache_location, identifier.replace('/', '+'))

    try:
        cached = open(path, 'r+')

        if cached.read() != str(method):
            changes.append({'method': name, 'url': method_url})

        cached.seek(0)
        cached.truncate()
        cached.write(str(method))
        cached.close()
    except IOError:
        logger.info("New method found - writing %s to its own file" % name)
        cached = open(path, 'w+')
        cached.write(str(method))
        cached.close()
        changes.append({'method': name, 'url': method_url})

if first_run:
    logger.info("`first_run` was true - not sending out notifications")
    changes = []

if changes:
    plural = 's' if len(changes) > 1 else ''
    message = "Detected modified endpoint" + plural + ":\n"

    for change in changes:
        message += '\n<%s|%s>' % (change['url'], change['method'])

    slack.notify(text=message)
else:
    logger.info("Script completed without finding changes")
