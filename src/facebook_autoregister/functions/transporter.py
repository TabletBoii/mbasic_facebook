from src.facebook_autoregister.database.mysql_db import MySQLDB
from src.facebook_autoregister.config.mysql_config import mysql122, mysql52

mysql_instance_52 = MySQLDB()
mysql_instance_52.create_connection(mysql52)
mysql_instance_122 = MySQLDB()
mysql_instance_122.create_connection(mysql122)


def get_available_accounts():
    get_available_accounts_query = """
                                    SELECT phone_number, password FROM facebook_accounts WHERE status = 1
                                   """
    available_accounts = mysql_instance_52.query_get_data(
        get_available_accounts_query)
    return available_accounts


def facebook_account_transporter():
    available_accounts = get_available_accounts()
    insert_accounts_query = f"""
                                INSERT INTO soc_accounts(soc_type, type, work, name, login, password) VALUES(2, \'FbUser100\', 1, \'+\', %s, %s)
                             """
    mysql_instance_122.query_set_multiple_data(
        insert_accounts_query, available_accounts)


if __name__ == "__main__":
    facebook_account_transporter()
