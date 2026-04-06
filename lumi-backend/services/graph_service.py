import requests
from auth.graph_auth import get_graph_token

def fetch_transcript(user_id, meeting_id):

    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    list_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/{meeting_id}/transcripts"

    response = requests.get(list_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Graph Error: {response.text}")

    data = response.json()

    if "value" not in data or not data["value"]:
        raise Exception("No transcripts found")

    transcript_id = data["value"][0]["id"]

    content_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content"

    content = requests.get(content_url, headers=headers)

    return content.text