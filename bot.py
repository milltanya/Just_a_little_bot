import config
import telebot
import help
import rbc_news
import rbc_topics

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['help', 'start'])
def bot_help(message):
    bot.send_message(message.chat.id, help.get_help())


@bot.message_handler(commands=['new_docs'])
def bot_new_docs(message):
    args = message.text.split()
    if args[0].isdigit():
        bot.send_message(message.chat.id, rbc_news.get_news(int(args[0])))


@bot.message_handler(commands=['new_topics'])
def bot_new_topics(message):
    args = message.text.split()
    if args[0].isdigit():
        bot.send_message(message.chat.id, rbc_topics.get_topics(int(args[0])))


@bot.message_handler(commands=['topic'])
def bot_new_topics(message):
    args = message.text.split()
    topic_information = rbc_topics.get_topic_information(args[0])
    if topic_information is not None:
        bot.send_message(message.chat.id, topic_information)


@bot.message_handler()
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "kek\n" + message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)