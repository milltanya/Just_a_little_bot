import sqlite3


def create_database():
    f = open('tmp.txt', 'a')
    f.write('create_database\n')
    f.close()
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document (
            Url TEXT PRIMARY KEY,
            Title TEXT NOT NULL,
            Time TEXT NOT NULL,
            Description TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document_tag (
            Doc_Url TEXT REFERENCES Document(Url),
            Title TEXT NOT NULL,
            Url TEXT NOT NULL,
            PRIMARY KEY(Doc_Url, Title)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Theme (
            Url TEXT PRIMARY KEY,
            Title TEXT NOT NULL,
            Description TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Theme_document (
            Theme_Url TEXT REFERENCES Theme(Url),
            Doc_Url TEXT REFERENCES Document(Url),
            PRIMARY KEY(Theme_Url, Doc_Url)
        )
    ''')
    conn.commit()
    conn.close()


def get_existing_themes_url():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT Url
        FROM Theme
    ''').fetchall()
    conn.close()
    return existing_url


def get_existing_docs_url():
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = cur.execute('''
        SELECT Url
        FROM Document
    ''').fetchall()
    conn.close()
    return existing_url


def update_docs_in_theme(docs_in_theme):
    print(docs_in_theme)
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    for theme in docs_in_theme.keys():
        for doc in docs_in_theme[theme]:
            cur.execute('''
                INSERT INTO Theme_document (Theme_Url, Doc_Url)
                VALUES ({}, {})
            '''.format(theme, doc))
    conn.commit()
    conn.close()


def update_themes(themes):
    print(themes)
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = get_existing_themes_url()
    for theme in themes:
        if theme['Url'] not in existing_url:
            existing_url.append(theme['Url'])
            cur.execute('''
                INSERT INTO Theme (Url, Title, Description)
                VALUES ({}, {}, {})
            '''.format(theme['Url'], theme['Title'], theme['Description']))
    conn.commit()
    conn.close()


def update_documents(documents):
    print(documents)
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    existing_url = get_existing_docs_url()
    for document in documents:
        if document['Url'] not in existing_url:
            existing_url.append(document['Url'])
            cur.execute('''
                INSERT INTO Document (Url, Title, Time, Description)
                VALUES ({}, {}, {}, {})
            '''.format(document['Url'], document['Title'], document['Time'], document['Description']))
            for tag_title in document['Tags'].keys():
                cur.execute('''
                    INSERT INTO Document_tag (Doc_Url, Title, Url)
                    VALUES ({}, {}, {})
                '''.format(document['Url'], tag_title, document['Tags'][tag_title]))
    conn.commit()
    conn.close()


def get_docs(number):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
        SELECT Title, Url
        FROM Document
        ORDER BY Time DESC
    ''').fetchall()[:number]
    conn.close()
    return docs


def get_themes(number):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    docs = cur.execute('''
        SELECT Theme.Title, Theme.Url
        FROM Theme
        JOIN Theme_document
        ON Theme.Url = Theme_document.Theme_Url
        JOIN Document
        ON Theme_document.Doc_Url = Document.Url
        GROUP BY Theme.Url
        ORDER BY MAX(Document.Time) DESC
    ''').fetchall()[:number]
    conn.close()
    return docs


def get_theme_information(title):
    conn = sqlite3.connect('rbc.db')
    cur = conn.cursor()
    description = cur.execute('''
        SELECT Description
        FROM Theme
        WHERE Title = {}
    '''.format(title))[0]
    docs = cur.execute('''
        SELECT Document.Title, Document.Url
        FROM (SELECT Url
        FROM Theme
        WHERE Title = {}) AS A
        JOIN Theme_document
        ON A.Url = Theme_document.Theme_Url
        JOIN Document
        ON Theme_document.Doc_Url = Document.Url
        ORDER BY Document.Time DESC
    '''.format(title))
    conn.close()
    return {'Description': description, 'Documents': docs}


if __name__ == "__main__":
    create_database()