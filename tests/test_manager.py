"""Tests for ContainerManager."""

from unittest.mock import Mock

from django_testcontainers_plus.manager import ContainerManager
from django_testcontainers_plus.providers.base import ContainerProvider


class MockSettings:
    """Mock Django settings object."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockProvider(ContainerProvider):
    """Mock container provider for testing."""

    def __init__(self, name: str = "mock", auto_detect: bool = True):
        self._name = name
        self._auto_detect = auto_detect

    @property
    def name(self) -> str:
        return self._name

    def can_auto_detect(self, settings) -> bool:
        return self._auto_detect

    def get_container(self, config):
        container = Mock()
        container.start = Mock()
        container.stop = Mock()
        return container

    def update_settings(self, container, settings, config):
        return {"TEST_CONFIG": {self.name: "updated"}}

    def get_default_config(self):
        return {"default": True}


class TestContainerManager:
    """Test ContainerManager class."""

    def test_init(self):
        """Test manager initialization."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        assert manager.settings == settings
        assert isinstance(manager.providers, list)
        assert manager.active_containers == {}
        assert manager.settings_updates == {}

    def test_get_testcontainers_config_missing(self):
        """Test getting config when TESTCONTAINERS is not defined."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        config = manager.get_testcontainers_config()
        assert config == {}

    def test_get_testcontainers_config_exists(self):
        """Test getting config when TESTCONTAINERS is defined."""
        testcontainers_config = {"postgres": {"enabled": True}}
        settings = MockSettings(TESTCONTAINERS=testcontainers_config)
        manager = ContainerManager(settings)

        config = manager.get_testcontainers_config()
        assert config == testcontainers_config

    def test_detect_needed_containers_auto_detect(self):
        """Test auto-detection of needed containers."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=True)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        assert len(needed) == 1
        assert needed[0] == mock_provider

    def test_detect_needed_containers_auto_detect_disabled(self):
        """Test auto-detection when provider cannot detect."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=False)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        assert len(needed) == 0

    def test_detect_needed_containers_explicitly_enabled(self):
        """Test explicitly enabled containers."""
        settings = MockSettings(TESTCONTAINERS={"postgres": {"enabled": True}})
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=False)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        assert len(needed) == 1
        assert needed[0] == mock_provider

    def test_detect_needed_containers_explicitly_disabled(self):
        """Test explicitly disabled containers."""
        settings = MockSettings(TESTCONTAINERS={"postgres": {"enabled": False}})
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=True)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        assert len(needed) == 0

    def test_detect_needed_containers_auto_false(self):
        """Test containers with auto=False but enabled defaults to True."""
        settings = MockSettings(TESTCONTAINERS={"postgres": {"auto": False}})
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=True)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        # Even with auto=False, provider is added because enabled defaults to True
        assert len(needed) == 1

    def test_detect_needed_containers_auto_false_enabled_false(self):
        """Test containers with both auto=False and enabled=False."""
        settings = MockSettings(TESTCONTAINERS={"postgres": {"auto": False, "enabled": False}})
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=True)
        manager.providers = [mock_provider]

        needed = manager.detect_needed_containers()
        assert len(needed) == 0

    def test_start_containers(self):
        """Test starting containers."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=True)
        manager.providers = [mock_provider]

        updates = manager.start_containers()

        assert "TEST_CONFIG" in updates
        assert updates["TEST_CONFIG"]["postgres"] == "updated"
        assert "postgres" in manager.active_containers
        assert manager.active_containers["postgres"].start.called

    def test_start_containers_with_config(self):
        """Test starting containers with custom config."""
        config = {
            "postgres": {
                "enabled": True,
                "image": "postgres:15",
            }
        }
        settings = MockSettings(TESTCONTAINERS=config)
        manager = ContainerManager(settings)

        mock_provider = MockProvider("postgres", auto_detect=False)
        manager.providers = [mock_provider]

        manager.start_containers()

        assert "postgres" in manager.active_containers

    def test_stop_containers(self):
        """Test stopping containers."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        mock_container = Mock()
        mock_container.stop = Mock()
        manager.active_containers["postgres"] = mock_container

        manager.stop_containers()

        assert mock_container.stop.called
        assert len(manager.active_containers) == 0

    def test_stop_containers_handles_exceptions(self):
        """Test stopping containers handles exceptions gracefully."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        mock_container = Mock()
        mock_container.stop = Mock(side_effect=Exception("Stop failed"))
        manager.active_containers["postgres"] = mock_container

        manager.stop_containers()

        assert len(manager.active_containers) == 0

    def test_merge_updates_simple(self):
        """Test simple settings merge."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        target = {}
        updates = {"KEY": "value"}

        manager._merge_updates(target, updates)

        assert target == {"KEY": "value"}

    def test_merge_updates_nested(self):
        """Test nested settings merge."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        target = {"DATABASES": {"default": {"ENGINE": "sqlite"}}}
        updates = {"DATABASES": {"default": {"HOST": "localhost"}}}

        manager._merge_updates(target, updates)

        assert target["DATABASES"]["default"]["ENGINE"] == "sqlite"
        assert target["DATABASES"]["default"]["HOST"] == "localhost"

    def test_merge_updates_override(self):
        """Test settings merge with override."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        target = {"KEY": "old"}
        updates = {"KEY": "new"}

        manager._merge_updates(target, updates)

        assert target["KEY"] == "new"

    def test_multiple_providers(self):
        """Test starting multiple containers."""
        settings = MockSettings()
        manager = ContainerManager(settings)

        provider1 = MockProvider("postgres", auto_detect=True)
        provider2 = MockProvider("redis", auto_detect=True)
        manager.providers = [provider1, provider2]

        updates = manager.start_containers()

        assert "postgres" in manager.active_containers
        assert "redis" in manager.active_containers
        assert updates["TEST_CONFIG"]["postgres"] == "updated"
        assert updates["TEST_CONFIG"]["redis"] == "updated"
