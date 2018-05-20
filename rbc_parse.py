import requests
from bs4 import BeautifulSoup
from time import gmtime, strftime


def make_soup(url):
    """
    Возвращает код страницы по указанному адресу
    :param url: string
    :return: soup
    """
    return BeautifulSoup(requests.get(url).text.encode(),
                         "html.parser")


def month(month_string):
    """
    Возврашает номер месяца по его названию (на русском) в формате строки из
    двух цифр (string)
    :param month_string: название месяца (string)
    :return: string
    """
    if 'янв' in month_string:
        return '01'
    elif 'фев' in month_string:
        return '02'
    elif 'мар' in month_string:
        return '03'
    elif 'апр' in month_string:
        return '04'
    elif 'мая' in month_string:
        return '05'
    elif 'июн' in month_string:
        return '06'
    elif 'июл' in month_string:
        return '07'
    elif 'авг' in month_string:
        return '08'
    elif 'сен' in month_string:
        return '09'
    elif 'окт' in month_string:
        return '10'
    elif 'ноя' in month_string:
        return '11'
    elif 'дек' in month_string:
        return '12'


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
            month(info[1]) + "-" + info[0] + " " + info[2]
    elif len(info) == 4:
        answer = info[2] + "-" + month(info[1]) + "-" + info[0] + " " + info[3]
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

def parse_docs_in_topic(url, last_date):
    """
    Возвращает список адресов документов в теме по ее адресу
    :param url: string
    :return: list
    """
    page = make_soup(url)
    docs = []
    for document in page.find_all('div', {'class': "item item_story-single js-story-item"}):
        doc_time = string_to_time(document.find('span', {'class': 'item__info'}).text.strip())
        if last_date is None or last_date < doc_time:
            docs.append(document.find('a', {'class': 'item__link no-injects js-yandex-counter'}).get('href'))
        else:
            break
    return docs


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
