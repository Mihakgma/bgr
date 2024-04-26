from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService

from json import load as json_load


def refine_str(text: str, seps: str=', '):
    text = text.strip()
    tmp_lst = [seps+text[i] if i > 0 and text[i-1] != " " and text[i].isupper()
               else text[i]
               for i in range(len(text))]
    return "".join(tmp_lst)


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
    return refine_str(found_elem_text)
    # return found_elem_text.replace("\n", ", ")


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
