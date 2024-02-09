import traceback
import sqlite3

class DBConnect:
    def __init__(self, path) -> None:
        open(path, 'a+').close()
        self.conn = sqlite3.connect(path)

    def query(self, query: str, dictionary: bool = True):
        cur = self.conn.cursor()
        try: cur.execute(query)
        except:
            print(query)
            traceback.print_exc()
            cur.close()
            return []
        if cur.description:
            if dictionary:
                columns = [column[0] for column in cur.description]
                rows = cur.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
            else: result = cur.fetchall()
        else: result = {}
        cur.close()
        self.conn.commit()
        return result

    @property
    def tables(self):
        t = [i['name'] for i in self.query("SELECT name FROM sqlite_master WHERE type='table'")]
        t.remove('sqlite_sequence')
        return t