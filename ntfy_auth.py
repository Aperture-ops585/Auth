import requests
import json
import os

# Load configuration from JSON file
CONFIG_PATH = "./config.json"

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def send_auth_request(request_id, ip_address, service):
    """
    Sends a push notification using URLs and Tags from config.
    """
    config = load_config()
    topic_url = config.get("topic_url")
    response_url = config.get("response_url")
    token = config.get("ntfy_token")
    tags = config.get("tags")

    headers = {
        "Title": f"Auth Request: {service.upper()}",
        "Priority": "5",
        "Tags": tags,
        "Authorization": f"Bearer {token}",
        "Actions": (
            f"http, Approve, {response_url}, method=POST, body='approved:{request_id}', clear=true; "
            f"http, Deny, {response_url}, method=POST, body='denied:{request_id}', clear=true"
        )
    }

    message = f"{service.upper()} login attempt from {ip_address}. Do you approve?"
    
    response = requests.post(
        topic_url,
        data=message.encode('utf-8'),
        headers=headers
    )
    
    return response

if __name__ == "__main__":
    # Test
    res = send_auth_request("test1234", "1.2.3.4", "test")
    print(f"Status: {res.status_code}")
