from sqlalchemy import text
from sqlalchemy import create_engine


class Database:
    __db = None

    def __init__(self):
        self.__db = create_engine("sqlite:///M:\\flask\\sqlite\\flask.db")

    def query(self, sql: str):
        result = self.__db.execute(text(sql))
        return result.fetchall()

    def get_transaction(self, trans_id):
        sql = text("SELECT * FROM transactions WHERE id = ?")
        transaction = self.__db.execute(sql, {trans_id}).fetchone()
        return transaction
