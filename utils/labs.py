from utils.mysql import DataBase
from utils.strings import strings
from dataclasses import dataclass

from tinydb import TinyDB, Query

import time

class DotDict:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DotDict(value))
            else:
                setattr(self, key, value)

class Lab:
    user_id: int                    # ид владельца лабы
    name: str                       # имя владельца, подтягивается автоматически
    username: str | None = None     # юз пользователя

    class root:
        commit: bool = True         # флаг отвечает за обновление лабы, если False, лаба перестает обновляться в бд
        premium_start: float = 0    # время создания премиума
        premium_long: float = 0     # сколько будет длиться премиум

        @property                   # поле возвращает тру фолз в зависимости от акитивности према
        def is_premium(self) -> bool: return time.time() < (self.premium_start + self.premium_long)

        last_message: float = 0     # время последнего зарегистрированного сообщения
        last_command: float = 0     # время последней отправленной команды
        slient: bool = False        # флаг показывает будет ли пользователь получать теги от бота
        ignore: bool = False        # игнорирует ли бот команды пользователя
        violations: int = 0         # колво нарушений

    class stats:
        qualification: int = 1      # квалификация
        security: int = 1           # безопасность
        mortality: int = 5          # летальность
        infectiousness: int = 1     # заразность
        immunity: int = 1           # иммунитет
        patogens: int = 10          # колво всех патогенов
        real_pats: int = 10         # текущее колво патогенов

    class bio:
        res: int = 100              # биоресурс
        exp: int = 100              # биоопыт
        coins: int = 100            # коины
        avocados: int = 0           # авокадо

    class infects:
        all: int = 0                # колличество всех операций
        suc: int = 0                # колличество успешных операций
        victims: int = 0            # колличество жертв

    class issues:
        all: int = 0                # все попытки заразить этого пользователя
        suc: int = 0                # успешные попытки заразить этого пользователя, одновременно и колличество всех болезней

    class names:
        patogen_name: str = None    # имя патогена
        lab_name: str = None        # имя лабы

        validate: bool = False      # обозначает будет ли проверяться имена на токсичность при изменении
        block: bool = False         # если тру, измеение имен и тд заблокировано

    class corp:
        key: str = None             # ключ корпы
        owner_id: int = None        # айди владельца корпы
        name: str = None            # название корпы

    def __repr__(self): return strings.format_dict(self.__dict__)

class Labs:

    _instance = None
    labs: dict[str, dict]
    db: DataBase.DbConnect

    def __new__(cls, user_id: str | int) -> Lab: # в первый раз принимает подключение к базе данных, в следующие разы ид лабы
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db = user_id
            cls._instance.labs = {}
            return cls._instance

        return cls._instance.get(user_id)

    def get(self, user_id: str | int) -> Lab:

        return None