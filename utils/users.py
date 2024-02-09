from utils.mysql import DataBase
from utils.strings import strings
from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    name: str
    username: str | None = None
    def __repr__(self): return strings.format_dict(self.__dict__)

class Users:

    _instance = None
    db: DataBase.DbConnect

    def __new__(cls, tag: str | int) -> User: # в первый раз принимает подключение к базе данных, в следующие разы тег для поиска
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db = tag
            return cls._instance
        else:
            if str(tag).isdigit(): user = cls._instance.db.query(f"SELECT * FROM `tg_users` WHERE `user_id` = '{tag}'")
            else: user = cls._instance.db.query(f"SELECT * FROM `tg_users` WHERE `user_name` = '{tag}'")
            if len(user) == 0: return None
            else: user = user[0]
            return User(user['user_id'], user['name'], user['user_name'])
        
    def get(self, tag: str | int) -> User:
        if str(tag).isdigit(): user = self.db.query(f"SELECT * FROM `tg_users` WHERE `user_id` = '{tag}'")
        else: user = self.db.query(f"SELECT * FROM `tg_users` WHERE `user_name` = '{tag}'")
        if len(user) == 0: return None
        else: user = user[0]
        return User(user['user_id'], user['name'], user['user_name'])