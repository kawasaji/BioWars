from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, BOT_TOKEN


class Father:

    def __init__(self, path: str) -> None:

        from utils.users import Users
        from utils.bot import Bot
        from utils.mysql import DataBase
        from utils.localdb import DBConnect

        self.path = path
        self.mysql = DataBase(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD)
        self.users = Users(self.mysql.select('telegram_data'))
        self.bot = Bot(BOT_TOKEN, self)

        self.victims = DBConnect('tables/victims.db')
        self.issues = DBConnect('tables/issues.db')