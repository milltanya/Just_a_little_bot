import sqlite3


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
        CREATE TABLE IF NOT EXISTS Document_tag (
            doc_url TEXT REFERENCES Document(url),
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            PRIMARY KEY(doc_url, title)
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
                        INSERT INTO Document_tag (doc_url, title, url)
                        VALUES ("{}", "{}", "{}")
                    '''.format(document['url'], tag_title, document['tags'][tag_title]))
                except sqlite3.OperationalError:
                    print('''
                        INSERT INTO Document_tag (doc_url, title, url)
                        VALUES ("{}", "{}", "{}")
                    '''.format(document['url'], tag_title, document['tags'][tag_title]))
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
    return docs


def new_topics(number):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
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
    return docs


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
    return {'description': description, 'documents': docs}


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


def words(topic_title):
    pass


def describe_doc(doc_title):
    pass


def describe_topic(topic_title):
    pass


create_database()