from britive.britive import Britive
import json
import base64
import requests


def main():
    token = Britive.source_federation_token_from('aws', duration_seconds=3600, tenant='britive.com')
    test = token.split('::')[1]
    payload = json.loads(base64.urlsafe_b64decode(test).decode())
    print(json.dumps(payload, indent=2))

    headers = payload['iam_request_headers']
    headers['content-type'] = 'application/x-www-form-urlencoded'
    headers['accept'] = 'application/json'

    response = requests.post(
        payload['iam_request_url'],
        headers=payload['iam_request_headers'],
        data=payload['iam_request_body']
    )
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()

