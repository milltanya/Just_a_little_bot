import requests
from bs4 import BeautifulSoup


def get_main_soup():
    return get_soup('https://www.rbc.ru/story/')


def get_soup(url):
    return BeautifulSoup(requests.get(url).text.encode())
