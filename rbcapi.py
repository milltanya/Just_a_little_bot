import database
import rbc

def update():
    f = open('tmp.txt', 'a')
    f.write('update_1\n')
    f.close()
    page = rbc.make_soup('https://www.rbc.ru/story/')
    f = open('tmp.txt', 'a')
    f.write('update_2\n')
    f.close()
    existing_themes_url = database.get_existing_themes_url()
    f = open('tmp.txt', 'a')
    f.write('update_3\n')
    f.close()
    existing_docs_url = database.get_existing_docs_url()
    f = open('tmp.txt', 'a')
    f.write('update_4\n')
    f.close()
    new_themes = []
    new_docs_in_theme = {}
    new_documents = []
    for item in page.find_all('a', {'class': 'item__link no-injects'})[:10]:
        f = open('tmp.txt', 'a')
        f.write('update_5\n')
        f.close()
        theme_url = rbc.simplify_url(item.get('href'))
        if theme_url not in existing_themes_url:
            f = open('tmp.txt', 'a')
            f.write('update_6\n')
            f.close()
            existing_themes_url.append(theme_url)
            theme = rbc.parse_theme(theme_url)
            new_themes.append(theme)
        f = open('tmp.txt', 'a')
        f.write('update_7\n')
        f.close()
        docs = rbc.parse_docs_in_theme(theme_url)
        new_docs_in_theme.update({theme_url: docs})
        for doc_url in docs:
            f = open('tmp.txt', 'a')
            f.write('update_8\n')
            f.close()
            if doc_url not in existing_docs_url:
                f = open('tmp.txt', 'a')
                f.write('update_9\n')
                f.close()
                existing_docs_url.append(doc_url)
                f = open('tmp.txt', 'a')
                f.write('update_9.1\n')
                f.close()
                doc = rbc.parse_article(rbc.simplify_url(doc_url))
                f = open('tmp.txt', 'a')
                f.write('update_9.2\n')
                f.close()
                new_documents.append(doc)
                f = open('tmp.txt', 'a')
                f.write('update_9.3\n')
                f.close()
    f = open('tmp.txt', 'a')
    f.write('update_10\n')
    f.write(new_themes)
    f.close()
    database.update_themes(new_themes)
    f = open('tmp.txt', 'a')
    f.write('update_11\n')
    f.close()
    database.update_documents(new_documents)
    f = open('tmp.txt', 'a')
    f.write('update_12\n')
    f.close()
    database.update_docs_in_theme(new_docs_in_theme)
    f = open('tmp.txt', 'a')
    f.write('update_13\n')
    f.close()


def get_new_docs(number):
    f = open('tmp.txt', 'a')
    f.write('get_new_docs_1\n')
    f.close()
    update()
    f = open('tmp.txt', 'a')
    f.write('get_new_docs_2\n')
    f.close()
    docs = database.get_docs(number)
    f = open('tmp.txt', 'a')
    f.write('get_new_docs_3\n')
    f.close()
    answer = ""
    for document in docs:
        answer += document[0] + '\n' + document[1] + '\n\n'
    return answer


def get_new_themes(number):
    update()
    themes = database.get_themes(number)
    answer = ""
    for theme in themes:
        answer += theme[0] + '\n' + theme[1] + '\n\n'
    return answer


def get_theme(title):
    update()
    theme = database.get_theme_information(title)
    answer = title + '\n' + theme['Description']
    for doc in theme['Documents']:
        answer += '\n\n' + doc[0] + '\n' + doc[1]
    return answer
