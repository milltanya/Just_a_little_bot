import soup


def get_topic_list(page):
    return page.find('div', {'class': 'l-row js-load-container'}).find_all('div', {'class': 'item item_story js-story-item'})


def get_item_title(item):
    return item.find('span', {'class': 'item__title'}).text.strip()


def get_item_link(item):
    return item.find('a').get('href')


def get_topic_description(topic):
    return topic.find('span', {'class': 'item__text'}).text.strip()


def get_topics(number):
    answer = ""
    for topic in get_topic_list(soup.get_main_soup())[:number]:
        topic_link = get_item_link(topic)
        topic_title = get_item_title(topic)
        answer += topic_title + "\n" + topic_link + "\n\n"
    return answer


def get_docs(topic_link):
    return soup.get_soup(topic_link).find_all('div', {'class': 'item item_story-single js-story-item'})


def get_doc_paragraphs(doc_page):
    return doc_page.find('div', {'class': 'article__text'}).find_all('p')


def get_doc_text(doc_title):
    for topic in get_topic_list(soup.get_main_soup()):
        topic_link = get_item_link(topic)
        documents = get_docs(topic_link)
        for doc in documents:
            title = get_item_title(doc)
            if title == doc_title:
                break
        if title == doc_title:
            break
    if title == doc_title:
        doc_paragraphs = get_doc_paragraphs(soup.get_soup(get_item_link(doc)))
        answer = doc_title
        for paragraph in doc_paragraphs:
            answer += '\n' + paragraph.text.strip()
        return answer
    else:
        return None


def get_topic_information(topic_title):
    for topic in get_topic_list(soup.get_main_soup()):
        title = get_item_title(topic)
        if title == topic_title:
            break
    if title == topic_title:
        answer = topic_title
        topic_link = get_item_link(topic)
        topic_description = get_topic_description(topic)
        answer += "\n" + topic_description + "\n"
        documents = get_docs(topic_link)
        for doc in documents[:5]:
            doc_title = get_item_title(doc)
            doc_link = get_item_link(doc)
            answer += "\n" + doc_title + "\n" + doc_link + "\n"
        return answer
    else:
        return None
