from sqlalchemy.orm import Session
from .models import Activity


def log_activity(
    db: Session,
    actor_id: int,
    verb: str,
    object_type: str,
    object_id: int = None,
    target_user_id: int = None
):
    """
    A reusable function to record actions in the Activity table.
    Makes the feed consistent and clean.
    """

    activity = Activity(
        actor_id=actor_id,
        verb=verb,
        object_type=object_type,
        object_id=object_id,
        target_user_id=target_user_id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity
