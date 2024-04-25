from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService

from json import load as json_load


# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
#
# from pandas import DataFrame, read_html, concat, ExcelFile, ExcelWriter, Series
# from pandas import isna as pd_isna
# from pandas import merge as pd_merge
# from math import isnan as math_isnan
#
# from random import uniform as random_uniform
# from random import randint as random_randint
# from time import sleep as time_sleep
#
# from datetime import datetime as dt
#
# from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardText, CF_UNICODETEXT, CloseClipboard
# from pyautogui import hotkey as pyt_hotkey
#
# from re import findall as re_findall
# from re import search as re_search
#
# from tqdm.notebook import tqdm
#
# from shutil import copyfile as shutil_copyfile


def get_element_attribute(driver,
                     css_selector: str,
                     get_href: int = 0,
                     timeout: int = 3):
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException or NoSuchElementException:
        print("Timed out waiting for page to load")
        return ""
    found_element = driver.find_element(By.CSS_SELECTOR, css_selector)
    found_elem_text = found_element.text
    if get_href:
        try:
            found_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
            return ", ".join([i.get_attribute('href') for i in found_elements])
        except BaseException as e:
            print(f'Возникла ошибка <{e}>')
            return ""
        # print(f'Найденный Вэб-Элемент с именем <{found_element}>')
        # found_href = found_element.get_attribute('href')
        # if found_href is not None:
        #     return found_href
        # try:
        #     found_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        #     return [i.get_attribute('href') for i in found_elements]
        # except BaseException as e:
        #     print(f'Возникла ошибка <{e}>')
        #     print('По всей видимости данный элемент - не итерируемый!')
        #     return ""
    return found_elem_text.replace("\n", ", ")


def get_bg_content(driver, css_selector_info: dict):
    if type(css_selector_info) != dict:
        raise ValueError("Неверный тип переданного аргумента <css_selector_info>!")
    [v.append(get_element_attribute(driver=driver,
                                    css_selector=v[0],
                                    get_href=v[1]))
     for (k,v) in css_selector_info.items()]
    return css_selector_info


if __name__ == '__main__':
    # подгружаем json с данными о CSS-Selectors
    css_selector_filename = "..\\resources\\bg_parsing_info.json"
    with open(css_selector_filename) as json_file:
        json_data = json_load(json_file)
    print(type(json_data))
    # print(json_data)

    start_html = "https://hobbyworld.ru/kragmorta"
    with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as driver:
        driver.get(start_html)
        result = get_bg_content(driver=driver, css_selector_info=json_data)
    # Selenium-browser has been closed
    # смотрим полученный результат
    print(*[(k, v) for (k, v) in result.items()], sep="\n")
