import rbc_data
import rbc_parse
import time
import os
import config


def update():
    """
    Обновляет базу данных
    :return:
    """
    page = rbc_parse.make_soup('https://www.rbc.ru/story/')
    existing_topics_url = rbc_data.get_existing_topics_url()
    existing_docs_url = rbc_data.get_existing_docs_url()
    for item in page.find_all('a', {'class': 'item__link no-injects'}):
        topic_url = item.get('href')
        if topic_url not in existing_topics_url:
            existing_topics_url.append(topic_url)
            rbc_data.update_topics(rbc_parse.parse_topic(topic_url))
        docs = rbc_parse.parse_docs_in_topic(topic_url)
        rbc_data.update_docs_in_topic(topic_url, docs)
        for doc_url in docs:
            if doc_url not in existing_docs_url:
                existing_docs_url.append(doc_url)
                rbc_data.update_documents(rbc_parse.parse_document(doc_url))
        rbc_data.update_topic_image(topic_url)


def updating():
    os.makedirs('log', 0o777, True)
    while True:
        update()
        f = open('log/update.txt', 'a')
        f.write(time.strftime("%Y-%m-%d %H:%M", time.gmtime()))
        f.close()
        time.sleep(config.UPDATE_PAUSE*60)


if __name__ == '__main__':
    rbc_data.create_database()
    updating()
