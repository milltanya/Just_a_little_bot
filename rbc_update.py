import rbc_data
import rbc_parse
import time


def update():
    page = rbc_parse.make_soup('https://www.rbc.ru/story/')
    existing_topics_url = rbc_data.get_existing_topics_url()
    existing_docs_url = rbc_data.get_existing_docs_url()
    new_topics = []
    new_docs_in_topic = {}
    new_documents = []
    for item in page.find_all('a', {'class': 'item__link no-injects'})[:10]:
        topic_url = rbc_parse.simplify_url(item.get('href'))
        if topic_url not in existing_topics_url:
            existing_topics_url.append(topic_url)
            topic = rbc_parse.parse_topic(topic_url)
            new_topics.append(topic)
        docs = rbc_parse.parse_docs_in_topic(topic_url)
        new_docs_in_topic.update({topic_url: docs})
        for doc_url in docs:
            if doc_url not in existing_docs_url:
                existing_docs_url.append(doc_url)
                doc = rbc_parse.parse_article(rbc_parse.simplify_url(doc_url))
                new_documents.append(doc)
    rbc_data.update_topics(new_topics)
    rbc_data.update_documents(new_documents)
    rbc_data.update_docs_in_topic(new_docs_in_topic)
    rbc_data.update_images()
    print("База обновлена")


def updating():
    while True:
        update()
        time.sleep(1800)


if __name__ == '__main__':
    rbc_data.create_database()
    updating()