import database
import rbc


def update():
    page = rbc.make_soup('https://www.rbc.ru/story/')
    existing_topics_url = database.get_existing_topics_url()
    existing_docs_url = database.get_existing_docs_url()
    new_topics = []
    new_docs_in_topic = {}
    new_documents = []
    for item in page.find_all('a', {'class': 'item__link no-injects'})[:10]:
        topic_url = rbc.simplify_url(item.get('href'))
        if topic_url not in existing_topics_url:
            existing_topics_url.append(topic_url)
            topic = rbc.parse_topic(topic_url)
            new_topics.append(topic)
        docs = rbc.parse_docs_in_topic(topic_url)
        new_docs_in_topic.update({topic_url: docs})
        for doc_url in docs:
            if doc_url not in existing_docs_url:
                existing_docs_url.append(doc_url)
                doc = rbc.parse_article(rbc.simplify_url(doc_url))
                new_documents.append(doc)
    database.update_topics(new_topics)
    database.update_documents(new_documents)
    database.update_docs_in_topic(new_docs_in_topic)


def new_docs(number):
    docs = database.new_docs(number)
    answer = ""
    for document in docs:
        answer += document[0] + '\n' + document[1] + '\n\n'
    return answer


def new_topics(number):
    topics = database.new_topics(number)
    answer = ""
    for topic in topics:
        answer += topic[0] + '\n' + topic[1] + '\n\n'
    return answer


def topic(title):
    topic = database.topic(title)
    answer = title + '\n' + topic['description']
    for doc in topic['documents']:
        answer += '\n\n' + doc[0] + '\n' + doc[1]
    return answer


def doc(title):
    return database.doc(title)
