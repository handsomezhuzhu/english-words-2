from typing import Optional
from . import schemas


EXAMPLE_SENTENCES = {
    "hello": ["Hello, how are you?", "The teacher said hello to every student."],
    "学习": ["我喜欢学习新的语言。", "每天学习一点点会有进步。"],
}


def complete_word(request: schemas.AICompletionRequest) -> schemas.AICompletionResponse:
    """A deterministic, offline AI completion stub.

    In production you could replace this with a call to an LLM provider.
    """
    word = request.word
    direction = request.direction

    # Mock data generation
    if direction == "en_to_zh":
        phonetics = schemas.Phonetics(uk="/həˈləʊ/", us="/həˈloʊ/")
        parts = [
            schemas.PartOfSpeech(pos="noun", meaningEn="A greeting", meaningZh="问候"),
            schemas.PartOfSpeech(pos="verb", meaningEn="To say hello", meaningZh="打招呼"),
        ]
        examples = [
            schemas.Example(sentenceEn=f"Hello, is anyone there?", sentenceZh="你好，有人在吗？"),
            schemas.Example(sentenceEn=f"She said hello to him.", sentenceZh="她向他打招呼。"),
        ]
        synonyms = ["hi", "greetings"]
        antonyms = ["goodbye"]
    else:
        phonetics = schemas.Phonetics(uk="", us="")
        parts = [
            schemas.PartOfSpeech(pos="noun", meaningEn="Example meaning", meaningZh="示例意思"),
        ]
        examples = [
            schemas.Example(sentenceEn="This is an example.", sentenceZh="这是一个示例。"),
        ]
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
