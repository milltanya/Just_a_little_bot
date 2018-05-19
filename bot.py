# -*- coding: utf-8 -*-
import telebot
import rbc_data
token = '570771300:AAGMX2JIFGv-2gglbJZDMj0xN0MFjTjy0Es'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['help', 'start'])
def bot_help(message):
    """
    Выводит справку по боту
    :param message: сообщение
    :return: None
    """
    help_text = 'Привет! Ты используешь бот Just_a_little_bot, который ' \
                'позволяет тебе получать самые актуальные новости с rbc.ru.' \
                '\nВот что умееет бот:\n' \
                '/help - показать все, что может бот\n' \
                '/new_docs <N> - показать N самых свежих новостей\n' \
                '/new_topics <N> - показать N самых свежих тем\n' \
                '/topic <topic_name> - показать описание темы и заголовки ' \
                '5 самых свежих новостей в этой теме\n' \
                '/doc <doc_title> - показать текст документа ' \
                'с заданным заголовком\n' \
                '/words <topic_name> - показать 5 слов, лучше всего ' \
                'характеризующих тему\n' \
                '/describe_doc <doc_title> - вывести статистику по документу' \
                ' (распределение частот слов, распределение длин слов)\n' \
                '/describe_topic <topic_name> - вывести статистику по теме ' \
                '(количество документов в теме, средняя длина документов, ' \
                'распределение частот слов в рамках всей темы, ' \
                'распределение длин слов в рамках всей темы)'
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['new_docs'])
def bot_new_docs(message):
    """
    Выводит N последних документов
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        if 0 < int(args[1]):
            for doc in rbc_data.new_docs(int(args[1])):
                bot.send_message(message.chat.id, doc)
        else:
            bot.send_message(message.chat.id, "Число должно быть больше нуля")
    else:
        bot.send_message(message.chat.id, "Введите одно число")


@bot.message_handler(commands=['new_topics'])
def bot_new_topics(message):
    """
    Выводит N последних тем
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        if 0 < int(args[1]):
            for topic in rbc_data.new_topics(int(args[1])):
                bot.send_message(message.chat.id, topic)
        else:
            bot.send_message(message.chat.id, "Число должно быть больше нуля")
    else:
        bot.send_message(message.chat.id, "Введите одно число")


@bot.message_handler(commands=['topic'])
def bot_topic(message):
    """
    Выводин информацию о теме
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) >= 2:
        answer = rbc_data.topic(" ".join(args[1:]))
        if answer is not None:
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, "Тема не найдена")
    else:
        bot.send_message(message.chat.id, "Введите название темы")


@bot.message_handler(commands=['doc'])
def bot_doc(message):
    """
    Выводит информацию о документе
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) >= 2:
        answer = rbc_data.doc(" ".join(args[1:]))
        if answer is not None:
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, "Документ не найден")
    else:
        bot.send_message(message.chat.id, "Введите название документа")


@bot.message_handler(commands=['words'])
def bot_words(message):
    """
    Выводит пять самых значимых слов для темы
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) >= 2:
        answer = rbc_data.words(" ".join(args[1:]))
        if answer is not None:
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, "Тема не найдена")
    else:
        bot.send_message(message.chat.id, "Введите название темы")


@bot.message_handler(commands=['describe_doc'])
def bot_describe_doc(message):
    """
    Отправляет изображения графиков для документа
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) >= 2:
        answer = rbc_data.describe_doc(" ".join(args[1:]))
        if answer is not None:
            with open(answer[0], 'rb') as image1:
                bot.send_photo(message.chat.id, image1)
            with open(answer[1], 'rb') as image2:
                bot.send_photo(message.chat.id, image2)
        else:
            bot.send_message(message.chat.id, "Документ не найден")
    else:
        bot.send_message(message.chat.id, "Введите название документа")


@bot.message_handler(commands=['describe_topic'])
def bot_describe_topic(message):
    """
    Выводит колисечтво документов в теме, среднюю длину документа и
    отправляет изображения графиков для темы
    :param message: сообщение
    :return: None
    """
    args = message.text.split()
    if len(args) >= 2:
        answer = rbc_data.describe_topic(" ".join(args[1:]))
        if answer is not None:
            bot.send_message(message.chat.id, answer[0])
            with open(answer[1], 'rb') as image1:
                bot.send_photo(message.chat.id, image1)
            with open(answer[2], 'rb') as image2:
                bot.send_photo(message.chat.id, image2)
        else:
            bot.send_message(message.chat.id, "Тема не найдена")
    else:
        bot.send_message(message.chat.id, "Введите название темы")


@bot.message_handler()
def bot_wrong_commands(message):
    """
    Отвечает на неправильные команды
    :param message: сообщение
    :return: None
    """
    bot.send_message(message.chat.id, "Введите правильную команду")


if __name__ == '__main__':
    bot.polling(none_stop=True)
