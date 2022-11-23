"""System module."""
import json
import time
import pytz
import string
import secrets
import requests
import requests.exceptions as req_exceptions
from mimesis import Person
from datetime import datetime
from random import uniform, randint
from src.facebook_autoregister.database.mysql_db import MySQLDB
from src.facebook_autoregister.config.mysql_config import mysql52
from mimesis.enums import Gender, Locale
from gologin import GoLogin, getRandomPort
from seleniumwire.webdriver import ChromeOptions, Chrome


db_instance_52 = MySQLDB()
db_instance_52.create_connection(mysql52)


class Utilities:
    def __init__(self,
                 online_sim_api_key: str,
                 gologin_api_key: str,
                 gologin_profile_id: str,
                 chromedriver_path: str):
        self.online_sim_api_key = online_sim_api_key
        self.gologin_api_key = gologin_api_key
        self.gologin_profile_id = gologin_profile_id
        self.chromedriver_path = chromedriver_path

    @staticmethod
    def change_proxy() -> tuple:
        get_proxy_query = '''
                            SELECT proxy, port, login, password, id, error, change_proxy_link
                            FROM proxies
                            WHERE status != 1 AND status != 2 LIMIT 1
                          '''
        update_used_proxy_query = '''
                                    UPDATE proxies
                                    SET status = 0
                                    WHERE status != 2
                                  '''
        proxy = db_instance_52.query_get_data(get_proxy_query)
        if len(proxy) == 0:
            db_instance_52.query_set_data(update_used_proxy_query)
            proxy = db_instance_52.query_get_data(get_proxy_query)
        proxy_url = proxy[0][0]
        proxy_port = proxy[0][1]
        proxy_username = proxy[0][2]
        proxy_password = proxy[0][3]
        proxy_id = proxy[0][4]
        change_proxy_link = proxy[0][6]
        current_datetime = datetime.now(
            pytz.timezone("Asia/Almaty")).strftime("%Y-%m-%d %H:%M:%S")
        print('proxy_url: ', proxy_url, "\nproxy_port: ", proxy_port, "\n")
        db_instance_52.query_set_data(f'''
                                        UPDATE proxies
                                        SET status = 1, use_date = \'{current_datetime}\'
                                        WHERE id = {proxy_id} AND status != 2
                                       ''')
        if isinstance(change_proxy_link, str):
            print("change_proxy_link: ", change_proxy_link)
            requests.get(change_proxy_link, timeout=20)
            time.sleep(12)
        return proxy_url, proxy_port, proxy_username, proxy_password, proxy_id, change_proxy_link

    @staticmethod
    def insert_account_data(
            first_name: str,
            last_name: str,
            password: str,
            phone_number: str,
            cookies: str) -> None:
        insert_account_query = f'''
                                    INSERT INTO facebook_accounts
                                    (first_name,
                                    last_name,
                                    phone_number,
                                    password,
                                    status,
                                    cookies)
                                    VALUES
                                    (\'{first_name}\',
                                    \'{last_name}\',
                                    \'{phone_number}\',
                                    \'{password}\',
                                    1,
                                    \'{cookies}\')
                                '''
        db_instance_52.query_set_data(insert_account_query)

    @staticmethod
    def type_to_input(text_to_type: str, selenium_field) -> None:
        for item in text_to_type:
            selenium_field.send_keys(item)
            time.sleep(uniform(0.05, 0.5))

    @staticmethod
    def set_gologin_proxy(
            proxy: tuple,
            profile_id: str,
            api_token: str) -> None:
        url = f"https://api.gologin.com/browser/{profile_id}/proxy"

        payload = json.dumps({
            "autoProxyRegion": "us",
            "host": f"{proxy[0]}",
            "mode": "http",
            "password": f"{proxy[3]}",
            "port": f"{proxy[1]}",
            "torProxyRegion": "us",
            "username": f"{proxy[2]}"
        })
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

        requests.request("PATCH", url, headers=headers, data=payload)

    @staticmethod
    def update_gologin_fingerprint(profile_id: str, api_token: str) -> None:
        try:
            url: str = "https://api.gologin.com/browser/fingerprints"

            payload = json.dumps({
                "browsersIds": [
                    profile_id
                ]
            })
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }

            requests.request(
                "PATCH",
                url,
                headers=headers,
                data=payload,
                timeout=20)
        except req_exceptions.ConnectionError as error:
            print(error)

    @staticmethod
    def generate_name(sex=1) -> tuple:
        person = Person(Locale.EN)
        match sex:
            case 2:
                first_name: str = person.first_name(gender=Gender.MALE)
                last_name: str = person.last_name(gender=Gender.MALE)
            case 1:
                first_name: str = person.first_name(gender=Gender.FEMALE)
                last_name: str = person.last_name(gender=Gender.FEMALE)
            case _:
                first_name: str = person.first_name(gender=Gender.MALE)
                last_name: str = person.last_name(gender=Gender.MALE)

        return first_name, last_name

    @staticmethod
    def generate_password() -> str:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        return password

    @staticmethod
    def get_user_agent(path) -> str:
        with open(path) as user_agent_file:
            user_agent_json = user_agent_file.read()
        user_agent_json = json.loads(user_agent_json)
        return user_agent_json[randint(0, len(user_agent_json) - 1)]

    def get_chromedriver(self, proxy: tuple, user_agent=None):
        self.set_gologin_proxy(
            proxy,
            self.gologin_profile_id,
            self.gologin_api_key)
        self.update_gologin_fingerprint(
            self.gologin_profile_id, self.gologin_api_key)

        gl = GoLogin({
            'token': self.gologin_api_key,
            'profile_id': self.gologin_profile_id,
            'port': getRandomPort()
        })

        try:
            debugger_address = gl.start()
        except req_exceptions.SSLError as error:
            print(error)
            return False
        options: ChromeOptions = ChromeOptions()
        options.add_argument('--host-rules=MAP * localhost')
        options.add_experimental_option("debuggerAddress", debugger_address)

        if user_agent:
            options.add_argument('--user-agent=%s' % user_agent)

        chromedriver = Chrome(
            options=options,
            executable_path=self.chromedriver_path)
        return chromedriver
