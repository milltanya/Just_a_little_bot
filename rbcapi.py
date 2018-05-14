import database
import rbc
database.create_database()

def update():
    print('update_1')
    page = rbc.make_soup('https://www.rbc.ru/story/')
    print('update_2')
    existing_themes_url = database.get_existing_themes_url()
    print('update_3')
    existing_docs_url = database.get_existing_docs_url()
    print('update_4')
    new_themes = []
    new_docs_in_theme = {}
    new_documents = []
    for item in page.find_all('a', {'class': 'item__link no-injects'}):
        print('update_5')
        theme_url = rbc.simplify_url(item.get('href'))
        if theme_url not in existing_themes_url:
            print('update_6')
            existing_themes_url.append(theme_url)
            theme = rbc.parse_theme(theme_url)
            new_themes.append(theme)
        print('update_7')
        docs = rbc.parse_docs_in_theme(theme_url)
        new_docs_in_theme.update({theme_url: docs})
        for doc_url in docs:
            print('update_8')
            if doc_url not in existing_docs_url:
                print('update_9')
                existing_docs_url.append(doc_url)
                doc = rbc.parse_article(rbc.simplify_url(doc_url))
                new_documents.append(doc)
    print('update_10')
    database.update_themes(new_themes)
    print('update_11')
    database.update_documents(new_documents)
    print('update_12')
    database.update_docs_in_theme(new_docs_in_theme)
    print('update_13')


def get_new_docs(number):
    print('get_new_docs_1')
    update()
    print('get_new_docs_2')
    docs = database.get_docs(number)
    print('get_new_docs_3')
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
