from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, ai
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/words", tags=["words"])


@router.post("/", response_model=schemas.Word)
def create_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check for duplicates
    existing_word = db.query(models.Word).filter(
        models.Word.owner_id == current_user.id,
        models.Word.english == word.english
    ).first()
    
    if existing_word:
        raise HTTPException(status_code=400, detail="Word already exists")

    new_word = models.Word(owner_id=current_user.id, **word.dict())
    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    return new_word


@router.get("/", response_model=list[schemas.Word])
def list_words(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.Word)
        .filter(models.Word.owner_id == current_user.id)
        .order_by(models.Word.created_at.desc())
        .all()
    )


@router.post("/complete", response_model=schemas.AICompletionResponse)
def complete_word(request: schemas.AICompletionRequest, db: Session = Depends(get_db)):
    return ai.complete_word(request, db)


@router.put("/{word_id}", response_model=schemas.Word)
def update_word(
    word_id: int,
    word_update: schemas.WordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing_word = db.query(models.Word).filter_by(id=word_id, owner_id=current_user.id).first()
    if not existing_word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Update fields
    existing_word.english = word_update.english
    existing_word.chinese = word_update.chinese
    existing_word.part_of_speech = word_update.part_of_speech
    existing_word.definition = word_update.definition
    existing_word.examples = word_update.examples
    
    # Optional: Update other fields if they are in the request, or keep existing logic
    # We stick to the main editable fields for now.

    db.commit()
    db.refresh(existing_word)
    return existing_word


@router.delete("/{word_id}")
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    word = db.query(models.Word).filter_by(id=word_id, owner_id=current_user.id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    db.delete(word)
    db.commit()
    return {"detail": "deleted"}
