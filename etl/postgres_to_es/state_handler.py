import os
import abc
import json
from typing import Any, Optional

from config import logger


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = 'state.json'):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        try:
            with open(self.file_path, 'w') as file:
                json.dump(state, file)
        except Exception as ex:
                logger.error(ex)       

    def retrieve_state(self) -> dict:
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
            except Exception as ex:
                logger.error(ex)
            return data
        return {}
        


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы
    постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    """

    def __init__(self, storage: BaseStorage = JsonFileStorage()):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        data = {key: value}
        self.storage.save_state(data)

    def get_state(self, key: str, default: Optional[str] = None) -> Any:
        """Получить состояние по определённому ключу"""
        data = self.storage.retrieve_state()
        if data.get(key, None):
            return data.get(key)
        return default
