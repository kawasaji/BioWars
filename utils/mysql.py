import pymysql
import time

class DataBase:
    def __init__(self, host: str, user: str, passwd: str, port: int = 3306) -> None:
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.passwd: str = passwd
        self.connections: list = []

    class DbConnect:
        def __init__(self, conn, parent) -> None:
            self.conn = conn
            self.parent: DataBase = parent
            self.time_start: float = time.time()
            self.query_counter: int = 0
            self.errors = (pymysql.MySQLError, pymysql.err.Error, pymysql.err.OperationalError)

        def query(self, query: str, max_retries: int = 10):
            self.query_counter += 1
            retries = 0

            while retries < max_retries:
                try:
                    with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                        return cur.fetchall()
                except self.errors:
                    retries += 1
                    time.sleep(0.1)
                    self.reconnect()
            return []

        def reconnect(self):
            # Повторное подключение к базе данных
            # print(f"Reconnect             ({datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')})")
            try:self.parent.close_connections()
            except self.errors: pass
            try: self.parent.connect(self.conn.db)
            except self.errors: pass

    def select(self, db_name: str, timeout: int = 60 * 60 * 24) -> DbConnect:
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.passwd,
            db=db_name,
            autocommit=True,
            connect_timeout=timeout
        )
        connect = self.DbConnect(conn, self)
        self.connections.append(connect)
        return connect

    def close_connections(self):
        for conn in self.connections:
            conn.conn.close()

    def __del__(self):
        self.close_connections()