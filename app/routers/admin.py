from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", summary="Admin dashboard")
async def admin_dashboard(
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Admin dashboard endpoint.
    Requires admin privileges.
    """
    return {"message": "Welcome to the admin dashboard"}


@router.get("/users", response_model=list[schemas.User], summary="List all users")
def list_users(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    List all users.
    Requires admin privileges.
    """
    return db.query(models.User).all()


@router.get("/users/{user_id}", response_model=schemas.User, summary="Get user by ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Get a specific user by their ID.
    Requires admin privileges.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=schemas.User, summary="Update user")
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Update a user's attributes.
    Requires admin privileges.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.is_admin is not None:
        user.is_admin = user_update.is_admin

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", response_model=schemas.User, summary="Delete user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Delete a user.
    Requires admin privileges.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return user


@router.get("/ai-config", response_model=schemas.SystemConfig, summary="Get AI configuration")
def get_ai_config(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Get the current AI configuration.
    Requires admin privileges.
    """
    config = db.query(models.SystemConfig).filter(models.SystemConfig.owner_id == current_admin.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="AI configuration not found")
    return config


@router.put("/ai-config", response_model=schemas.SystemConfig, summary="Update AI configuration")
def update_ai_config(
    config_update: schemas.SystemConfigCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Update the AI configuration.
    Requires admin privileges.
    """
    config = db.query(models.SystemConfig).filter(models.SystemConfig.owner_id == current_admin.id).first()
    if not config:
        config = models.SystemConfig(**config_update.dict(), owner_id=current_admin.id)
        db.add(config)
    else:
        update_data = config_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


