# -*- coding: utf-8 -*-
import sqlite3
import re
import collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import pandas
import os


def create_database():
    os.makedirs('./images/lengths/docs', 0o777, True)
    os.makedirs('./images/frequences/docs', 0o777, True)
    os.makedirs('./images/lengths/topics', 0o777, True)
    os.makedirs('./images/frequences/topics', 0o777, True)
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


def count_words(text, words, n):
    for word in re.findall(r"\w+", text):
        if len(word) > 1:
            if len(word) > 3:
                words[word[0].upper() + word[1:]] += n
            elif word.isupper():
                words[word] += n


def count_lengths(words, lengths):
    for word in words.keys():
        length = len(word)
        if length >= len(lengths):
            lengths.extend([0] * (length - len(lengths) + 1))
        lengths[length] += words[word]


def describe_text(text, file_name):
    words = collections.defaultdict(int)
    lengths = []
    frequences = [0] * 100
    count_words(text, words, 1)
    count_lengths(words, lengths)
    total = sum(words.values())
    for word in words.keys():
        frequences[int(words[word] * 100 / total)] += words[word]
    matplotlib.rc('font', family='Arial')
    try:
        data_frame = pandas.DataFrame(lengths)
        plot = data_frame.plot(kind='line', title='Длины слов')
        plot.set_xlabel('Длина')
        plot.set_ylabel('Количество слов')
        matplotlib.pyplot.legend('')
        matplotlib.pyplot.savefig('images/lengths/' + file_name + '.png')
        matplotlib.pyplot.close()
    except TypeError:
        print("TypeError")
        print(text)
        print(lengths)
    data_frame = pandas.DataFrame(frequences[:10])
    plot = data_frame.plot(kind='line', title='Частоты слов')
    plot.set_xlabel('Частотв')
    plot.set_ylabel('Количество слов')
    matplotlib.pyplot.legend('')
    matplotlib.pyplot.savefig('images/frequences/' + file_name + '.png')
    matplotlib.pyplot.close()


def update_images():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
        SELECT title, text
        FROM Document
    ''').fetchall()
    for doc in docs:
        describe_text(doc[1], 'docs/' + doc[0])
    topics = cur.execute('''
        SELECT title, url
        FROM Topic
    ''').fetchall()
    for topic in topics:
        docs_text = cur.execute('''
                SELECT Document.text
                FROM (
                    SELECT doc_url
                    FROM Topic_document
                    WHERE topic_url = "{}"
                    ) AS A
                JOIN Document
                ON A.doc_url = Document.url
            '''.format(topic[1])).fetchall()
        text = ''
        for item in docs_text:
            text += item[0]
        describe_text(text, 'topics/' + topic[0])


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
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    answer = None
    if cur.execute('''
        SELECT *
        FROM Document
        WHERE title = "{}"
    '''.format(doc_title)).fetchall() != []:
         answer = ['images/lengths/docs/' + doc_title + '.png', 'images/frequences/docs/' + doc_title + '.png']
    cur.close()
    return answer


def describe_topic(topic_title):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    answer = None
    if cur.execute('''
            SELECT *
            FROM Topic
            WHERE title = "{}"
    '''.format(topic_title)).fetchall() != []:
        docs_text = cur.execute('''
                SELECT Document.text
                FROM (SELECT url
                FROM Topic
                WHERE title = "{}") AS A
                JOIN Topic_document
                ON A.url = Topic_document.topic_url
                JOIN Document
                ON Topic_document.doc_url = Document.url
            '''.format(topic_title)).fetchall()
        docs_count = len(docs_text)
        docs_avg_length = 0
        for text in docs_text:
            docs_avg_length += len(re.findall(r"\w+", text[0]))
        docs_avg_length /= docs_count
        answer = ["Количество документов в теме " + str(docs_count) + '\n\nСредняя длина документа ' + str(int(docs_avg_length)) + ' слова', 'images/lengths/topics/' + topic_title + '.png', 'images/frequences/topics/' + topic_title + '.png']
    conn.close()
    return answer


print(describe_topic("Новое правительство"))
