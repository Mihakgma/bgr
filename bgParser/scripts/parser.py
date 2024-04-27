# from time import sleep as time_sleep
from selenium import webdriver
# from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService
# from os import getcwd as os_getcwd
# from os import chdir as os_chdir
from json import load as json_load
from json import dump as json_dump
from re import findall as re_findall

from datetime import datetime

# from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
#     ElementNotInteractableException, StaleElementReferenceException
#
# from tqdm.notebook import tqdm


class WebParser:
    """
    __names_dict_path - путь к файлу с наименованиями файлов, путями и проч информацией...
    """
    __names_dict_path = "..\\resources\\names_info.json"
    __last_downloaded_htmls_key = "last_downloaded_htmls"

    def __init__(self, sitemap_address: str, exclude_marks_web_pages: list):
        self.sitemap_address = sitemap_address
        self.exclude_marks_web_pages = exclude_marks_web_pages

    @classmethod
    def get_names_dict_path(cls):
        return cls.__names_dict_path

    @classmethod
    def get_last_downloaded_htmls_key(cls):
        return cls.__last_downloaded_htmls_key

    def start_parsing(self,
                      txt_filename: str,
                      open_tag: str="<loc>",
                      close_tag: str="</loc>"):
        sitemap_address = self.sitemap_address
        with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as driver:
            driver.get(sitemap_address)
            pg_source = driver.page_source
            print("Количество символов в тексте страницы составило:")
            print(len(pg_source))
            found_pages_htmls = self.find_tag_values(web_page_source=pg_source,
                                                     open_tag=open_tag,
                                                     close_tag=close_tag)
            print(*found_pages_htmls, sep='\n')
            self.write_list_to_txt_file(lst=found_pages_htmls,
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
        file_format = ".txt"
        if type(filename) != str or not filename.endswith(file_format):
            raise TypeError("Передан неверный аргумент имени файла!")
        filename_new = "_".join([
            filename.split(file_format)[0],
            self.get_now_timestamp(),
            file_format
        ])
        with open(filename_new, 'w') as f:
            for line in lst:
                f.write(f"{line}\n")
        self.update_info_dict(dict_path=self.get_names_dict_path(),
                              key_ldf=self.get_last_downloaded_htmls_key(),
                              value=filename_new)

    def get_now_timestamp(self, need_underspaces: bool=True):
        if type(need_underspaces) != bool:
            raise TypeError("Передан неверный аргумент!")
        now = datetime.now()

        time = now.strftime("%d:%m:%Y:%H:%M")
        return [time, time.replace(":", "_")][need_underspaces]

    @staticmethod
    def update_info_dict(dict_path,
                         key_ldf,
                         value,
                         append_to_lst=False):
        if type(append_to_lst) != bool:
            raise TypeError("Variable <append_to_lst> need to be bool type!")
        with open(dict_path) as json_file:
            json_data: dict = json_load(json_file)
        if append_to_lst:
            if type(json_data[key_ldf]) != list:
                raise TypeError(f"Value for key <{key_ldf}> is not a list!")
            json_data[key_ldf].append(value)
        else:
            json_data[key_ldf] = value
        with open(dict_path, "w") as jsonFile:
            json_dump(json_data, jsonFile)


if __name__ == '__main__':
    # подгружаем json с данными
    with open(WebParser.get_names_dict_path()) as json_file:
        json_data = json_load(json_file)
    print(type(json_data))
    print(json_data)
    parser_1 = WebParser(sitemap_address=json_data['sitemap'],
                         exclude_marks_web_pages=json_data["exclude_marks_webpages"])
    parser_1.start_parsing(txt_filename=json_data['htmls_txt_filename'])
