import sqlite3
conn = sqlite3.connect('rbc.db')
cur = conn.cursor()


def get_news(number):
    news = []
    request = cur.execute('''
        SELECT Title, Url, Time
        FROM Document
        ORDER BY Time
    ''').fetchall()
    for line in request[:number]:
        title, url, time = line
        news.append({'Title': title, 'Url': url, 'Time': time})
    return news


# def upgrade_docs(urls):
#     existing_url = cur.execute('''
#         SELECT Url
#         FROM Document
#     ''').fetchall()
#     for url in urls:
#         if url not in existing_url:
#
#             existing_url.append(document['Url'])
#             cur.execute('''
#                             INSERT INTO Document (Title, last_name, active, profile) VALUES
#                             ("Maxim", "Popov", 1, (SELECT id FROM user_types WHERE name = "Teacher"))
#                         ''')


def main():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document (
            ID_Document INTEGER PRIMARY KEY AUTOINCREMENT,
            Url TEXT NOT NULL UNIQUE,
            Title TEXT NOT NULL,
            Time DATETIME NOT NULL,
            Text TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Document_tag (
            ID_Document INTEGER REFERENCES Document(ID_Document),
            Title TEXT NOT NULL,
            Url TEXT NOT NULL,
            PRIMARY KEY(ID_Document, Title)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Theme (
            ID_Theme INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Url TEXT NOT NULL UNIQUE,
            Description TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Theme_document (
            ID_Theme INTEGER REFERENCES Theme(ID_Theme),
            ID_Document INTEGER REFERENCES Document(ID_Document),
            PRIMARY KEY(ID_Theme, ID_Document)
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()