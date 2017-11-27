import requests

from bs4 import BeautifulSoup
from slackweb import Slack

from settings import SLACK_URL


url = "https://canvas.instructure.com/doc/api/all_resources.html"
changes = []

slack = Slack(url=SLACK_URL)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

methods = soup.find_all('div', {'class': 'method_details'})

for method in methods:
    try:
        name = method.find_all('h2', {'class': 'api_method_name'})[0].find_all('a')[0].text.strip()
        identifier = method.find_all('h2', {'class': 'api_method_name'})[0]['name']
        method_url = url + method.find_all('a', href=True)[0]['href']
    except IndexError:
        print("Couldn't find method name for method:\n%s" % method)

    try:
        cached = open('cache/%s' % identifier.replace('/', '+'), 'r+')

        if cached.read() != str(method):
            changes.append({'method': name, 'url': method_url})

        cached.seek(0)
        cached.truncate()
        cached.write(str(method))
        cached.close()
    except IOError:
        cached = open('cache/%s' % identifier.replace('/', '+'), 'w+')
        cached.write(str(method))
        cached.close()
        changes.append({'method': name, 'url': method_url})

if changes:
    plural = 's' if len(changes) > 1 else ''

    message = "Detected modified endpoint" + plural + ":\n"

    for change in changes:
        message += '\n<%s|%s>' % (change['url'], change['method'])

    slack.notify(text=message)
