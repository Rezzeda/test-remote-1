import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

reply_keyboard = [['/play', '/settings'],
                  ['/rules', '/close']]

candies = 50
step = 15

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

token = ''


def start(update, context):
    name = f'{update.message.from_user.first_name}'
    update.message.reply_text(
        f"Привет, {name}! Давай поиграем? Выбери команду:\nplay - играть;\nsettings - настроить количество;\nrules - правила;\nclose - закрыть.\n",
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def rules(update, context):
    update.message.reply_text(
        "В начале игры определяем количество конфет на кону и максимальное количество конфет, которое можно взять за раз."
        "По умолчанию всего конфет 50, а максимум за ход можно взять 15")


def settings(update, context):
    update.message.reply_text("Введите через ПРОБЕЛ количество конфет на кону и максимально возможное количество на 1 ход:")


def set_settings(update, context):
    global candies
    global step
    candies, step = map(int, update.message.text.split())
    update.message.reply_text('Правила установлены. Начинаем, нажмите /play', reply_markup=markup)
    return ConversationHandler.END


def play(update, context):
    update.message.reply_text(
        f"На кону {candies} конфет. Ваш ход. Сколько конфет возьмете?(Макс. {step} конфет.)",
        reply_markup=ReplyKeyboardRemove())
    return 1


def stop(update, context):
    update.message.reply_text("Всего хорошего!")
    return ConversationHandler.END


def play_step(update, context):
    global candies
    global step
    candy = int(update.message.text)
    candies -= candy
    if candies <= step:
        update.message.reply_text("Игра окончена. Бот победил!", reply_markup=markup)
        return ConversationHandler.END
    else:
        update.message.reply_text(f"На кону {candies} конфет. Я беру {candies % (step + 1)} конфет.")
        candies -= candies % (step + 1)
        update.message.reply_text(f"Осталось {candies} конфет.")
        if candies <= step:
            update.message.reply_text("Игра окончена. ВЫ победили!", reply_markup=markup)
            return ConversationHandler.END


def main():
    updater = Updater(token)
    dp = updater.dispatcher
    settings_handler = ConversationHandler(
        entry_points=[CommandHandler('settings', settings)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, set_settings)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    play_handler = ConversationHandler(
        entry_points=[CommandHandler('play', play)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, play_step)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("rules", rules))
    dp.add_handler(settings_handler)
    dp.add_handler(play_handler)
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("stop", stop))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
