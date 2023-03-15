from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .base import Store


from .memory import MemoryStore

__all__ = ("StoreRegistry",)


def default_default_factory(name: str) -> Store:
    return MemoryStore()


class StoreRegistry:
    """Registry for :class:`Store <.base.Store>` instances."""

    __slots__ = ("_stores", "_default_factory")

    def __init__(
        self, stores: dict[str, Store] | None = None, default_factory: Callable[[str], Store] = default_default_factory
    ) -> None:
        """Initialize ``StoreRegistry``.

        Args:
            stores: A dictionary of store names to stores used to initialize the registry
            default_factory: A callable use by :meth:`StoreRegistry.get` to provide a store if the requested name hasn't
                been registered yet. This callable receives the requested name and should return a
                :class:`Store <.base.Store>`
        """
        self._stores = stores or {}
        self._default_factory = default_factory

    def register(self, name: str, store: Store, override: bool = False) -> None:
        """Register a new :class:`Store <.base.Store>`.

        Args:
            name: Name to register the store under
            store: The store to register
            override: Whether to allow overriding an existing store of the same name

        Raises:
            ValueError: If a store is already registered under this name and ``override`` is not ``True``
        """
        if not override and name in self._stores:
            raise ValueError(f"Store with the name {name!r} already exists")
        self._stores[name] = store

    def get(self, name: str) -> Store:
        """Get a store registered under ``name``. If no such store is registered, create a store using the default
        factory with ``name`` and register the returned store under ``name``.

        Args:
            name: Name of the store

        Returns:
            A :class:`Store <.base.Store>`
        """
        store = self._stores.get(name)
        if not store:
            store = self._stores[name] = self._default_factory(name)
        return store  # noqa: RET504

    @property
    def default(self) -> Store:
        """Return the default store (i.e. the store registered under the name ``default``.

        Equivalent to ``registry.get("default")``
        """
        return self.get("default")
