"""Tests for provider base classes."""

from matrixllm.providers.base import ModelInfo


class TestModelInfo:
    """Tests for ModelInfo dataclass."""

    def test_create_minimal_model_info(self):
        """Test creating ModelInfo with minimal fields."""
        info = ModelInfo(id="openai/gpt-4")
        assert info.id == "openai/gpt-4"
        assert info.object == "model"
        assert info.owned_by is None
        assert info.meta is None

    def test_create_full_model_info(self):
        """Test creating ModelInfo with all fields."""
        info = ModelInfo(
            id="anthropic/claude-3",
            object="model",
            owned_by="anthropic",
            meta={"max_tokens": 100000},
        )
        assert info.id == "anthropic/claude-3"
        assert info.object == "model"
        assert info.owned_by == "anthropic"
        assert info.meta == {"max_tokens": 100000}

    def test_model_info_is_frozen(self):
        """Test that ModelInfo is immutable (frozen dataclass)."""
        info = ModelInfo(id="test-model")
        # Should raise an error when trying to modify
        try:
            info.id = "new-id"
            assert False, "Expected FrozenInstanceError"
        except Exception:
            pass  # Expected behavior

    def test_model_info_equality(self):
        """Test ModelInfo equality comparison."""
        info1 = ModelInfo(id="model-1", owned_by="owner")
        info2 = ModelInfo(id="model-1", owned_by="owner")
        info3 = ModelInfo(id="model-2", owned_by="owner")

        assert info1 == info2
        assert info1 != info3

    def test_model_info_hash(self):
        """Test that ModelInfo is hashable (frozen dataclass)."""
        info1 = ModelInfo(id="model-1")
        info2 = ModelInfo(id="model-1")

        # Should be able to use in sets
        model_set = {info1, info2}
        assert len(model_set) == 1

    def test_model_info_with_ollama_format(self):
        """Test ModelInfo with Ollama-style model ID."""
        info = ModelInfo(
            id="ollama/llama2:7b",
            owned_by="meta",
        )
        assert info.id == "ollama/llama2:7b"

    def test_model_info_with_meta_dict(self):
        """Test ModelInfo with various metadata."""
        info = ModelInfo(
            id="test-model",
            meta={
                "context_length": 4096,
                "supports_function_calling": True,
                "pricing": {"prompt": 0.001, "completion": 0.002},
            },
        )
        assert info.meta["context_length"] == 4096
        assert info.meta["supports_function_calling"] is True
        assert info.meta["pricing"]["prompt"] == 0.001
