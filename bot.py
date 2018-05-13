# -*- coding: utf-8 -*-
import telebot
import rbc

token = '570771300:AAGMX2JIFGv-2gglbJZDMj0xN0MFjTjy0Es'
bot = telebot.TeleBot(token)


def get_help():
    """
    Функция возвращает справку по боту
    :return: string
    """
    return 'Привет! Ты используешь бот Just_a_little_bot, который ' \
           'позволяет тебе получать самые актуальные новости с rbc.ru.\n' \
           'Вот что умееет бот:\n' \
           '/help - показать все, что может бот\n' \
           '/new_docs <N> - показать N самых свежих новостей\n' \
           '/new_topics <N> - показать N самых свежих тем\n' \
           '/topic <topic_name> - показать описание темы и заголовки ' \
           '5 самых свежих новостей в этой теме\n' \
           '/doc <doc_title> - показать текст документа ' \
           'с заданным заголовком\n' \
           '/words <topic_name> - показать 5 слов, лучше всего ' \
           'характеризующих тему\n' \
           '/describe_doc <doc_title> - вывести статистику по документу ' \
           '(распределение частот слов, распределение длин слов)\n' \
           '/describe_topic <topic_name> - вывести статистику по теме ' \
           '(количество документов в теме, средняя длина документов, ' \
           'распределение частот слов в рамках всей темы, ' \
           'распределение длин слов в рамках всей темы)'



@bot.message_handler(commands=['help', 'start'])
def bot_help(message):
    bot.send_message(message.chat.id, get_help())


@bot.message_handler(commands=['new_docs'])
def bot_new_docs(message):
    args = message.text.split()
    if args[1].isdigit():
        bot.send_message(message.chat.id, rbc.get_news(int(args[1])))


@bot.message_handler(commands=['new_topics'])
def bot_new_topics(message):
    args = message.text.split()
    if args[1].isdigit():
        bot.send_message(message.chat.id, rbc.get_topics(int(args[1])))


@bot.message_handler(commands=['topic'])
def bot_new_topics(message):
    args = message.text.split()
    topic_information = rbc.get_topic_information(" ".join(args[1:]))
    if topic_information is not None:
        bot.send_message(message.chat.id, topic_information)


@bot.message_handler()
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "kek\n" + message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)