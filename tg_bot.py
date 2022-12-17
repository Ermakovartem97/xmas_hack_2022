import telebot
from telebot import types
from json import loads

from Take_all_stonck import insert_data_persons, take_user_portfolio
from model import get_portfolio_new

token = ''
bot = telebot.TeleBot(token)
competition_name = ''
tmp_user = []
user_data = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    is_create_profile = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton("Составить профиль", callback_data='{"st":"cp"}')
    button2 = types.InlineKeyboardButton('Настроить самому', callback_data='{"st":"ncp"}')
    is_create_profile.add(button1, button2)
    bot.send_message(message.chat.id,
                     'Привет, это бот для персонализированного подбора потфеля. Прошу ответить на несколько вопросов для составления вашего личного профиля инвестора.',
                     reply_markup=is_create_profile)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     'Привет, это бот для составления оптимального портфеля. Все возможные команды можно просмотреть написав /')


@bot.message_handler(commands=['lk'])
def lk(message):
    lk_menu = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("Мой портфель", callback_data='{"st":"mp"}')
    button2 = types.InlineKeyboardButton('Сгенерировать новый портфель', callback_data='{"st":"pp"}')
    button3 = types.InlineKeyboardButton('Настроить портфель', callback_data='{"st":"ps"}')
    lk_menu.add(button1, button3)
    lk_menu.add(button2)
    bot.send_message(message.chat.id, f'Добро пожаловать в личный кабинет', reply_markup=lk_menu)


@bot.callback_query_handler(func=lambda call: loads(call.data)['st'] in ('cp', 'cp1', 'cp2'))
def callback_inline(call):
    try:
        data = loads(call.data)
        if data['st'] == "cp":

            choose_risk = types.InlineKeyboardMarkup(row_width=3)
            button1 = types.InlineKeyboardButton("Минимальный", callback_data='{"st":"cp1","a":"1"}')
            button2 = types.InlineKeyboardButton('Средний', callback_data='{"st":"cp1","a":"2"}')
            button3 = types.InlineKeyboardButton('Высокий', callback_data='{"st":"cp1","a":"3"}')
            choose_risk.add(button1, button2, button3)
            bot.send_message(call.message.chat.id,
                             'Прошу ответить на несколько вопросов.\nКакой уровень риска подходит вам?',
                             reply_markup=choose_risk)

        if data['st'] == "cp1":
            user_data.append(data['a'])
            choose_risk = types.InlineKeyboardMarkup(row_width=3)
            button1 = types.InlineKeyboardButton("3 месяца", callback_data='{"st":"cp2","a":"3"}')
            button2 = types.InlineKeyboardButton('6 месяцев', callback_data='{"st":"cp2","a":"6"}')
            button3 = types.InlineKeyboardButton('12 месяцев', callback_data='{"st":"cp2","a":"12"}')
            choose_risk.add(button1, button2, button3)
            bot.send_message(call.message.chat.id,
                             'Какой горизонт планирования вас устроит?',
                             reply_markup=choose_risk)

        if data['st'] == "cp2":
            user_data.append(data['a'])
            bot.send_message(call.message.chat.id,
                             'Какое количество средств вы планируете вложить?')

            @bot.message_handler(content_types='text')
            def take_sum(message):
                user_data.append(message.text)
                bot.send_message(call.message.chat.id,
                                 "Ваши данные сохранены для составления портфеля\nЧтобы зайти в личный кабинет набирите команду /lk")
                global tmp_user
                tmp_user = user_data[-3:]


    except Exception as e:
        print(repr(e))

@bot.callback_query_handler(func=lambda call: loads(call.data)['st'] in ('mp'))
def get_portfolio(call):
    portfolio = take_user_portfolio(call.message.from_user.id).tail(1)
    if portfolio.shape[0] > 0:
        bot.send_message(call.message.chat.id, f'Ваш портфель:\n{str(portfolio.iloc[0,0])}')
    else:
        bot.send_message(call.message.chat.id, 'Создайте новый портфель в личном кабинете')

@bot.callback_query_handler(func=lambda call: loads(call.data)['st'] in ('pp'))
def create_portfolio(call):
    bot.send_message(call.message.chat.id, 'Начался подбор портфеля, ожидайте')
    global tmp_user
    print(len(tmp_user))
    if len(tmp_user) < 3:
        tmp_user = [2, 2, 100000]
    portfolio = get_portfolio_new(tmp_user)
    bot.send_message(call.message.chat.id, 'Формирование портфеля закончено, вы можете посмотреть его в личном кабинете')
    insert_data_persons([(str(call.message.from_user.id), str(portfolio)),])

@bot.callback_query_handler(func=lambda call: loads(call.data)['st'] in ('ps'))
def create_portfolio(call):
    bot.send_message(call.message.chat.id, 'Данный функционал находится в разработке')

@bot.callback_query_handler(func=lambda call: loads(call.data)['st'] in ('ncp'))
def create_portfolio(call):
    bot.send_message(call.message.chat.id, 'Настройте свой профиль в личном кабинете /lk')

bot.infinity_polling()
