from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, Post, Follow, Like
from app.auth_utils import get_current_user, get_db, require_admin, require_owner
from app.activity_logger import log_activity

router = APIRouter(prefix="/admin", tags=["Admin & Owner Controls"])


# -------------------
# DELETE USER
# -------------------
@router.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(require_admin)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.role == "owner":
        raise HTTPException(status_code=403, detail="Owners cannot be deleted.")

    # Delete user's posts, follows, likes
    db.query(Post).filter(Post.user_id == user_id).delete()
    db.query(Follow).filter(Follow.follower_id == user_id).delete()
    db.query(Follow).filter(Follow.following_id == user_id).delete()
    db.query(Like).filter(Like.user_id == user_id).delete()

    db.delete(user)
    db.commit()

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="USER_DELETED",
        object_type="user",
        object_id=user_id
    )

    return {"message": f"User {user_id} deleted."}


# -------------------
# OWNER ONLY: Promote admin
# -------------------
@router.post("/promote/{user_id}", status_code=status.HTTP_200_OK)
def promote_to_admin(user_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(require_owner)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.role = "admin"
    db.commit()
    
    return {"message": f"User {user_id} is now an admin."}
