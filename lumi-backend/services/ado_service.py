import os
import requests
from dotenv import load_dotenv
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class ADOService:
    def __init__(self):
        self.org = os.getenv("ADO_ORGANIZATION")
        self.project = os.getenv("ADO_PROJECT")
        self.pat = os.getenv("ADO_PAT")
        self.feature_values = None
        self.user_map = None
        if self.user_map is None:
            self.user_map = self.get_ado_users()
            
    def get_user_display_name(self, display_name):

        if self.user_map is None:
            self.user_map = self.get_ado_users()

        name = display_name.lower()

        for stored_name in self.user_map.values():
            if name in stored_name.lower():
                return stored_name

        return None

    def create_work_item(self, item, parent_id=None):

        title = item.get("title", "No Title")
        description = item.get("description", "No Description")
        item_type = item.get("type", "Task")
        encoded_type = item_type.replace(" ", "%20")

        url = f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workitems/${encoded_type}?api-version=7.0"

        body = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "value": f"<div>{description}</div>"
            }
        ]

        # Priority
        priority_map = {
                "critical": 1,
                "high": 2,
                "medium": 3,
                "low": 4
            }

        priority = item.get("priority")

        if priority:
            if isinstance(priority, str):
                priority = priority_map.get(priority.lower(), 3)

            body.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Common.Priority",
                "value": int(priority)
            })

        # Story Points
        if item.get("story_points"):
            body.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                "value": int(item["story_points"])
            })

        # Owner
        owner = item.get("owner")

        if owner:

            if self.user_map is None:
                self.user_map = self.get_ado_users()

            owner_lower = owner.lower()
            owner_email = None
            owner_display = None

            for display_name, user in self.user_map.items():
                if owner_lower in display_name:
                    owner_display = user["name"]
                    owner_email = user["email"]
                    break

            print("Transcript owner:", owner)
            print("Matched user:", owner_display)
            print("Matched email:", owner_email)

            if owner_email:
                body.append({
                    "op": "add",
                    "path": "/fields/System.AssignedTo",
                    "value": owner_email
                })

        # Acceptance Criteria for User Story
        if item_type == "User Story":
            body.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                "value": f"<div>{description}</div>"
            })

        # Feature Value
        if item_type == "Feature":

            if not self.feature_values:
                self.feature_values = self.get_feature_values()

            feature_value = item.get("feature_value")

            # If AI value not valid, fallback to first allowed value
            if not feature_value or feature_value not in self.feature_values:
                feature_value = "Functionality"

            body.append({
                "op": "add",
                "path": "/fields/Custom.FeatureValue",
                "value": feature_value
            })

        # Parent relationship
        if parent_id:
            body.append({
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workItems/{parent_id}",
                    "attributes": {
                        "comment": "Linked by AI meeting assistant"
                    }
                }
            })

        response = requests.post(
            url,
            headers={"Content-Type": "application/json-patch+json"},
            auth=("", self.pat),
            json=body,
            verify=False
        )

        if response.status_code not in [200, 201]:
            print("ADO STATUS:", response.status_code)
            print("ADO RESPONSE:", response.text[:300])
            raise Exception("Azure DevOps work item creation failed")

        return response.json()
    
    def get_ado_users(self):

        team_id = "aa8a1d30-18d0-49a8-a7f5-51e49afaab29"

        url = f"https://dev.azure.com/{self.org}/_apis/projects/{self.project}/teams/{team_id}/members?api-version=7.0"

        try:
            response = requests.get(url, auth=("", self.pat), verify=False)

            if response.status_code != 200:
                print("Failed to fetch team members:", response.text)
                return {}

            members = response.json().get("value", [])

            user_map = {}

            for m in members:

                display = m.get("identity", {}).get("displayName")
                email = m.get("identity", {}).get("uniqueName")

                if display and email:
                    user_map[display.lower()] = {
                        "name": display,
                        "email": email
                    }

            print("Team Members:", user_map)

            return user_map

        except Exception as e:
            print("User Fetch Failed:", e)
            return {}
        
    def get_feature_values(self):

        return [
            "Compliance",
            "Continuous Improvement",
            "Discovery",
            "Functionality",
            "Required Maintenance",
            "Technical Excellence"
        ]

    def sync_all_items(self, action_items):

        results = []

        epics = []
        features = []
        stories = []
        tasks = []
        bugs = []

        epic_id = None
        feature_id = None
        story_id = None

        # STEP 1: Categorize items
        for item in action_items:

            item_type = item.get("type", "Task")

            if item_type == "Epic":
                epics.append(item)

            elif item_type == "Feature":
                features.append(item)

            elif item_type == "User Story":
                stories.append(item)

            elif item_type == "Bug":
                bugs.append(item)

            else:
                tasks.append(item)

        # STEP 2: Create Epics
        for item in epics:

            epic = self.create_work_item(item)
            epic_id = epic["id"]

            results.append({
                "title": item["title"],
                "type": "Epic",
                "ado_id": epic_id,
                "url": epic["_links"]["html"]["href"]
            })

        # STEP 3: Create Features
        for item in features:

            feature = self.create_work_item(item, parent_id=epic_id)
            feature_id = feature["id"]

            results.append({
                "title": item["title"],
                "type": "Feature",
                "ado_id": feature_id,
                "url": feature["_links"]["html"]["href"]
            })

        # STEP 4: Create User Stories
        for item in stories:

            story = self.create_work_item(item, parent_id=feature_id)
            story_id = story["id"]

            results.append({
                "title": item["title"],
                "type": "User Story",
                "ado_id": story_id,
                "url": story["_links"]["html"]["href"]
            })

        # STEP 5: Create Tasks and Bugs
        for item in tasks + bugs:

            task = self.create_work_item(item, parent_id=story_id)

            results.append({
                "title": item["title"],
                "type": item["type"],
                "ado_id": task["id"],
                "url": task["_links"]["html"]["href"]
            })

        return results