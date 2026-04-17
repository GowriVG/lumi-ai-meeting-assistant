import requests
from auth.graph_auth import get_graph_token
from logger import logger

from logger import logger

def fetch_latest_transcript():
    try:
        logger.info("Fetching transcript from Microsoft Graph")

        token = get_graph_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        meetings_url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"
        meetings = requests.get(meetings_url, headers=headers).json()

        if not meetings.get("value"):
            raise Exception("No meetings found")

        meeting_id = meetings["value"][0]["id"]

        transcript_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
        transcripts = requests.get(transcript_url, headers=headers).json()

        if not transcripts.get("value"):
            raise Exception("No transcripts found")

        transcript_id = transcripts["value"][0]["id"]

        content_url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content"

        content = requests.get(content_url, headers=headers)

        return content.text

    except Exception:
        logger.error("Graph API failed", exc_info=True)
        raise