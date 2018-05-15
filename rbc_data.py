import sqlite3
import re
import collections


def create_database():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            time TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Tag (
            url TEXT NOT NULL,
            title TEXT PRIMARY KEY
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document_tag (
            doc_url TEXT REFERENCES Document(url),
            tag_title TEXT REFERENCES Tag(title)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Topic (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Topic_document (
            topic_url TEXT REFERENCES Topic(url),
            doc_url TEXT REFERENCES Document(url),
            PRIMARY KEY(topic_url, doc_url)
        )
    ''')
    conn.commit()
    conn.close()


def get_existing_topics_url():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT url
        FROM Topic
    ''').fetchall()
    conn.close()
    return existing_url


def get_existing_docs_url():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT url
        FROM Document
    ''').fetchall()
    conn.close()
    return existing_url


def update_docs_in_topic(docs_in_topic):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    for topic in docs_in_topic.keys():
        for doc in docs_in_topic[topic]:
            try:
                cur.execute('''
                    INSERT INTO Topic_document (topic_url, Doc_url)
                    VALUES ("{}", "{}")
                '''.format(topic, doc))
            except sqlite3.IntegrityError:
                pass
    conn.commit()
    conn.close()


def update_topics(topics):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    for topic in topics:
        try:
            cur.execute('''
                INSERT INTO Topic (url, title, description)
                VALUES ("{}", "{}", "{}")
            '''.format(topic['url'], topic['title'], topic['description']))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()


def update_documents(documents):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = get_existing_docs_url()
    for document in documents:
        if document['url'] not in existing_url:
            existing_url.append(document['url'])
            try:
                cur.execute('''
                    INSERT INTO Document (url, title, time, text)
                    VALUES ("{}", "{}", "{}", "{}")
                '''.format(document['url'], document['title'], document['time'], document['text']))
            except sqlite3.IntegrityError:
                pass
            for tag_title in document['tags'].keys():
                try:
                    cur.execute('''
                        INSERT INTO Tag (title, url)
                        VALUES ("{}", "{}")
                    '''.format(tag_title, document['tags'][tag_title]))
                except sqlite3.IntegrityError:
                    pass
                try:
                    cur.execute('''
                        INSERT INTO Document_tag (doc_url, tag_title)
                        VALUES ("{}", "{}")
                    '''.format(document['url'], tag_title))
                except sqlite3.IntegrityError:
                    pass
    conn.commit()
    conn.close()


def new_docs(number):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
        SELECT title, url
        FROM Document
        ORDER BY time DESC
    ''').fetchall()[:number]
    conn.close()
    answer = ""
    for document in docs:
        answer += document[0] + '\n' + document[1] + '\n\n'
    return answer


def new_topics(number):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    topics = cur.execute('''
        SELECT Topic.title, Topic.url
        FROM Topic
        JOIN Topic_document
        ON Topic.url = Topic_document.topic_url
        JOIN Document
        ON Topic_document.doc_url = Document.url
        GROUP BY Topic.url
        ORDER BY MAX(Document.time) DESC
    ''').fetchall()[:number]
    conn.close()
    answer = ""
    for topic in topics:
        answer += topic[0] + '\n' + topic[1] + '\n\n'
    return answer


def topic(title):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    description = cur.execute('''
        SELECT description
        FROM Topic
        WHERE title = "{}"
    '''.format(title)).fetchall()[0][0]
    docs = cur.execute('''
        SELECT Document.title, Document.url
        FROM (SELECT url
        FROM Topic
        WHERE title = "{}") AS A
        JOIN Topic_document
        ON A.url = Topic_document.topic_url
        JOIN Document
        ON Topic_document.doc_url = Document.url
        ORDER BY Document.time DESC
    '''.format(title)).fetchall()[:5]
    conn.close()
    answer = title + '\n' + description
    for doc in docs:
        answer += '\n\n' + doc[0] + '\n' + doc[1]
    return answer


def doc(title):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    text = cur.execute('''
            SELECT text
            FROM Document
            WHERE title = "{}"
        '''.format(title)).fetchall()[0][0]
    conn.close()
    return text


def count_words(text, words, n):
    for word in re.findall(r"\w+", text):
        if len(word) > 1:
            if len(word) > 3:
                words[word[0].upper() + word[1:]] += n
            elif word.isupper():
                words[word] += n


def words(topic_title):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    words = collections.defaultdict(int)
    count_words(topic_title, words, 3)
    docs = cur.execute('''
            SELECT Document.title
            FROM (
                      SELECT url
                      FROM Topic
                      WHERE title = "{}"
                 ) AS A
            JOIN Topic_document
            ON A.url = Topic_document.topic_url
            JOIN Document
            ON Topic_document.doc_url = Document.url
        '''.format(topic_title)).fetchall()
    for doc_title in docs:
        count_words(doc_title[0], words, 2)
    tags = cur.execute('''
            SELECT Document_tag.tag_title
            FROM (
                      SELECT url
                      FROM Topic
                      WHERE title = "{}"
                 ) AS A
            JOIN Topic_document
            ON A.url = Topic_document.topic_url
            JOIN Document
            ON Topic_document.doc_url = Document.url
            JOIN Document_tag
            ON Document.url = Document_tag.doc_url
        '''.format(topic_title)).fetchall()
    for tag_title in tags:
        count_words(tag_title[0], words, 1)
    conn.close()
    best_words = []
    for word in words.keys():
        for b_word in best_words:
            if words[word] > words[b_word]:
                best_words.insert(best_words.index(b_word), word)
                break
        if word not in best_words:
            best_words.append(word)
        best_words = best_words[:5]
    return ('\n'.join(best_words))


def describe_doc(doc_title):
    pass


def describe_topic(topic_title):
    pass
