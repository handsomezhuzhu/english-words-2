import json
import httpx
from sqlalchemy.orm import Session
from . import schemas, models

def complete_word(request: schemas.AICompletionRequest, db: Session) -> schemas.AICompletionResponse:
    config = db.query(models.SystemConfig).first()
    
    if not config or not config.api_url or not config.api_key:
        # Fallback to mock if not configured
        return _mock_complete(request)

    prompt = f"""
    You are a helpful assistant that provides dictionary data for language learning.
    Target Word: "{request.word}"
    
    Please provide the following information in strict JSON format:
    1. Phonetics (UK and US)
    2. Parts of Speech (list with pos, English meaning, Chinese meaning)
    3. Examples (list with English sentence and Chinese translation)
    4. Synonyms (list of strings)
    5. Antonyms (list of strings)

    Format:
    {{
        "word": "{request.word}",
        "phonetics": {{"uk": "...", "us": "..."}},
        "partsOfSpeech": [{{"pos": "...", "meaningEn": "...", "meaningZh": "..."}}],
        "examples": [{{"sentenceEn": "...", "sentenceZh": "..."}}],
        "synonyms": ["..."],
        "antonyms": ["..."]
    }}
    
    Ensure the JSON is valid and contains no other text.
    """

    try:
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Determine endpoint - usually /v1/chat/completions
        url = config.api_url.rstrip('/')
        if not url.endswith('/chat/completions'):
            url += '/chat/completions'

        payload = {
            "model": config.model,
            "messages": [
                {"role": "system", "content": "You are a dictionary API. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data['choices'][0]['message']['content']
            # Clean up potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Map to schema
            return schemas.AICompletionResponse(
                word=result.get("word", request.word),
                phonetics=schemas.Phonetics(**result.get("phonetics", {})),
                partsOfSpeech=[schemas.PartOfSpeech(**p) for p in result.get("partsOfSpeech", [])],
                examples=[schemas.Example(**e) for e in result.get("examples", [])],
                synonyms=result.get("synonyms", []),
                antonyms=result.get("antonyms", []),
                direction=request.direction
            )

    except Exception as e:
        print(f"AI Error: {e}")
        return _mock_complete(request)


def _mock_complete(request: schemas.AICompletionRequest) -> schemas.AICompletionResponse:
    word = request.word
    direction = request.direction

    # Mock data generation
    if direction == "en_to_zh":
        phonetics = schemas.Phonetics(uk="/mock/", us="/mock/")
        parts = [
            schemas.PartOfSpeech(pos="noun", meaningEn="A mock definition", meaningZh="模拟定义"),
        ]
        examples = [
            schemas.Example(sentenceEn=f"This is a mock example for {word}.", sentenceZh=f"这是 {word} 的模拟例句。"),
        ]
        synonyms = ["mock"]
        antonyms = []
    else:
        phonetics = schemas.Phonetics(uk="", us="")
        parts = []
        examples = []
        synonyms = []
        antonyms = []

    return schemas.AICompletionResponse(
        word=word,
        phonetics=phonetics,
        partsOfSpeech=parts,
        examples=examples,
        synonyms=synonyms,
        antonyms=antonyms,
        direction=direction,
    )