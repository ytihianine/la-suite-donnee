from typing import Any

import pytest

from src.infra.io.io_interface import IOInterface


class DummyIO(IOInterface):
    """Concrete implementation of IOInterface for testing."""

    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    def read(self, source: str) -> Any:
        """Read data from the in-memory store."""
        return self.store[source]

    def write(self, destination: str, data: Any) -> None:
        """Write data to the in-memory store."""
        self.store[destination] = data


class TestIOInterface:
    """Tests for the IOInterface abstract class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that IOInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IOInterface()  # type: ignore[abstract]

    def test_write_and_read(self) -> None:
        """Test that a concrete implementation can write and read data."""
        io = DummyIO()
        io.write("key", {"value": 42})

        result = io.read("key")

        assert result == {"value": 42}

    def test_read_missing_key_raises(self) -> None:
        """Test that reading a missing key raises KeyError."""
        io = DummyIO()

        with pytest.raises(KeyError):
            io.read("missing")
