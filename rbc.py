import requests
from bs4 import BeautifulSoup
from time import gmtime, strftime
session = requests.Session()
session.max_redirects = 100000


def make_soup(url):
    return BeautifulSoup(session.get(url).text.encode(), "html.parser")


def simplify_url(url):
    url = url.replace('htttps://', '')
    index = url.rfind('?from=')
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
    for par in page.find('div', {'class': 'article__text'}).find_all('p')[:10]:
        if par.find('div') is None:
            text += par.text.strip() + '\n'
    tags = {}
    for tag in page.find_all('a', {'class': 'article__tags__link'})[:10]:
        tag_title = tag.text.strip().replace('"', '')
        tag_link = simplify_url(tag.get('href'))
        tags.update({tag_title: tag_link})
    return {'url': url, 'title': title, 'time': time, 'text': text, 'tags': tags}


def parse_docs_in_topic(url):
    page = make_soup(url)
    docs = []
    for document in page.find_all('a', {'class': 'item__link no-injects js-yandex-counter'})[:10]:
        docs.append(simplify_url(document.get('href')))
    return docs


def parse_topic(url):
    page = make_soup(url)
    title = page.find('div', {'class': 'story__title js-story-one-id'}).contents[0].strip()[:-1]
    text = page.find('span', {'class': 'story__text'}).text.strip()
    return {'title': title, 'url': url, 'description' : text}
