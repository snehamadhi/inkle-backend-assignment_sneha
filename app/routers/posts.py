from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Post, User
from app.schemas import UserOut
from app.auth_utils import get_current_user, get_db, require_admin
from app.activity_logger import log_activity


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(content: str, 
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Create a new post. Only authenticated users can post.
    """
    if not content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty.")

    post = Post(
        user_id=current_user.id,
        content=content
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # Log activity
    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="POST_CREATED",
        object_type="post",
        object_id=post.id
    )

    return {"id": post.id, "content": post.content, "created_by": current_user.name}


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_posts(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    """
    Returns list of all posts. Requires authentication.
    """
    posts = db.query(Post).all()

    return [
        {
            "id": post.id,
            "content": post.content,
            "author_id": post.user_id,
            "created_at": post.created_at
        }
        for post in posts
    ]


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Delete a post.
    - Users can delete their own posts
    - Admin and Owner can delete any post
    """

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Permission logic
    if post.user_id != current_user.id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not allowed to delete this post")

    # Record who deleted it
    if current_user.role in ["admin", "owner"]:
        post.deleted_by = current_user.role

    db.delete(post)
    db.commit()

    # Log activity
    log_activity(
        db=db,
        actor_id=current_user.id,
        verb="POST_DELETED",
        object_type="post",
        object_id=post.id
    )

    return {"message": "Post deleted"}
