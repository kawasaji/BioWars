from strings import strings
import time
import inspect


"""
Штука работает за счет анотаций, если существует анотация к полю, оно будет в конечном объекте
Можно установить значение по умолчанию для поля, но анотация обятельна!
"""

class Lab:
    user_id: int                    # ид владельца лабы
    name: str                       # имя владельца, подтягивается автоматически
    username: str | None = None     # юз пользователя

    class root:
        commit: bool = True         # флаг отвечает за обновление лабы, если False, лаба перестает обновляться в бд
        premium_start: float = 0    # время создания премиума
        premium_long: float = 0     # сколько будет длиться премиум

        @property                   # поле возвращает тру фолз в зависимости от акитивности према
        def is_premium(self) -> bool:
            return time.time() < (self.premium_start + self.premium_long)

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

    def __str__(self): 
        result = '{'
        indent=4*' '
        for key, value in self.__dict__.items():
            if isinstance(value, str): result += f"\n{indent}'{key}': '{value}',"
            else: result += f"\n{indent}'{key}': {str(value)},"

        return result + '\n}'


    

class dbLab:
    def __new__(self, obj, data: dict = {}) -> Lab:
        for a in obj.__annotations__:
            setattr(obj, a, data.get(a) if a in data else obj.__dict__.get(a))
            
        for name, member in inspect.getmembers(obj):
            if inspect.isclass(member) and member != obj.__class__:
                static = {}
                for a in member.__annotations__:
                    static[a] = data[name].get(a) if name in data and a in data[name] else member.__dict__.get(a)

                member.__init__ = dbLab.__init__
                member.__repr__ = dbLab.__str__
                member = member(static)
                obj.__dict__[name] = member

        return obj
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict): setattr(self, key, self.__class__(value))
            else: setattr(self, key, value)
    def __str__(self): return str(self.__dict__)

lab = dbLab(Lab(), {"user_id": 228, "root": {"ignore": 45}})

print(lab)