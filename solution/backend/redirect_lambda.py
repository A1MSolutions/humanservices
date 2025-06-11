import json
import os
from urllib.parse import urljoin

def handler(event, context):
    original_path = event['path']
    # Use environment variable for domain, fallback to default
    domain = os.environ.get('REDIRECT_DOMAIN', 'humanservices.policyconnector.digital')
    new_domain = f'https://{domain}'
    new_url = urljoin(new_domain, original_path)

    response = {
        'statusCode': 302,
        'headers': {
            'Location': new_url,
        },
    }

    return response
