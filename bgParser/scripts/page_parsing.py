from json import dump as json_dump
from json import load as json_load

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.notebook import tqdm
from webdriver_manager.chrome import ChromeDriverManager


def get_elements_attribute(driver,
                           css_selector,
                           attr_name: str,
                           separator: str):
    try:
        found_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        return separator.join([i.get_attribute(attr_name) for i in found_elements])
    except BaseException as e:
        print(f'Возникла ошибка <{e}>')
        return ""


def refine_str(text: str, seps: str=', '):
    text = text.strip()
    tmp_lst = [seps+text[i] if i > 0 and
               text[i-1] != " " and
               text[i].isupper() and
               not text[i-1].isupper()
               else text[i]
               for i in range(len(text))]
    return "".join(tmp_lst)


def parse_value(driver,
                css_selector: str,
                source_type: int = 0,
                separator: str = ", ",
                need_replace_newline: int = 0,
                timeout: int = 3):
    # print(css_selector)
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException or NoSuchElementException:
        print("Timed out waiting for page to load")
        return ""

    found_element = driver.find_element(By.CSS_SELECTOR, css_selector)
    if source_type == 1:  # get_attribute('href')
        res = get_elements_attribute(driver=driver,
                                     css_selector=css_selector,
                                     attr_name='href',
                                     separator=separator)
        return res
    elif source_type == 2:  # get_attribute('src')
        res = get_elements_attribute(driver=driver,
                                     css_selector=css_selector,
                                     attr_name='src',
                                     separator=separator)
        return res

    found_elem_text = found_element.text
    if "\n" in found_elem_text and need_replace_newline == 1:
        return found_elem_text.replace("\n", separator)
    return refine_str(found_elem_text)


def get_bg_content(driver,
                   url: str,
                   css_selector_info: dict,
                   result_dict: dict):
    if type(url) != str and not url.startswith("https://"):
        raise ValueError("Неверный тип переданного аргумента <url>!")
    if type(result_dict) != dict:
        raise ValueError("Неверный тип переданного аргумента <result_dict>!")
    if type(css_selector_info) != dict:
        raise ValueError("Неверный тип переданного аргумента <css_selector_info>!")

    # url = driver.current_url
    if url not in result_dict or len(result_dict[url]) == 0:
        result_dict[url] = {}
        page_not_found_error = "Запрашиваемая страница не найдена"
        if page_not_found_error in driver.page_source:
            result_dict[url]["error"] = page_not_found_error
        else:  # запрашиваемая страница существует
            try:
                for (k, v) in css_selector_info.items():
                    curr_value = parse_value(driver=driver,
                                             css_selector=v[0],
                                             source_type=v[1],
                                             need_replace_newline=v[2])
                    result_dict[url][k] = curr_value
                result_dict[url]["parsed_ok"] = 1
                result_dict[url]["duplicates"] = 0
                result_dict[url]["error"] = ""
            except BaseException as e:
                error_txt = f"{v}_{e}"
                result_dict[url]["error"] = error_txt
    elif url in result_dict:
        result_dict[url]["duplicates"] += 1
    return result_dict


def main_func(css_selector_filename,
                  start_htmls,
                  res_dict_path,
                  show_parsed_data: bool=False,
                  access_error_limit: int = 12):
    if type(show_parsed_data) != bool:
        raise TypeError("Ошибочный тип данных для аргумента <show_parsed_data>")
    if type(access_error_limit) != int:
        raise TypeError("Ограничитель количества ошибок парсинга <access_error_limit> должен быть целым числом!")
    # подгружаем json с данными о CSS-Selectors
    with open(css_selector_filename) as json_file:
        json_data = json_load(json_file)
    # print(type(json_data))
    with open(res_dict_path) as json_file:
        test_dict = json_load(json_file)
    # test_dict = {}
    with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as driver:
        errors_in_row = []
        error_counter = 0
        for html in tqdm(start_htmls):
            if access_error_limit == error_counter:
                print(f"Процесс парсинга прерван из-за достижения лимита <{access_error_limit}> на НЕПРЕРЫВНЫЕ ОШИБКИ")
                break
            try:
                if html not in test_dict:
                    driver.get(html)
                test_dict = get_bg_content(driver=driver,
                                           url=html,
                                           css_selector_info=json_data,
                                           result_dict=test_dict)
                if error_counter != 0:
                    errors_in_row.append(error_counter)
                    error_counter = 0
            except BaseException or WebDriverException:
                error_counter += 1
                answer = input('Для отмены процесса парсинга нажмите х или Х')
                answer = answer.lower().strip()
                if 'x' in answer or 'х' in answer:
                    break
    errors_in_row.append(error_counter)
    print(f"В ходе парсинга последнее количество подряд следующих ошибок составило: <{error_counter}>")
    print(f"В ходе парсинга наибольшее количество подряд следующих ошибок составило: <{max(errors_in_row)}>")
    print(f"В ходе парсинга количество ошибочных эпизодов составило: <{len(errors_in_row)}>")
    # Selenium-browser has been closed
    if show_parsed_data:
        # смотрим полученный результат
        print(*[(k, *[(col, val) for (col, val) in v.items()])
                for (k, v) in test_dict.items()], sep="\n")

    with open(res_dict_path, "w") as jsonFile:
        json_dump(test_dict, jsonFile)


if __name__ == '__main__':
    # объявление переменных
    css_selector_filename = "..\\resources\\bg_parsing_info.json"
    start_htmls = [
        "https://hobbyworld.ru/kragmorta",
        "https: // hobbyworld.ru / mir - fantastiki - 245",
        "https://hobbyworld.ru/cat",  # порченый урл!!!
        "https://hobbyworld.ru/catan-kupci-i-varvari",
        "https://hobbyworld.ru/catan-kupci-i-varvari"
    ]
    res_dict_path = "..\\output\\test_parsed_pages.json"
    main_func(css_selector_filename,
              start_htmls,
              res_dict_path)
