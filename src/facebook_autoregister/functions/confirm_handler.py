"""System module."""
import json
import sys
import time
from typing import Any

import requests


class OnlineSimData:
    def __init__(self, api_key, service):
        self.apikey = api_key
        self.service = service

    def __fetch_number_by_service(self):
        response = requests.get(f'https://onlinesim.ru/api/getNumbersStats.php'
                                f'?apikey={self.apikey}'
                                f'&country').text
        response = json.loads(response)
        country_code_list = list(response.keys())
        mapped_response = [[response[x]['name'], response[x]['services'].get(
            'service_' + self.service)] for x in country_code_list]
        return mapped_response

    def __get_profitable_code(self, index: int):
        ban_list = [233, 232, 234, 216, 225,
                    91, 226, 221, 7, 223,
                    63, 254, 220, 62, 84,
                    245, 92, 60, 231,
                    964, 31]
        country_list = self.__fetch_number_by_service()
        country_list = list(
            filter(
                lambda x: x[1] is not None and x[1]['count'] >= 4 and x[1]['code'] not in ban_list,
                country_list))
        country_list.sort(key=lambda x: x[1]['price'])
        return country_list[index][1]['code']

    def __check_balance(self) -> bool:
        is_enough_money = requests.get(
            f'https://onlinesim.ru/api/getBalance.php'
            f'?apikey={self.apikey}').text
        is_enough_money = json.loads(is_enough_money)
        if float(is_enough_money['balance']) < 15:
            return False
        return True

    def __get_number_state(self, tzid=None):
        if tzid is not None:
            number_state = requests.get(
                f'https://onlinesim.ru/api/getState.php'
                f'?apikey={self.apikey}'
                f'&tzid={tzid}', timeout=20).text
            number_state = json.loads(number_state)
            return number_state
        else:
            number_state = requests.get(
                f'https://onlinesim.ru/api/getState.php'
                f'?apikey={self.apikey}', timeout=20).text
            number_state = json.loads(number_state)
            if isinstance(number_state, dict):
                print("Number wasn't created")
                return None

            number_state = list(
                filter(
                    lambda a: a['service'] == self.service,
                    number_state))
            return number_state

    def generate_phone_number(self, driver=None) -> Any:
        is_number_exists = self.__get_number_state()
        balance_status = self.__check_balance()

        if not balance_status:
            driver.close()
            driver.quit()
            print('Not enough money')
            sys.exit()
        if is_number_exists is None or isinstance(
                is_number_exists, list) and len(is_number_exists) == 0:
            response_state = True
            origin_index: int = 0
            while response_state:
                country_code = self.__get_profitable_code(origin_index)
                response = requests.get(
                    f'https://onlinesim.ru/api/getNum.php'
                    f'?apikey={self.apikey}'
                    f'&service={self.service}'
                    f'&action=getNumber'
                    f'&country={country_code}',
                    timeout=20).text
                response = json.loads(response)
                response_state = True if response['response'] == 'NO_NUMBER' else False
                if response_state:
                    origin_index += 1
                    continue
                phone_number_state = self.__get_number_state(
                    tzid=response["tzid"])
                phone_number = phone_number_state[0]['number']
                tzid = phone_number_state[0]["tzid"]
                return phone_number, tzid
        else:
            phone_number = is_number_exists[0]['number']
            tzid = is_number_exists[0]["tzid"]
            return phone_number, tzid

    def get_number_code(self):
        msg_is_true = None
        number_of_requests = 0
        while msg_is_true is None:
            if number_of_requests >= 15:
                return None
            phone_number_adv_info = requests.get(
                f'https://onlinesim.ru/api/getState.php'
                f'?apikey={self.apikey}', timeout=20).text
            phone_number_adv_info = json.loads(phone_number_adv_info)

            if phone_number_adv_info[0].get('msg') is not None:
                return phone_number_adv_info[0].get('msg')
            number_of_requests += 1
            time.sleep(10)

    def close_operation(self, driver, tzid) -> None:
        response = requests.get(f"https://onlinesim.ru/api/setOperationOk.php"
                                f"?apikey={self.apikey}"
                                f"&tzid={tzid}", timeout=20)
        driver.close()
        driver.quit()
        time.sleep(10)
