from abc import ABC, abstractmethod
from typing import Any, Optional

from aiogram.fsm.context import FSMContext


class StateData(ABC):
    def __init__(self, state: FSMContext, data_key: str) -> None:
        self._state = state
        self._data_key = data_key

    async def _init(self):
        data = await self._state.get_data()
        if data.get(self._data_key) is None:
            await self._set_data(self._get_init_state_data())

    @abstractmethod
    def _get_init_state_data(self) -> dict[str, Any]:
        ...

    @classmethod
    async def create(cls, state: FSMContext, data_key: str):
        self = cls(state, data_key)
        await self._init()
        return self

    async def _get_data(self) -> dict[str, Any]:
        data = await self._state.get_data()
        return data[self._data_key]

    async def _set_data(self, data: dict[str, Any] | None):
        await self._state.update_data({self._data_key: data})

    async def _update_data(self, data: Optional[dict[str, Any]] = None, **kwargs: Any):
        if data:
            kwargs.update(data)

        state_data = await self._get_data()
        state_data.update(kwargs)
        await self._set_data(state_data)

    async def _get_data_key_value(self, key: str) -> Any:
        data = await self._get_data()
        return data[key]
