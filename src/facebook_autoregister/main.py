import os.path
from time import sleep
from random import randint
from src.facebook_autoregister.functions.utils import Utilities
from seleniumwire.webdriver import Chrome
from requests.exceptions import ProxyError
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from src.facebook_autoregister.functions.confirm_handler import OnlineSimData
from selenium.webdriver.support.select import Select
from config import config

api_key_os: str = config["TOKENS"]["api_key_os"]
api_token_gl: str = config["TOKENS"]["api_token_gl"]
profile_id: str = config["TOKENS"]["profile_id"]
ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
chromedriver_path: str = ROOT_DIR + '/chromedriver'


def main(link='https://mbasic.facebook.com'):
    selenium_utilities = Utilities(
                            api_key_os,
                            api_token_gl,
                            profile_id,
                            chromedriver_path)
    online_sim_data = OnlineSimData(api_key_os, '3223')
    iterations = 1
    while True:
        print(f'______________Attempt {iterations}______________')
        iterations += 1
        proxy: tuple = selenium_utilities.change_proxy()
        try:
            driver: Chrome = selenium_utilities.get_chromedriver(proxy)
            if not driver:
                continue
        except ProxyError:
            print("Proxy connection lost")
            continue
        driver.get(link)
        driver.implicitly_wait(30.0)
        sleep(3)

        driver.find_element(By.XPATH, '//input[@name=\'sign_up\']').click()
        sleep(2)

        phone_number_input = driver.find_element(By.NAME, "reg_email__")
        generated_number = online_sim_data.generate_phone_number(driver=driver)
        number = generated_number[0]
        print("Phone number: ", number)
        tzid: str = generated_number[1]
        selenium_utilities.type_to_input(number, phone_number_input)
        sleep(3)

        password_input = driver.find_element(By.NAME, "reg_passwd__")
        password_value: str = selenium_utilities.generate_password()
        selenium_utilities.type_to_input(password_value, password_input)

        print("Password: ", password_value)
        sleep(2)

        select = Select(
            driver.find_element(
                By.XPATH,
                "//select[@title='Месяц']"))
        select.select_by_value(str(randint(1, 11)))
        sleep(2)

        select = Select(
            driver.find_element(
                By.XPATH,
                "//select[@title='День']"))
        select.select_by_value(str(randint(1, 28)))
        sleep(2)

        select = Select(
            driver.find_element(
                By.XPATH,
                "//select[@title='Год']"))
        select.select_by_value(str(randint(1970, 2004)))
        sleep(2)

        sex_value: int = randint(1, 2)
        driver.find_element(
            By.XPATH,
            f'//input[@name=\'sex\'][@value=\'{sex_value}\']').click()

        first_name, last_name = selenium_utilities.generate_name(sex=sex_value)
        print("First name: ", first_name)
        print("Last name: ", last_name)

        first_name_input = driver.find_element(
            By.XPATH, "//input[@name=\'firstname\']")
        sleep(5)
        last_name_input = driver.find_element(
            By.XPATH, "//input[@name=\'lastname\']")
        sleep(5)

        selenium_utilities.type_to_input(first_name, first_name_input)
        sleep(1)
        selenium_utilities.type_to_input(last_name, last_name_input)

        sleep(5)
        driver.find_element(
            By.XPATH,
            '//input[@type=\'submit\'][@name=\'submit\']').click()
        sleep(5)
        try:
            driver.find_element(By.XPATH, '//a[@target = \'_self\']').click()
            sleep(5)
            sms = online_sim_data.get_number_code()
            if sms is None:
                print(number, " didn't send the code")
                online_sim_data.close_operation(driver, tzid)
                continue
            sms_input = driver.find_element(By.XPATH, '//input[@name=\'c\']')
            selenium_utilities.type_to_input(sms, sms_input)
            sleep(5)

            driver.find_element(
                By.XPATH, '//input[@name=\'submit[confirm]\']').click()

            sleep(3)
            cookies = driver.get_cookies()
            cookies = ', '.join(map(str, cookies))
            selenium_utilities.insert_account_data(
                first_name, last_name, password_value, number, cookies)
            online_sim_data.close_operation(driver, tzid)
            print(number, " was successfully created")

        except NoSuchElementException:
            print('FIRED')
            sleep(40)
            online_sim_data.close_operation(driver, tzid)


if __name__ == "__main__":
    main()
