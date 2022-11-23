from src.facebook_autoregister.database.mysql_db import MySQLDB
from tmp.mysql_config import mysql122, mysql52
from src.facebook_autoregister.functions.queries import queries
mysql_52_instance = MySQLDB()
mysql_52_instance.create_connection(mysql52)

mysql_122_instance = MySQLDB()
mysql_122_instance.create_connection(mysql122)


def transfer_script():
    ready_accounts = mysql_52_instance.query_get_data(queries['get_ready_accounts_query'])
    mysql_52_instance.query_set_multiple_data(queries['update_accounts_status_query'], ready_accounts)
    mysql_122_instance.query_set_multiple_data(queries['insert_ready_accounts_query'], ready_accounts)


if __name__ == "__main__":
    transfer_script()
