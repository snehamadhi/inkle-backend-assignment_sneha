from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Follow, User
from app.auth_utils import get_current_user, get_db
from app.activity_logger import log_activity

router = APIRouter(prefix="/follow", tags=["Follow System"])


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
def follow_user(user_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Follow another user unless:
    - Already following
    - Trying to follow self
    """

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already following this user.")

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()
    db.refresh(follow)

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="FOLLOWED",
        object_type="user",
        object_id=user_id,
        target_user_id=user_id
    )

    return {"message": f"You are now following user {user_id}"}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def unfollow_user(user_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):

    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=400, detail="You are not following this user.")

    db.delete(follow)
    db.commit()

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="UNFOLLOWED",
        object_type="user",
        object_id=user_id,
        target_user_id=user_id
    )

    return {"message": f"You unfollowed user {user_id}"}
