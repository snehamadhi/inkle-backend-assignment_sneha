from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Like, Post, Block, User
from app.auth_utils import get_current_user, get_db
from app.activity_logger import log_activity

router = APIRouter(prefix="/like", tags=["Likes"])


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def like_post(post_id: int,
              db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    # Cannot like your own post (optional rule)
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You can’t like your own post.")

    # Check if user is blocked by the post owner
    blocked = db.query(Block).filter(
        Block.blocker_id == post.user_id,
        Block.blocked_user_id == current_user.id
    ).first()

    if blocked:
        raise HTTPException(status_code=403, detail="You are blocked by this user.")

    # Check if already liked
    existing = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Post already liked.")

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()

    # Log activity
    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="LIKED",
        object_type="post",
        object_id=post_id,
        target_user_id=post.user_id
    )

    return {"message": f"You liked post {post_id}"}


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def unlike_post(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()

    if not like:
        raise HTTPException(status_code=400, detail="You have not liked this post.")

    db.delete(like)
    db.commit()

    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="UNLIKED",
        object_type="post",
        object_id=post_id
    )

    return {"message": f"You unliked post {post_id}"}
