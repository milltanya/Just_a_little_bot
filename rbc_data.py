# -*- coding: utf-8 -*-
import sqlite3
import re
import collections
import matplotlib
import pandas
import os
matplotlib.use('Agg')
import matplotlib.pyplot


def create_database():
    """
    Создает базу данных и директории, в которых будут храниться изображения
    :return: None
    """
    os.makedirs('data/images/docs', 0o777, True)
    os.makedirs('data/images/topics', 0o777, True)
    conn = sqlite3.connect('data/rbc.db')
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
    """
    Возвращает список адресов тем, которые уже есть в базе
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT url
        FROM Topic
    ''').fetchall()
    conn.close()
    return list(item[0] for item in existing_url)


def get_existing_docs_url():
    """
    Возвращает список адресов документов, которые уже есть в базе
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT url
        FROM Document
    ''').fetchall()
    conn.close()
    return list(item[0] for item in existing_url)


def get_last_document_date():
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    date = cur.execute('''
        SELECT MAX(time)
        FROM Document;
    ''').fetchall()
    conn.close()
    if date != []:
        return date[0][0]
    else:
        return None


def update_docs_in_topic(topic, docs_in_topic):
    """
    Обновляет таблицу Topic_document значениями словаря docs_in_topic
    :param docs_in_topic: словарь, сопоставляющий адресу темы список адресов
    документов (dict)
    :return: None
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    for doc in docs_in_topic:
        cur.execute('''
            INSERT OR IGNORE INTO Topic_document (topic_url, Doc_url)
            VALUES ("{}", "{}")
        '''.format(topic.replace('"', ''), doc.replace('"', '')))
    conn.commit()
    conn.close()


def count_words(text, words, n=1):
    """
    Обновляет words количеством появлений каждого слова в тексте,
    умноженным на n
    :param text: текст (string)
    :param words: словарь слов и частот (collections.defaultdict(int))
    :param n: коэффициент (int, по умолчанию 1)
    :return: None
    """
    for word in re.findall(r"\w+", text):
        words[word[0].upper() + word[1:]] += n


def make_image(data, plot_title, xlabel, ylabel, file_name):
    """
    Делает изображение графика по указанным данным
    :param data: данные  (list)
    :param plot_title: Название графика (string)
    :param xlabel: Название оси абсцисс (string)
    :param ylabel: Название оси ординат (string)
    :param file_name: Название файла(string)
    :return:
    """
    data_frame = pandas.DataFrame(data)
    plot = data_frame.plot(kind='bar', title=plot_title)
    plot.set_xlabel(xlabel)
    plot.set_ylabel(ylabel)
    matplotlib.pyplot.legend('')
    matplotlib.pyplot.savefig('data/images/' + file_name + '.png')
    matplotlib.pyplot.close()


def describe_text(text, file_name):
    """
    Делает графики частот и длин слов в тексте и записывает их в файл с данным
    названием
    :param text: текст (string)
    :param file_name: название файла (string)
    :return: None
    """
    words = collections.defaultdict(int)
    count_words(text, words)
    lengths = []
    for word in words.keys():
        length = len(word)
        if length >= len(lengths):
            lengths.extend([0] * (length - len(lengths) + 1))
        lengths[length] += words[word]
    total = sum(words.values())
    frequences = [0] * 100
    for word in words.keys():
        frequences[int(words[word] * 100 / total)] += words[word]
    make_image(lengths, 'Длины слов', 'Длина',
               'Количество слов', file_name + ' L')
    make_image(frequences[:10], 'Частоты слов', 'Частота',
               'Количество слов', file_name + ' F')


def update_topics(topic):
    """
    Обновляет базу тем значениями из списка словарей
    :param new_topics: list
    :return: None
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO Topic (url, title, description)
        VALUES ("{}", "{}", "{}")
    '''.format(topic['url'].replace('"', ''),
                topic['title'].replace('"', ''),
                topic['description'].replace('"', '')))
    conn.commit()
    conn.close()


def update_topic_image(topic_url):
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    topic_title = cur.execute('''
            SELECT title
            FROM Topic
            WHERE url = "{}"
        '''.format(topic_url)).fetchall()[0][0]
    docs_text = cur.execute('''
                SELECT Document.text
                FROM (
                    SELECT doc_url
                    FROM Topic_document
                    WHERE topic_url = "{}"
                    ) AS A
                JOIN Document
                ON A.doc_url = Document.url
            '''.format(topic_url)).fetchall()
    text = ' '.join([item[0] for item in docs_text])
    describe_text(text, 'topics/' + topic_title)
    conn.close()


def update_documents(document):
    """
    Обновляет базу документов значениями из списка словарей
    :param documents: list
    :return: None
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    describe_text(document['text'], 'docs/' + document['title'])
    cur.execute('''
        INSERT OR IGNORE INTO Document (url, title, time, text)
        VALUES ("{}", "{}", "{}", "{}")
    '''.format(document['url'].replace('"', ''),
                document['title'].replace('"', ''),
                document['time'].replace('"', ''),
                document['text'].replace('"', '')))
    for tag_title in document['tags'].keys():
        cur.execute('''
            INSERT OR IGNORE INTO Tag (title, url)
            VALUES ("{}", "{}")
        '''.format(tag_title.replace('"', ''),
                    document['tags'][tag_title].replace('"', '')))
        cur.execute('''
            INSERT OR IGNORE INTO Document_tag (doc_url, tag_title)
            VALUES ("{}", "{}")
        '''.format(document['url'].replace('"', ''),
                    tag_title.replace('"', '')))
    conn.commit()
    conn.close()


def new_docs(number):
    """
    Возвращает указанное количество документов с самой поздней датой в виде
    списка строк из названия документа и его адреса
    :param number: количество документов (int)
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
        SELECT title, url
        FROM Document
        ORDER BY time DESC
    ''').fetchall()[:number]
    conn.close()
    answer = []
    for document in docs:
        answer.append(document[0] + '\n' + document[1])
    return answer


def new_topics(number):
    """
    Возвращает указанное количество тем с самой поздней датой в виде списка
    строк из названия темы и ее адреса
    :param number: количество тем (int)
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    topics = cur.execute('''
        SELECT DISTINCT Topic.title, Topic.url
        FROM Topic
        JOIN Topic_document
        ON Topic.url = Topic_document.topic_url
        JOIN Document
        ON Topic_document.doc_url = Document.url
        ORDER BY Document.time DESC
    ''').fetchall()[:number]
    conn.close()
    answer = []
    for topic in topics:
        answer.append(topic[0] + '\n' + topic[1])
    return answer


def topic(title):
    """
    Возвращает описание темы и заголовки 5 самых свежих новостей в этой теме
    в виде одной строки
    :param title: название темы (string)
    :return: string
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    description = cur.execute('''
        SELECT description
        FROM Topic
        WHERE title = "{}"
    '''.format(title.replace('"', ''))).fetchall()
    if description == []:
        conn.close()
        return None
    else:
        answer = title + '\n' + description[0][0]
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
        '''.format(title.replace('"', ''))).fetchall()[:5]
        conn.close()
        for doc in docs:
            answer += '\n\n' + doc[0] + '\n' + doc[1]
        return answer


def doc(title):
    """
    Возвращает текст документа с указанным заголовком
    :param title: название документа (string)
    :return: string
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    text = cur.execute('''
        SELECT text
        FROM Document
        WHERE title = "{}"
    '''.format(title.replace('"', ''))).fetchall()
    conn.close()
    if text == []:
        return None
    else:
        return text[0][0]


def words(topic_title):
    """
    Возвращает 5 самых значимых слов в теме. Формула для подсчета значимости
    слова: +3 за упоминание слова в названии темы, +2 за упоминание слова в
    названии документа в теме, +1 за упоминание слова в теге, слова длины 1 не
    учитываются, длины 2-3 - только написанные в верхнем регистре(аббревиатуры)
    :param topic_title: название темы (string)
    :return: string
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    url = cur.execute('''
        SELECT url
        FROM Topic
        WHERE title = "{}"
    '''.format(topic_title.replace('"', ''))).fetchall()
    if url == []:
        return None
    else:
        url = url[0][0]
        docs = cur.execute('''
            SELECT Document.title
            FROM Topic_document
            JOIN Document
            ON Topic_document.doc_url = Document.url
            WHERE Topic_document.topic_url = "{}"
        '''.format(url.replace('"', ''))).fetchall()
        words = collections.defaultdict(int)
        count_words(topic_title, words, 3)
        for doc_title in docs:
            count_words(doc_title[0], words, 2)
        tags = cur.execute('''
                SELECT Document_tag.tag_title
                FROM Topic_document
                JOIN Document
                ON Topic_document.doc_url = Document.url
                JOIN Document_tag
                ON Document.url = Document_tag.doc_url
                WHERE Topic_document.topic_url = "{}"
            '''.format(url.replace('"', ''))).fetchall()
        for tag_title in tags:
            count_words(tag_title[0], words, 1)
        conn.close()
        best_words = []
        for word in words.keys():
            if len(word) > 1 and ((len(word) > 3) or word.isupper()):
                for b_word in best_words:
                    if words[word] > words[b_word]:
                        best_words.insert(best_words.index(b_word), word)
                        break
                if word not in best_words:
                    best_words.append(word)
                best_words = best_words[:5]
        return ('\n'.join(best_words))


def describe_doc(doc_title):
    """
    Возвращает адреса изображений графиков для документа в списке строк
    :param doc_title: название документа (string)
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    answer = None
    if cur.execute('''
        SELECT *
        FROM Document
        WHERE title = "{}"
    '''.format(doc_title.replace('"', ''))).fetchall() != []:
        answer = ['data/images/docs/' + doc_title + ' L.png',
                  'data/images/docs/' + doc_title + ' F.png']
    cur.close()
    return answer


def describe_topic(topic_title):
    """
    Возвращает информацию о теме: количество документов в теме, среднюю длину
    документа и адреса изображений графиков в виде списка строк
    :param topic_title: название темы (string)
    :return: list
    """
    conn = sqlite3.connect('data/rbc.db')
    cur = conn.cursor()
    answer = None
    url = cur.execute('''
            SELECT *
            FROM Topic
            WHERE title = "{}"
    '''.format(topic_title.replace('"', ''))).fetchall()
    if url != []:
        url = url[0][0]
        docs_text = cur.execute('''
                SELECT Document.text
                FROM Topic_document
                JOIN Document
                ON Topic_document.doc_url = Document.url
                WHERE Topic_document.topic_url = "{}"
            '''.format(url.replace('"', ''))).fetchall()
        docs_count = len(docs_text)
        docs_avg_length = 0
        for text in docs_text:
            docs_avg_length += len(re.findall(r"\w+", text[0]))
        docs_avg_length /= docs_count
        answer = ["Количество документов в теме " + str(docs_count) +
                  "\n\nСреднее количество слов в документе " +
                  str(docs_avg_length),
                  'data/images/topics/' + topic_title + ' L.png',
                  'data/images/topics/' + topic_title + ' F.png']
    conn.close()
    return answer
