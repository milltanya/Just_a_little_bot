import config
import telebot
import help
import rbc_news
import rbc_topics

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['help', 'start'])
def bot_help(message):
    s = help.get_help()
    bot.send_message(message.chat.id, s)
    print(s)


@bot.message_handler(commands=['new_docs'])
def bot_new_docs(message):
    args = message.text.split()
    if args[1].isdigit():
        s = rbc_news.get_news(int(args[1]))
        bot.send_message(message.chat.id, s)
        print(s)


@bot.message_handler(commands=['new_topics'])
def bot_new_topics(message):
    print("new_topics")
    print(message.text)
    args = message.text.split()
    print(args)
    if args[1].isdigit():
        s = rbc_topics.get_topics(int(args[1]))
        bot.send_message(message.chat.id, s)
        print(s)


@bot.message_handler(commands=['topic'])
def bot_new_topics(message):
    args = message.text.split()
    topic_information = rbc_topics.get_topic_information(" ".join(args[1:]))
    if topic_information is not None:
        bot.send_message(message.chat.id, topic_information)


@bot.message_handler()
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "kek\n" + message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
