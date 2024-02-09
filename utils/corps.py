from utils.mysql import DataBase
from utils.strings import strings
from dataclasses import dataclass

import time

class Corp:
    key: str
    owner_id: int

    created_from: float = time.time()

    def __repr__(self): return strings.format_dict(self.__dict__)

class Corps:

    _instance = None
    corps: dict[str, dict]
    db: DataBase.DbConnect

    def __new__(cls, user_id: str | int) -> Corp: # в первый раз принимает подключение к базе данных, в следующие разы ид лабы
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db = user_id
            cls._instance.corps = {}
            return cls._instance

        return cls._instance.get(user_id)

    def get(self, user_id: str | int) -> Corp:

        return None