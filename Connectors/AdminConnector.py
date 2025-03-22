from Connectors.Connector import Connector
from Models.Admin import Admin

class AdminConnector(Connector):
    def sign_in(self, username, password):
        if self.conn is None:
            self.connect()

        cursor = self.conn.cursor()
        sql = "SELECT * FROM admin WHERE AdminAccount=%s AND AdminPassword=%s"
        val = (username, password)
        cursor.execute(sql, val)
        dataset = cursor.fetchone()
        ad = None
        if dataset is not None:
            # Vì dùng DictCursor, dataset là một dict chứ không phải tuple
            ad = Admin(
                dataset["AdminID"],
                dataset["AdminFullName"],
                dataset["AdminAccount"],
                dataset["AdminPassword"],
                dataset["AdminPhone"]
            )
        cursor.close()
        return ad
