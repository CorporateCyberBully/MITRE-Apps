import urllib.request
from base64 import b64encode

# Replace with your Jira instance URL
jira_url = "https://your-instance.atlassian.net"

# Replace your email and API token
email = "your-email@example.com"
api_token = "your-api-token"

credentials = b64encode(bytes(f'{email}:{api_token}', 'utf-8')).decode('ascii')
headers = { 'Authorization' : f'Basic {credentials}' }

request = urllib.request.Request(jira_url, headers=headers)

try:
    response = urllib.request.urlopen(request)
    print(f"Response status code: {response.getcode()}")
except urllib.error.HTTPError as e:
    print(f"Response status code: {e.code}")