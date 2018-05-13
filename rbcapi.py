import database
import rbc


def update():
    page = rbc.make_soup('https://www.rbc.ru/story/')
    existing_themes_url = database.get_existing_themes_url()
    existing_docs_url = database.get_existing_docs_url()
    new_themes = []
    new_docs_in_theme = {}
    new_documents = []
    for item in page.find_all('a', {'class': 'item__link no-injects'}):
        theme_url = rbc.simplify_url(item.get('href'))
        if theme_url not in existing_themes_url:
            existing_themes_url.append(theme_url)
            theme = rbc.parse_theme(theme_url)
            new_themes.append(theme)
        docs = rbc.parse_docs_in_theme(theme_url)
        new_docs_in_theme.update({theme_url: docs})
        for doc_url in docs:
            if doc_url not in existing_docs_url:
                existing_docs_url.append(doc_url)
                doc = rbc.parse_article(rbc.simplify_url(doc_url))
                new_documents.append(doc)
    database.update_themes(new_themes)
    database.update_documents(new_documents)
    database.update_docs_in_theme(new_docs_in_theme)


def get_new_docs(number):
    docs = database.get_docs(number)
    answer = ""
    for document in docs:
        answer += document[0] + '\n' + document[1] + '\n\n'
    return answer


def get_new_themes(number):
    themes = database.get_themes(number)
    answer = ""
    for theme in themes:
        answer += theme[0] + '\n' + theme[1] + '\n\n'
    return answer


def get_theme(title):
    theme = database.get_theme_information(title)
    answer = title + '\n' + theme['Description']
    for doc in theme['Documents']:
        answer += '\n\n' + doc[0] + '\n' + doc[1]
    return answer
