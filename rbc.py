import requests
from bs4 import BeautifulSoup
from time import gmtime, strftime


def make_soup(url):
    return BeautifulSoup(requests.get(url).text.encode(), "html.parser")


def simplify_url(url):
    index = url.rfind('?')
    if index > 0:
        url = url[:index]
    return url


def month(month_string):
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
    answer = ""
    info = time_string.replace(',', '').split()
    if len(info) == 1:
        answer = strftime("%Y%m%d", gmtime()) + info[0].replace(':', '')
    elif len(info) == 3:
        answer = strftime("%Y", gmtime()) + month(info[1]) + info[0] + info[2].replace(':', '')
    elif len(info) == 4:
        answer = info[2] + month(info[1]) + info[0] + info[3].replace(':', '')
    return answer


def parse_article(url):
    page = make_soup(url)
    title = page.find('div', {'class': 'article__header__title'}).find('span', {'class': 'js-slide-title'}).text.strip()
    time = string_to_time(page.find('span', {'class': 'article__header__date'}).text.strip())
    text = ""
    paragraphs = page.find('div', {'class': 'article__text'}).find_all('p')
    for par in paragraphs:
        if par.find('div') is None:
            text += par.text.strip() + '\n'
    tags = {}
    for tag in page.find_all('a', {'class': 'article__tags__link'}):
        tag_title = tag.text.strip()
        tag_link = tag.get('href')
        tags.update({tag_title: tag_link})
    return {'Url': url, 'Title': title, 'Time' : time, 'Text': text, 'Tags': tags}


def parse_docs_in_theme(url):
    page = make_soup(url)
    docs = []
    for document in page.find_all('a', {'class': 'item__link no-injects js-yandex-counter'}):
        docs.append(document.get('href'))
    return docs


def parse_theme(url):
    page = make_soup(url)
    title = page.find('div', {'class': 'story__title js-story-one-id'}).contents[0].strip()[:-1]
    print(title)
    text = page.find('span', {'class': 'story__text'}).text.strip()
    print(text)
    return {'Title': title, 'Url': url, 'Description' : text}
