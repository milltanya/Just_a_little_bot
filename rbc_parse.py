import requests
import config
from bs4 import BeautifulSoup
from time import gmtime, strftime
session = requests.Session()
session.max_redirects = config.MAX_SESSION_NUMBER


def make_soup(url):
    """
    Возвращает код страницы по указанному адресу
    :param url: string
    :return: soup
    """
    return BeautifulSoup(session.get(url).text.encode(),
                         "html.parser")


def string_to_time(time_string):
    """
    Преобразует строку, полученную с сайта, в строку в формате
    "YYYY-MM-DD HH:MM"
    :param time_string: время
    :return: string
    """
    answer = ""
    info = time_string.replace(',', '').split()
    if len(info) == 1:
        answer = strftime("%Y-%m-%d", gmtime()) + " " + info[0]
    elif len(info) == 3:
        answer = strftime("%Y-", gmtime()) + \
                 config.MONTHS[info[1]] + "-" + info[0] + " " + info[2]
    elif len(info) == 4:
        answer = info[2] + "-" + config.MONTHS[info[1]] +\
            "-" + info[0] + " " + info[3]
    return answer


def parse_document(url):
    """
    Возвращает информацию о документе в формате словаря
    :param url: string
    :return: dict
    """
    page = make_soup(url)
    title = page.find('div', {'class': 'article__header__title'}).find(
        'span', {'class': 'js-slide-title'}).text.strip()
    time = string_to_time(
        page.find('span', {'class': 'article__header__date'}).text.strip())
    text = ""
    for par in page.find('div', {'class': 'article__text'}).find_all('p'):
        if par.find('div') is None and par.find('script') is None:
            text += par.text.strip() + '\n'
    tags = {}
    for tag in page.find_all('a', {'class': 'article__tags__link'}):
        tags.update({tag.text.strip().replace('"', ''): tag.get('href')})
    return {'url': url, 'title': title, 'time': time,
            'text': text, 'tags': tags}


def parse_docs_in_topic(url):
    """
    Возвращает список адресов документов в теме по ее адресу
    :param url: string
    :return: list
    """
    page = make_soup(url)
    return list(
        document.find(
            'a', {'class': 'item__link no-injects js-yandex-counter'}
        ).get('href') for document in page.find_all(
            'div', {'class': "item item_story-single js-story-item"}
        )
    )


def parse_topic(url):
    """
    Возвращает информацию о теме по ее адресу
    :param url: string
    :return: dict
    """
    page = make_soup(url)
    title = page.find('div', {'class':
                      'story__title js-story-one-id'}).contents[0].strip()[:-1]
    description = page.find('span', {'class': 'story__text'}).text.strip()
    return {'title': title, 'url': url, 'description': description}
