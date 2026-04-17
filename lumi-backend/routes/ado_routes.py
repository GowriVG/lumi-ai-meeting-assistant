from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from services.ado_service import ADOService
from memory.session_store import get_meeting
from exceptions.custom_exceptions import MeetingNotFoundError, PromptValidationError

router = APIRouter()
ado_service = ADOService()


class WorkItem(BaseModel):
    title: str
    description: str
    type: str
    priority: str | None = None
    story_points: int | None = None
    owner: str | None = None


# @router.post("/sync-to-ado/{meeting_id}")
# def sync_to_ado(meeting_id: str):
#     meeting = get_meeting(meeting_id)

#     if not meeting:
#         raise MeetingNotFoundError("Meeting not found")

#     summary = meeting.get("summary")

#     if not summary:
#         raise PromptValidationError("Summary not generated")

#     items = summary.get("action_items", [])

#     return {
#         "status": "success",
#         "synced_items": ado_service.sync_all_items(items)
#     }

@router.post("/sync-to-ado/{meeting_id}")
def sync_to_ado(meeting_id: str):
    meeting = get_meeting(meeting_id)

    if not meeting:
        raise MeetingNotFoundError("Meeting not found")

    summary = meeting.get("summary")

    if not summary:
        raise PromptValidationError("Summary not generated")

    items = summary.get("action_items", [])

    result = ado_service.sync_all_items(items)

    return {
        "status": "success",
        "data": result
    }

# @router.post("/sync-selected/{meeting_id}")
# def sync_selected(meeting_id: str, items: List[WorkItem]):

#     if not items:
#         raise PromptValidationError("No items provided")

#     return {
#         "status": "success",
#         "synced_items": ado_service.sync_all_items(
#             [item.dict() for item in items]
#         )
#     }

@router.post("/sync-selected/{meeting_id}")
def sync_selected(meeting_id: str, items: List[WorkItem]):

    if not items:
        raise PromptValidationError("No items provided")

    result = ado_service.sync_all_items(
        [item.dict() for item in items]
    )

    return {
        "status": "success",
        "data": result
    }