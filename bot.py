# -*- coding: utf-8 -*-
import telebot
import rbc_update
import rbc_data
from multiprocessing import Process
token = '570771300:AAGMX2JIFGv-2gglbJZDMj0xN0MFjTjy0Es'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['help', 'start'])
def bot_help(message):
    help_text = 'Привет! Ты используешь бот Just_a_little_bot, который ' \
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
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['update'])
def bot_new_docs(message):
    rbc_update.update()
    args = message.text.split()
    if len(args) == 1:
        bot.send_message(message.chat.id, "База обновлена")


@bot.message_handler(commands=['new_docs'])
def bot_new_docs(message):
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        bot.send_message(message.chat.id, rbc_data.new_docs(int(args[1])))


@bot.message_handler(commands=['new_topics'])
def bot_new_topics(message):
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        bot.send_message(message.chat.id, rbc_data.new_topics(int(args[1])))


@bot.message_handler(commands=['topic'])
def bot_topic(message):
    args = message.text.split()
    if len(args) >= 2:
        bot.send_message(message.chat.id, rbc_data.topic(" ".join(args[1:])))


@bot.message_handler(commands=['doc'])
def bot_topic(message):
    args = message.text.split()
    if len(args) >= 2:
        bot.send_message(message.chat.id, rbc_data.doc(" ".join(args[1:])))


@bot.message_handler(commands=['words'])
def bot_words(message):
    args = message.text.split()
    if len(args) >= 2:
        bot.send_message(message.chat.id, rbc_data.words(" ".join(args[1:])))


@bot.message_handler()
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "kek\n" + message.text)


if __name__ == '__main__':
    rbc_data.create_database()
    rbc_update.update()
    
    class Bot:
        def __call__(self):
            bot.polling(none_stop=True)

    class Update:
        def __call__(self):
            rbc_update.updating()

    process_bot = Process(target=Bot())
    process_update = Process(target=Update())
    process_bot.start()
    process_update.start()
    process_bot.join()
    process_update.join()
