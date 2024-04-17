from time import sleep as time_sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service as ChromiumService
from os import getcwd as os_getcwd
from os import chdir as os_chdir
from json import load as json_load
from re import findall as re_findall

from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    ElementNotInteractableException, StaleElementReferenceException

from tqdm.notebook import tqdm


# подгружаем json с данными
with open("..\\resources\\dict.json") as json_file:
    json_data = json_load(json_file)




class WebParser:
    exclude_marks_web_pages = [
        "/news/",
        "-blog-"
    ]

    def __init__(self, sitemap_address: str):
        self.sitemap_address = sitemap_address

    def start_parsing(self, txt_filename: str):
        sitemap_address = self.sitemap_address
        with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as driver:
            driver.get(sitemap_address)
            pg_source = driver.page_source
            print("Количество символов в тексте страницы составило:")
            print(len(pg_source))
            found_games_htmls = self.find_tag_values(web_page_source=pg_source)
            print(*found_games_htmls, sep='\n')
            self.write_list_to_txt_file(lst=found_games_htmls,
                                        filename=txt_filename)
            input("Для закрытия браузера нажмите Enter!")

    def find_tag_values(self,
                        web_page_source,
                        open_tag: str="<loc>",
                        close_tag: str="</loc>"):
        search_mask = fr"{open_tag}(.*?){close_tag}"
        result = re_findall(search_mask, web_page_source)
        print(f"Before filtering: <{len(result)}> elements in list.")
        result = [html for html in result
                  if all([j not in html for j in self.exclude_marks_web_pages])]
        print(f"After filtering: <{len(result)}> elements in list.")
        return result

    def write_list_to_txt_file(self, lst: list, filename: str):
        if type(filename) != str or not filename.endswith(".txt"):
            print("передали неверный агрумент имени файла!")
            return
        with open(filename, 'w') as f:
            for line in lst:
                f.write(f"{line}\n")


if __name__ == '__main__':
    print(type(json_data))
    print(json_data)
    parser_1 = WebParser(sitemap_address=json_data['sitemap_1'])
    parser_1.start_parsing(txt_filename=json_data['htmls_txt_filename'])
