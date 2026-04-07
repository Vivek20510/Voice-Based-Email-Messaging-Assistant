import os
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


def summarize_text(text: str, model: str = None):
    if not model:
        model = os.getenv("NLP_MODEL", "sshleifer/tiny-mbart")

    if pipeline is None:
        raise RuntimeError(
            "transformers package not installed; pip install transformers"
        )

    try:
        language = detect(text)
    except LangDetectException:
        language = "en"

    summarizer = pipeline("summarization", model=model)
    result = summarizer(text, max_length=120, min_length=20, do_sample=False)
    summary = result[0]["summary_text"]
    return {"summary": summary, "language": language}


def suggest_replies(text: str, model: str = None):
    if not model:
        model = os.getenv("NLP_MODEL", "google/flan-t5-small")

    if pipeline is None:
        raise RuntimeError(
            "transformers package not installed; pip install transformers"
        )

    try:
        language = detect(text)
    except LangDetectException:
        language = "en"

    generator = pipeline("text2text-generation", model=model)
    prompt = f"Generate 3 short email replies for the following message: {text}"
    result = generator(prompt, max_length=128, do_sample=False)
    replies = result[0]["generated_text"]
    return {"replies": replies, "language": language}
