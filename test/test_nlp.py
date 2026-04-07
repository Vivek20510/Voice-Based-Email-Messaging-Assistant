from src.services.nlp_service import summarize_text, suggest_replies


def test_summarize_returns_dict(monkeypatch):
    class Dummy:
        def __call__(self, text, **kwargs):
            return [{"summary_text": "Short summary"}]

    monkeypatch.setattr(
        "src.services.nlp_service.pipeline", lambda task, model: Dummy()
    )
    monkeypatch.setattr("src.services.nlp_service.detect", lambda text: "en")
    result = summarize_text("Some long text to summarize", model="dummy")
    assert result == {"summary": "Short summary", "language": "en"}


def test_suggest_replies_returns_dict(monkeypatch):
    class Dummy:
        def __call__(self, prompt, **kwargs):
            return [{"generated_text": "Reply 1; Reply 2"}]

    monkeypatch.setattr(
        "src.services.nlp_service.pipeline", lambda task, model: Dummy()
    )
    monkeypatch.setattr("src.services.nlp_service.detect", lambda text: "en")
    suggestion = suggest_replies("Please respond")
    assert suggestion == {"replies": "Reply 1; Reply 2", "language": "en"}
