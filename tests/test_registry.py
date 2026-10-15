import pytest

from ferrule.registry import load_registry


def test_shipped_registry_loads_with_empty_scores():
    reg = load_registry(env={})
    assert reg.providers["ollama"].local
    assert all(m.scores == {} for m in reg.models)  # scores only ever come from the eval harness
    assert "qwen2.5-coder:7b" in [m.name for m in reg.models]


def test_hosted_provider_needs_its_key():
    reg = load_registry(env={})
    groq = reg.providers["groq"]
    assert not groq.available({})
    assert groq.available({"GROQ_API_KEY": "gsk_test"})
    assert reg.providers["ollama"].available({})


def test_registry_never_contains_keys():
    text = load_registry.__globals__["DEFAULT_REGISTRY"].read_text()
    assert "api_key:" not in text and "gsk_" not in text and "sk-" not in text


def test_env_override_and_unknown_provider(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text("providers: {a: {base_url: 'http://x', local: true}}\n"
                    "models: [{name: m, provider: b}]\n")
    with pytest.raises(ValueError, match="unknown providers: b"):
        load_registry(env={"FERRULE_REGISTRY": str(path)})


def test_invalid_field_rejected(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text("providers: {a: {base_url: 'http://x', api_key: 'oops'}}\nmodels: []\n")
    with pytest.raises(ValueError, match="api_key"):
        load_registry(path)
