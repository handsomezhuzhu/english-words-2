import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, scheduler
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/start", response_model=list[schemas.ReviewItem])
def start_review(
    request: schemas.ReviewRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    words = scheduler.pick_for_review(db, current_user.id, request.count)
    items = []
    for word in words:
        if request.mode == "en_to_zh":
            question = word.english or word.definition or ""
            answer = word.chinese or word.definition or ""
        elif request.mode == "zh_to_en":
            question = word.chinese or word.definition or ""
            answer = word.english or word.definition or ""
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")
        
        examples_list = []
        if word.examples:
            try:
                # Try parsing as JSON first
                raw_examples = json.loads(word.examples)
                examples_list = [schemas.Example(**ex) for ex in raw_examples]
            except Exception:
                # Fallback: Parse plain text
                # Assumes format: 
                # English Sentence
                # Chinese Sentence
                # (empty line)
                lines = [line.strip() for line in word.examples.split('\n') if line.strip()]
                # Naive pairing: assume every even line is English, odd is Chinese
                # Or improved: check if line contains chinese characters
                
                # Let's try to pair them up. 
                # If we have an even number of lines, assume En/Zh pairs.
                if len(lines) >= 2:
                    for i in range(0, len(lines) - 1, 2):
                        # A simple heuristic: The one with more ASCII is likely English
                        # But strictly following the AI output format (En \n Zh) is safer for now.
                        examples_list.append(schemas.Example(
                            sentenceEn=lines[i],
                            sentenceZh=lines[i+1]
                        ))
                elif len(lines) == 1:
                     # Just one line, assume it's English/mixed
                     examples_list.append(schemas.Example(sentenceEn=lines[0], sentenceZh=""))

        items.append(
            schemas.ReviewItem(
                id=word.id, 
                question=question, 
                answer=answer,
                examples=examples_list
            )
        )
    return items


@router.post("/{word_id}/result")
def submit_result(
    word_id: int,
    answer: schemas.ReviewAnswer,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    word = db.query(models.Word).filter_by(id=word_id, owner_id=current_user.id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    scheduler.schedule_next(word, answer.grade)
    db.add(word)
    db.commit()
    return {"detail": "updated"}
