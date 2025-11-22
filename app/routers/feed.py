from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import Activity, Block
from app.auth_utils import get_current_user, get_db

router = APIRouter(prefix="/feed", tags=["Activity Feed"])


@router.get("/")
def get_activity_feed(db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    """
    Returns the activity feed for the user.
    It hides activity from users who blocked the current user.
    """

    # Find all users who have blocked the current user
    blocked_by = db.query(Block).filter(
        Block.blocked_user_id == current_user.id
    ).all()

    blocked_user_ids = [record.blocker_id for record in blocked_by]

    # Get all activity EXCEPT from blocked users
    activities = db.query(Activity).filter(
        Activity.actor_id.not_in(blocked_user_ids)
    ).order_by(Activity.created_at.desc()).all()

    formatted = []

    for act in activities:

        entry = {
            "id": act.id,
            "timestamp": act.created_at,
        }

        # Convert activity to readable message
        if act.verb == "POST_CREATED":
            entry["message"] = f"User {act.actor_id} made a post"
        elif act.verb == "POST_DELETED":
            entry["message"] = f"User {act.actor_id} deleted a post"
        elif act.verb == "FOLLOWED":
            entry["message"] = f"User {act.actor_id} followed User {act.target_user_id}"
        elif act.verb == "UNFOLLOWED":
            entry["message"] = f"User {act.actor_id} unfollowed User {act.target_user_id}"
        elif act.verb == "BLOCKED":
            entry["message"] = f"User {act.actor_id} blocked User {act.target_user_id}"
        elif act.verb == "UNBLOCKED":
            entry["message"] = f"User {act.actor_id} unblocked User {act.target_user_id}"
        else:
            entry["message"] = f"Activity: {act.verb}"

        formatted.append(entry)

    return formatted
