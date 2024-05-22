from page_parsing import main_func as main_func
from json import load as json_load
# from parser import WebParser


if __name__ == '__main__':
    css_selector_filename = "..\\resources\\bg_parsing_info.json"
    # start_htmls_filename = WebParser.get_last_downloaded_htmls_key()
    names_dict_path = "..\\resources\\names_info.json"
    with open(names_dict_path) as json_file:
        json_data = json_load(json_file)
    start_htmls_filename = json_data["last_downloaded_htmls"]
    with open(start_htmls_filename) as file:
        start_htmls = [line.rstrip() for line in file]
    res_dict_path = "..\\output\\parsed_board_games.json"
    main_func(css_selector_filename,
              start_htmls,
              res_dict_path)
