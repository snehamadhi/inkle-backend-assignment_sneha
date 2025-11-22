from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Block, User, Follow
from app.auth_utils import get_current_user, get_db
from app.activity_logger import log_activity

router = APIRouter(prefix="/block", tags=["Block System"])


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
def block_user(user_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot block yourself.")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if already blocked
    existing = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_user_id == user_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already blocked.")

    # Auto remove follow if already following them
    follow_entry = db.query(Follow).filter(
        Follow.follower_id == user_id,
        Follow.following_id == current_user.id
    ).first()
    if follow_entry:
        db.delete(follow_entry)

    block = Block(blocker_id=current_user.id, blocked_user_id=user_id)
    db.add(block)
    db.commit()

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="BLOCKED",
        object_type="user",
        object_id=user_id,
        target_user_id=user_id
    )

    return {"message": f"User {user_id} blocked."}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def unblock_user(user_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):

    block_record = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_user_id == user_id
    ).first()

    if not block_record:
        raise HTTPException(status_code=400, detail="User is not blocked.")

    db.delete(block_record)
    db.commit()

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="UNBLOCKED",
        object_type="user",
        object_id=user_id,
        target_user_id=user_id
    )

    return {"message": f"User {user_id} unblocked."}
