import soup


def get_news(number):
    page = soup.get_main_soup()
    answer = ""
    for new in page.find('div', {'class': 'news-feed__list'}).find_all('a', {'class': 'news-feed__item chrome js-yandex-counter'})[:number]:
        new_link = new.get('href')
        new_title = new.find('span', {'class': 'news-feed__item__title'}).text.strip()
        answer += new_title + "\n" + new_link + "\n\n"
    return answer
