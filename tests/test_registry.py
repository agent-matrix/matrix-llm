"""Tests for the RuntimeRegistry."""

import pytest
from datetime import datetime, timezone

from matrixllm.core.registry import RuntimeNodeState, RuntimeRegistry


class TestRuntimeNodeState:
    """Tests for RuntimeNodeState dataclass."""

    def test_create_minimal_node(self):
        """Test creating a node with minimal fields."""
        node = RuntimeNodeState(
            node_id="test-node",
            connector="relay_link",
        )
        assert node.node_id == "test-node"
        assert node.connector == "relay_link"
        assert node.endpoint is None
        assert node.tags == []
        assert node.models == []
        assert node.capacity == 1
        assert node.healthy is True

    def test_create_full_node(self):
        """Test creating a node with all fields."""
        node = RuntimeNodeState(
            node_id="node-1",
            connector="direct_endpoint",
            endpoint="http://127.0.0.1:8000",
            tags=["gpu", "fast"],
            models=["llama", "mistral"],
            capacity=4,
            meta={"region": "us-west"},
            healthy=True,
        )
        assert node.node_id == "node-1"
        assert node.connector == "direct_endpoint"
        assert node.endpoint == "http://127.0.0.1:8000"
        assert node.tags == ["gpu", "fast"]
        assert node.models == ["llama", "mistral"]
        assert node.capacity == 4
        assert node.meta == {"region": "us-west"}

    def test_last_seen_default(self):
        """Test that last_seen is set to current time by default."""
        before = datetime.now(timezone.utc)
        node = RuntimeNodeState(node_id="test", connector="relay_link")
        after = datetime.now(timezone.utc)
        assert before <= node.last_seen <= after


@pytest.mark.asyncio
class TestRuntimeRegistry:
    """Tests for RuntimeRegistry."""

    async def test_registry_initialization(self):
        """Test creating an empty registry."""
        registry = RuntimeRegistry()
        nodes = await registry.list()
        assert nodes == []

    async def test_upsert_node(self):
        """Test adding a node to the registry."""
        registry = RuntimeRegistry()
        node = RuntimeNodeState(node_id="node-1", connector="relay_link")

        await registry.upsert(node)

        result = await registry.get("node-1")
        assert result is not None
        assert result.node_id == "node-1"

    async def test_upsert_updates_last_seen(self):
        """Test that upsert updates the last_seen timestamp."""
        registry = RuntimeRegistry()
        node = RuntimeNodeState(node_id="node-1", connector="relay_link")

        old_time = node.last_seen
        await registry.upsert(node)

        result = await registry.get("node-1")
        assert result is not None
        assert result.last_seen >= old_time

    async def test_upsert_replaces_existing(self):
        """Test that upserting a node replaces the existing one."""
        registry = RuntimeRegistry()

        node1 = RuntimeNodeState(
            node_id="node-1",
            connector="relay_link",
            capacity=1,
        )
        await registry.upsert(node1)

        node2 = RuntimeNodeState(
            node_id="node-1",
            connector="direct_endpoint",
            capacity=4,
        )
        await registry.upsert(node2)

        result = await registry.get("node-1")
        assert result is not None
        assert result.connector == "direct_endpoint"
        assert result.capacity == 4

    async def test_get_nonexistent_node(self):
        """Test getting a node that doesn't exist."""
        registry = RuntimeRegistry()
        result = await registry.get("nonexistent")
        assert result is None

    async def test_remove_node(self):
        """Test removing a node from the registry."""
        registry = RuntimeRegistry()
        node = RuntimeNodeState(node_id="node-1", connector="relay_link")

        await registry.upsert(node)
        await registry.remove("node-1")

        result = await registry.get("node-1")
        assert result is None

    async def test_remove_nonexistent_node(self):
        """Test removing a node that doesn't exist (should not raise)."""
        registry = RuntimeRegistry()
        # Should not raise
        await registry.remove("nonexistent")

    async def test_list_nodes(self):
        """Test listing all nodes."""
        registry = RuntimeRegistry()

        node1 = RuntimeNodeState(node_id="node-1", connector="relay_link")
        node2 = RuntimeNodeState(node_id="node-2", connector="direct_endpoint")

        await registry.upsert(node1)
        await registry.upsert(node2)

        nodes = await registry.list()
        assert len(nodes) == 2
        node_ids = {n.node_id for n in nodes}
        assert node_ids == {"node-1", "node-2"}

    async def test_touch_updates_last_seen(self):
        """Test that touch updates the last_seen timestamp."""
        registry = RuntimeRegistry()
        node = RuntimeNodeState(node_id="node-1", connector="relay_link")
        await registry.upsert(node)

        old_time = (await registry.get("node-1")).last_seen
        await registry.touch("node-1")
        new_time = (await registry.get("node-1")).last_seen

        assert new_time >= old_time

    async def test_touch_updates_healthy(self):
        """Test that touch can update the healthy status."""
        registry = RuntimeRegistry()
        node = RuntimeNodeState(node_id="node-1", connector="relay_link", healthy=True)
        await registry.upsert(node)

        await registry.touch("node-1", healthy=False)

        result = await registry.get("node-1")
        assert result.healthy is False

    async def test_touch_nonexistent_node(self):
        """Test that touching a nonexistent node does nothing."""
        registry = RuntimeRegistry()
        # Should not raise
        await registry.touch("nonexistent")
        await registry.touch("nonexistent", healthy=False)
