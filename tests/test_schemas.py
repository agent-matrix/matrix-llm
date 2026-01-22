"""Tests for API schemas."""

import pytest
from pydantic import ValidationError

from matrixllm.api.schemas import (
    OAChatChoice,
    OAChatMessage,
    OAChatRequest,
    OAChatResponse,
    OAEmbeddingData,
    OAEmbeddingsRequest,
    OAEmbeddingsResponse,
)


class TestOAChatMessage:
    """Tests for OAChatMessage schema."""

    def test_create_message(self):
        """Test creating a simple chat message."""
        msg = OAChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self):
        """Test creating an assistant message."""
        msg = OAChatMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_system_message(self):
        """Test creating a system message."""
        msg = OAChatMessage(role="system", content="You are a helpful assistant.")
        assert msg.role == "system"

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = OAChatMessage(role="user", content="Test")
        data = msg.model_dump()
        assert data == {"role": "user", "content": "Test"}

    def test_missing_role_raises_error(self):
        """Test that missing role raises validation error."""
        with pytest.raises(ValidationError):
            OAChatMessage(content="Hello")

    def test_missing_content_raises_error(self):
        """Test that missing content raises validation error."""
        with pytest.raises(ValidationError):
            OAChatMessage(role="user")


class TestOAChatRequest:
    """Tests for OAChatRequest schema."""

    def test_minimal_request(self):
        """Test creating a request with minimal fields."""
        req = OAChatRequest(
            messages=[OAChatMessage(role="user", content="Hello")]
        )
        assert req.model is None
        assert len(req.messages) == 1
        assert req.stream is False

    def test_full_request(self):
        """Test creating a request with all fields."""
        req = OAChatRequest(
            model="gpt-4",
            messages=[
                OAChatMessage(role="system", content="Be helpful"),
                OAChatMessage(role="user", content="Hello"),
            ],
            temperature=0.7,
            max_tokens=100,
            stream=True,
        )
        assert req.model == "gpt-4"
        assert len(req.messages) == 2
        assert req.temperature == 0.7
        assert req.max_tokens == 100
        assert req.stream is True

    def test_default_values(self):
        """Test default values for optional fields."""
        req = OAChatRequest(
            messages=[OAChatMessage(role="user", content="Hello")]
        )
        assert req.temperature is None
        assert req.max_tokens is None
        assert req.stream is False

    def test_empty_messages_is_valid(self):
        """Test that empty messages list is valid."""
        req = OAChatRequest(messages=[])
        assert req.messages == []


class TestOAChatChoice:
    """Tests for OAChatChoice schema."""

    def test_create_choice(self):
        """Test creating a chat choice."""
        choice = OAChatChoice(
            message=OAChatMessage(role="assistant", content="Hello!")
        )
        assert choice.index == 0
        assert choice.finish_reason == "stop"

    def test_custom_index(self):
        """Test creating a choice with custom index."""
        choice = OAChatChoice(
            index=1,
            message=OAChatMessage(role="assistant", content="Hello!"),
            finish_reason="length",
        )
        assert choice.index == 1
        assert choice.finish_reason == "length"


class TestOAChatResponse:
    """Tests for OAChatResponse schema."""

    def test_create_response(self):
        """Test creating a chat response."""
        resp = OAChatResponse(
            id="chatcmpl-123",
            choices=[
                OAChatChoice(
                    message=OAChatMessage(role="assistant", content="Hi!")
                )
            ],
        )
        assert resp.id == "chatcmpl-123"
        assert resp.object == "chat.completion"
        assert len(resp.choices) == 1

    def test_response_serialization(self):
        """Test response serialization."""
        resp = OAChatResponse(
            id="test-id",
            choices=[
                OAChatChoice(
                    message=OAChatMessage(role="assistant", content="Hello")
                )
            ],
        )
        data = resp.model_dump()
        assert data["id"] == "test-id"
        assert data["object"] == "chat.completion"


class TestOAEmbeddingsRequest:
    """Tests for OAEmbeddingsRequest schema."""

    def test_single_input(self):
        """Test request with single string input."""
        req = OAEmbeddingsRequest(input="Hello world")
        assert req.input == "Hello world"
        assert req.model is None

    def test_list_input(self):
        """Test request with list of strings."""
        req = OAEmbeddingsRequest(input=["Hello", "World"])
        assert req.input == ["Hello", "World"]

    def test_with_model(self):
        """Test request with model specified."""
        req = OAEmbeddingsRequest(
            model="text-embedding-ada-002",
            input="Hello",
        )
        assert req.model == "text-embedding-ada-002"


class TestOAEmbeddingData:
    """Tests for OAEmbeddingData schema."""

    def test_create_embedding(self):
        """Test creating embedding data."""
        emb = OAEmbeddingData(index=0, embedding=[0.1, 0.2, 0.3])
        assert emb.index == 0
        assert emb.embedding == [0.1, 0.2, 0.3]

    def test_empty_embedding(self):
        """Test embedding with empty vector."""
        emb = OAEmbeddingData(index=0, embedding=[])
        assert emb.embedding == []


class TestOAEmbeddingsResponse:
    """Tests for OAEmbeddingsResponse schema."""

    def test_create_response(self):
        """Test creating embeddings response."""
        resp = OAEmbeddingsResponse(
            data=[OAEmbeddingData(index=0, embedding=[0.1, 0.2])]
        )
        assert resp.object == "list"
        assert len(resp.data) == 1
        assert resp.model is None

    def test_with_model(self):
        """Test response with model field."""
        resp = OAEmbeddingsResponse(
            data=[OAEmbeddingData(index=0, embedding=[0.1])],
            model="nomic-embed-text",
        )
        assert resp.model == "nomic-embed-text"
