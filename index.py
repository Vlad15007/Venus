import telebot
from telebot import types
import sqlite3
import datetime


try:
    API_TOKEN=''
    GROUP_ID=0
except:
    print('Файл с настройками не найден или некорректен')


VALUTE = 'грн'# Сюда валюта


bot = telebot.TeleBot(API_TOKEN)

DATABASE_NAME = 'food_data_base.db'
sql_con = sqlite3.connect(DATABASE_NAME)
sql_cur = sql_con.cursor()
SQL = {'con': sql_con, 'cur': sql_cur}

distribution_message = 'Текст рассылки'


FOOD_MENU_TEXT = 'Меню'
CART_TEXT = '🛒Корзина'
PLUS_TEXT = '➕'
MINUS_TEXT = '➖'
BACK_TEXT = '◀Назад'
CONFIRM_TEXT = '✅Подтвердить'
CANCEL_TEXT = '❌Отмена'
CONTACTS_TEXT = '☎️Контакты'
WRITE_US_TEXT = '✉️Написать нам'
ADD_TO_CART_TEXT = '🛒Добавить в корзину'
BACK_TO_CART_TEXT = '🛒Вернуть в корзину'
ORDER_TEXT = '✅Перейти к заказу'
PLACE_ORDER_TEXT = '✅Оформить заказ'
GALOCHKA_TEXT = '✅'
ADMIN_TEXT = '/admin'
SUBSCRIBE_TEXT = 'Подписка'


def new_sql():
    global DATABASE_NAME
    sql_con = sqlite3.connect(DATABASE_NAME)
    sql_cur = sql_con.cursor()
    SQL = {'con': sql_con, 'cur': sql_cur}
    return SQL


def get_inline_search_users():
    return list(map(lambda s: s[0],
                    new_sql()['cur'].execute('''SELECT user_id FROM Inline_users''').fetchall()))


def get_inline_search_category(user_id):
    category = new_sql()['cur'].execute('''SELECT category FROM Inline_users
        WHERE user_id = ?''', (user_id,)).fetchone()
    if category:
        return category[0]
    else:
        return False


def get_admin_ids():
    return list(map(lambda s: s[0],
                    new_sql()['cur'].execute('''SELECT user_id FROM Admin_list''').fetchall()))


def get_edit_admin_ids():
    return list(map(lambda s: s[0],
                    new_sql()['cur'].execute('''SELECT admin_id FROM Edit_dish''').fetchall()))


def back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_back = types.KeyboardButton(BACK_TEXT)
    keyboard.add(button_back)

    return keyboard


def confirm_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    button_yes = types.KeyboardButton(CONFIRM_TEXT)
    button_no = types.KeyboardButton(CANCEL_TEXT)

    keyboard.row(button_yes, button_no)

    return keyboard


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel_button = types.KeyboardButton(CANCEL_TEXT)
    keyboard.add(cancel_button)

    return keyboard


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message)
    text = message.text
    user_id = message.from_user.id
    if text == '/start':
        send_greeting_msg(user_id)
        send_main_menu(user_id)
    elif text == '/admin':
        send_admin_menu(user_id)
    else:
        send_greeting_msg(user_id)
        send_main_menu(user_id)


def send_greeting_msg(user_id):
    bot.send_message(user_id, 'Добро пожаловать')
    bot.send_message(user_id, 'Это бот')
    sql = new_sql()
    users = sql['cur'].execute('''SELECT id FROM Users''').fetchall()
    print(users)
    if (user_id,) not in users:
        sql['cur'].execute('''INSERT INTO Users(id, distribution, reg_date) VALUES(?, 1, ?)''',
                           (user_id, datetime.date.today()))
        sql['con'].commit()


def send_main_menu(user_id, handler=True, food_menu_hand=True, contacts_food_menu=True, subsc_food_menu=True, write_us_food_menu=True):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    key_food_menu = types.KeyboardButton(FOOD_MENU_TEXT)
    key_text_us = types.KeyboardButton(WRITE_US_TEXT)
    key_conacts = types.KeyboardButton(CONTACTS_TEXT)

    keyboard.row(key_food_menu, key_conacts, types.KeyboardButton(SUBSCRIBE_TEXT), key_text_us,)

    message = bot.send_message(user_id, text='Главное меню', reply_markup=keyboard)
    if handler:
        print('send_main_menu')
        print(food_menu_hand, contacts_food_menu, subsc_food_menu, write_us_food_menu)
        bot.register_next_step_handler(message, lambda m: main_menu_handler(m, food_menu_hand, contacts_food_menu, subsc_food_menu, write_us_food_menu))


def main_menu_handler(message, food_menu_hand=True, contacts_food_menu_hand=True, subsc_food_menu_hand=True, write_us_food_menu_hand=True):
    #try:
        text = message.text
        user_id = message.from_user.id
        send_us_admins = get_send_us_admins()
        if message.reply_to_message:
            if (user_id,) in send_us_admins:
                msg_text = message.reply_to_message.text
                msg_user_id = int(msg_text.split('\n')[-1].split('ID: ')[-1])
                bot.send_message(msg_user_id, 'Вам пришел ответ от админа:\n' + text)
                bot.register_next_step_handler(message, main_menu_handler)
        else:
            print('main_menu_handler')
            print(food_menu_hand, contacts_food_menu_hand, subsc_food_menu_hand, write_us_food_menu_hand)
            if text == FOOD_MENU_TEXT and food_menu_hand:
                send_food_menu(user_id)
            elif text == CONTACTS_TEXT:
                send_contacts(user_id, contacts_food_menu_hand)
            elif text == WRITE_US_TEXT:
                send_write_us(user_id, write_us_food_menu_hand)
            elif text == ADMIN_TEXT:
                send_admin_menu(user_id)
            elif text == SUBSCRIBE_TEXT:
                send_subscribe_text(user_id, subsc_food_menu_hand)

    #except:
    #    bot.send_message(message.from_user.id, 'Неверный формат')
    #    send_main_menu(message.from_user.id)


def send_subscribe_text(user_id, subsc_food_menu_hand=True):
    try:
        keyboard = types.InlineKeyboardMarkup()

        button_yes = types.InlineKeyboardButton(text='Да',
                                                callback_data='distribution][on][' + str(user_id))
        button_no = types.InlineKeyboardButton(text='Нет',
                                               callback_data='distribution][off][' + str(user_id))

        keyboard.row(button_yes, button_no)

        bot.send_message(user_id, text='Хотите быть подписанным на рассылку?', reply_markup=keyboard)

        send_main_menu(user_id, True, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand)
    except:
        return False


def send_write_us(user_id, subsc_food_menu_hand=True):
    message = bot.send_message(user_id, 'Отправьте сообщение для отправки админу', reply_markup=cancel_keyboard())
    bot.register_next_step_handler(message, lambda s: send_write_handler(s, subsc_food_menu_hand))


def send_write_handler(message, subsc_food_menu_hand=True):
    try:
        text = message.text
        admins = get_send_us_admins()
        if text == CANCEL_TEXT:
            send_main_menu(message.from_user.id, True, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand)
        else:
            for i in admins:
                bot.send_message(i[0], 'Вам пришло сообщение от пользователя:\n' + text + '\nLogin: ' + str(
                    '@' + message.from_user.username) + '\nID: ' + str(message.from_user.id))
            bot.send_message(message.from_user.id, 'Сообщение админу отправлено')
            send_main_menu(message.from_user.id, True, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand, subsc_food_menu_hand)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        send_main_menu(message.from_user.id)


def get_send_us_admins():
    return new_sql()['cur'].execute('''SELECT * FROM Send_us_admins''').fetchall()


@bot.inline_handler(lambda query: True)
def query_edit(inline_query):
    try:
        user_id = inline_query.from_user.id
        request = inline_query.query
        result_lst = []
        if request[:8] == 'category':
            category = int(request.split('-')[1].split()[0])
            print(request)
            print(category)

            if len(request.split()) >= 2:
                search_request = ' '.join(request.split()[1:])
                dishes = new_sql()['cur'].execute("""SELECT * FROM Dish
                                        WHERE category = ? AND name like '%{}%'""".format(
                    search_request), (category,)).fetchall()
            else:
                dishes = new_sql()['cur'].execute('''SELECT * FROM Dish
                        WHERE category = ?''', (category,)).fetchall()

            l = 0

            for dish in dishes:
                print(dish)
                l += 1
                food_id = dish[0]
                title = dish[1]
                description = dish[4]
                image_path = dish[2]
                weight = dish[5]
                cost = dish[6]

                keyboard = types.InlineKeyboardMarkup()
                s = types.InlineKeyboardButton(text='sad', callback_data='null')
                keyboard.add(s)

                if user_id in get_edit_admin_ids():
                    s = types.InlineQueryResultCachedPhoto(id=str(l), title=title,
                                                           description=food_id,
                                                           caption=food_id,
                                                           photo_file_id=image_path,
                                                           parse_mode='')
                else:
                    print(get_food_text(food_id))
                    print(get_food_text(food_id,1))
                    s = types.InlineQueryResultArticle(
                                           id=str(l),
                                           title=title,
                                           description=get_food_text(food_id,1),
                                           input_message_content=types.InputTextMessageContent(
                                           message_text='<a href="'+image_path+'">&#8204;</a>'+get_food_text(food_id),
                                           parse_mode='HTML',
                                           ),
                                           reply_markup=food_menu_inline_keyboard(
                                                               user_id,
                                                               food_id),
                                           thumb_url=image_path
                                           )
                    # s = types.InlineQueryResultCachedPhoto(id=str(l), title=title,
                    #                                        description=get_food_text(food_id),
                    #                                        caption=get_food_text(food_id),
                    #                                        photo_file_id=image_path,
                    #                                        reply_markup=food_menu_inline_keyboard(
                    #                                            user_id,
                    #                                            food_id))

                result_lst.append(s)

        bot.answer_inline_query(inline_query.id, result_lst)

    except Exception as e:
        print(e)


def get_food_info_sql(food_id):
    try:
        food_sql = new_sql()['cur'].execute('''SELECT * FROM Dish
            WHERE id = ?''', (food_id,)).fetchone()
        food_dict = dict()
        food_dict['id'] = food_sql[0]
        food_dict['name'] = food_sql[1]
        food_dict['image_id'] = food_sql[2]
        food_dict['category'] = food_sql[3]
        food_dict['description'] = food_sql[4]
        food_dict['weight'] = food_sql[5]
        food_dict['price'] = food_sql[6]
        if food_dict:
            return food_dict
        else:
            return False
    except:
        return False


def send_food_category(user_id):
    try:
        keyboard = types.InlineKeyboardMarkup()

        categories = new_sql()['cur'].execute('''SELECT * FROM Categories''').fetchall()
        row = []
        if len(categories) == 1:
            for category in categories:
                row.append(types.InlineKeyboardButton(text=category[1],
                                                      switch_inline_query_current_chat=(
                                                              'category-' + str(category[0]) + ' ')))
                keyboard.row(*row)
        else:
            for category in categories:
                row.append(types.InlineKeyboardButton(text=category[1],
                                                      switch_inline_query_current_chat=(
                                                              'category-' + str(category[0]) + ' ')))
                if len(row) == 2:
                    keyboard.row(*row)
                    row = []

        message = bot.send_message(user_id, text='Категории:', reply_markup=keyboard)
        return message
    except Exception as e:
        print('send_food_category ERROR')
        print(e)
        return False


def food_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    cart_button = types.KeyboardButton(CART_TEXT)
    back_button = types.KeyboardButton(BACK_TEXT)
    food_menu_button = types.KeyboardButton(FOOD_MENU_TEXT)

    keyboard.row(back_button, food_menu_button, cart_button)

    return keyboard


def send_food_menu(user_id, handler=True):
    try:
        bot.send_message(user_id,
                         'Для выбора нажмите на нужную категорию и в появившейся внизу форме выбирите товар',
                         reply_markup=food_menu_keyboard())
        message = send_food_category(user_id)
        if handler:
            bot.register_next_step_handler(message, food_menu_handler)
    except:
        print('send_food_menu ERROR')
        return False


def food_menu_handler(message):
    try:
        text = message.text
        user_id = message.from_user.id
        if text == BACK_TEXT:
            send_main_menu(user_id)
        elif text == CART_TEXT:
            send_user_cart(user_id)
        elif text == FOOD_MENU_TEXT:
            send_food_menu(user_id)
        else:
            bot.register_next_step_handler(message, food_menu_handler)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        send_food_menu(message, False)


def get_user_cart(user_id):
    try:
        cart = new_sql()['cur'].execute('''SELECT food_id, count FROM Cart
            WHERE user_id = ?''', (user_id,)).fetchall()
        cart_dict = dict()
        for i in cart:
            cart_dict[i[0]] = i[1]

        return cart_dict
    except:
        return False


def get_food_text(food_id,typesep=0):
    try:
        print(food_id)
        food_info = get_food_info_sql(food_id)
        print(food_info)
        text = ''
        if typesep == 1:
            text += 'Цена: ' + str(
                food_info['price']) + ' ' + VALUTE + ' • ' + 'Выход: ' + str(food_info['weight']) + ' • ' + str(
                food_info['description'])
        else:
            text += str(food_info['name']) + '\n\n' + str(
                food_info['description']) + '\n\n' + 'Цена: ' + str(
                food_info['price']) + ' ' + VALUTE +'\n' + 'Выход: ' + str(food_info['weight'])
        return text
    except:
        return False


def edit_cart(user_id, food_id, plus):
    try:
        user_cart = get_user_cart(user_id)
        sql = new_sql()
        if food_id in user_cart.keys():
            old_count = user_cart[food_id]
            if plus:
                new_count = old_count + 1
            else:
                new_count = old_count - 1
            if new_count > 0:
                sql['cur'].execute('''UPDATE Cart
                SET count = ?
                WHERE user_id = ? AND food_id = ?''', (new_count, user_id, food_id))
            elif new_count <= 0:
                sql['cur'].execute('''DELETE from Cart
                WHERE user_id = ? AND food_id = ?''', (user_id, food_id))
        else:
            if plus:
                sql['cur'].execute('''INSERT INTO Cart(user_id, food_id, count) VALUES(?, ?, 1)''',
                                   (user_id, food_id))
        sql['con'].commit()
    except:
        return False


def food_menu_inline_keyboard(user_id, food_id):
    try:
        user_cart = get_user_cart(user_id)
        if food_id in user_cart.keys():
            count = user_cart[food_id]
        else:
            count = 0

        keyboard = types.InlineKeyboardMarkup()

        if count > 0:
            plus_button = types.InlineKeyboardButton(text=PLUS_TEXT,
                                                     callback_data=('plus][' + str(
                                                         food_id) + '][' + 'menu'))
            minus_button = types.InlineKeyboardButton(text=MINUS_TEXT,
                                                      callback_data=('minus][' + str(
                                                          food_id) + '][' + 'menu'))
            count_button = types.InlineKeyboardButton(text=str(count) + ' шт.', callback_data='null')

            keyboard.row(minus_button, count_button, plus_button)

            cart_button = types.InlineKeyboardButton(text=CART_TEXT,
                                                     callback_data=('cart][' + str(user_id)))
            menu_button = types.InlineKeyboardButton(text=FOOD_MENU_TEXT,
                                                     callback_data=('food_menu][' + str(user_id)))

            keyboard.row(menu_button, cart_button)
        else:
            add_to_cart = types.InlineKeyboardButton(text=ADD_TO_CART_TEXT,
                                                     callback_data=('add_cart][' + str(
                                                         food_id) + '][' + 'menu'))
            keyboard.add(add_to_cart)

        return keyboard
    except:
        return False


def cart_inline_keyboard(user_id, food_id):
    try:
        user_cart = get_user_cart(user_id)
        if food_id in user_cart.keys():
            count = user_cart[food_id]
        else:
            count = 0

        keyboard = types.InlineKeyboardMarkup()

        if count > 0:
            plus_button = types.InlineKeyboardButton(text=PLUS_TEXT,
                                                     callback_data=('plus][' + str(
                                                         food_id) + '][' + 'cart'))
            minus_button = types.InlineKeyboardButton(text=MINUS_TEXT,
                                                      callback_data=('minus][' + str(
                                                          food_id) + '][' + 'cart'))
            count_button = types.InlineKeyboardButton(text=str(count) + ' шт.', callback_data='null')

            keyboard.row(minus_button, count_button, plus_button)

            menu_button = types.InlineKeyboardButton(text=FOOD_MENU_TEXT,
                                                     callback_data=('food_menu][' + str(user_id)))

            keyboard.row(menu_button)

            order_button = types.InlineKeyboardButton(text=ORDER_TEXT,
                                                      callback_data=('order][' + str(user_id)))
            keyboard.row(order_button)
        else:
            add_to_cart = types.InlineKeyboardButton(text=BACK_TO_CART_TEXT,
                                                     callback_data=('add_cart][' + str(
                                                         food_id) + '][' + 'cart'))
            keyboard.add(add_to_cart)

        return keyboard
    except:
        return False


def send_user_cart(user_id, text_button=True):
    try:
        user_cart = get_user_cart(user_id)
        if user_cart:
            message = bot.send_message(user_id, 'Корзина')
            for i in user_cart:
                food_info = get_food_info_sql(i)
                message = bot.send_photo(user_id, photo=food_info['image_id'],
                                         caption=get_food_text(i),
                                         reply_markup=cart_inline_keyboard(user_id, i))
        else:
            message = bot.send_message(user_id, 'Корзина пуста')
        if text_button:
            bot.register_next_step_handler(message, food_menu_handler)
    except:
        message = bot.send_message(user_id, 'Неверный формат')
        bot.register_next_step_handler(message, food_menu_handler)


def send_contacts(user_id, food_menu=True):
    try:
        bot.send_message(user_id, 'Контакты')
        bot.send_message(user_id, 'Тут ваша информация')
        bot.send_location(user_id, 55.55, 55.55)
        print(food_menu)
        send_main_menu(user_id, True, food_menu, food_menu, food_menu, food_menu)
    except:
        return False


def get_user_info(user_id):
    try:
        user_info = new_sql()['cur'].execute('''SELECT * FROM Users
        WHERE id = ?''', (user_id,)).fetchone()

        user_dict = dict()
        user_dict['id'] = user_info[0]
        user_dict['name'] = user_info[1]
        user_dict['phone'] = user_info[2]
        user_dict['distribution'] = user_info[3]

        return user_dict
    except:
        return False


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    print(call)
    user_id = call.from_user.id
    data = call.data
    name = data.split('][')[0]
    if name != 'null':
        if name == "food_menu":
            send_food_menu(user_id, False)
        elif name == "text_us":
            send_write_us(user_id)
        elif name == "text_us":
            send_contacts(user_id)
        elif name == 'distribution':
            switch_on = {'on': 1, 'off': 0}[data.split('][')[1]]
            sql = new_sql()
            sql['cur'].execute('''UPDATE Users
            SET distribution = ?
            WHERE id = ?''', (switch_on, user_id))
            sql['con'].commit()
            if switch_on:
                bot.answer_callback_query(call.id, "Подписка на рассылку включена")
            else:
                bot.answer_callback_query(call.id, 'Подписка на рассылку отключена')
        elif name == 'inline_category':
            category = int(data.split('][')[1])
            sql = new_sql()
            sql['cur'].execute('''UPDATE Inline_users
                SET category = ?
                WHERE user_id = ?''', (category, user_id))
            sql['con'].commit()
            bot.answer_callback_query(call.id, "Категория выбрана")
        elif name in ['plus', 'minus', 'add_cart']:
            food_id = int(data.split('][')[1])
            mode = data.split('][')[2]
            plus = {'plus': True, 'minus': False, 'add_cart': True}[name]
            edit_cart(user_id, food_id, plus)
            if mode == 'cart':
                keyboard = cart_inline_keyboard(user_id, food_id)
            else:
                keyboard = food_menu_inline_keyboard(user_id, food_id)
            if call.inline_message_id:
                bot.edit_message_reply_markup(inline_message_id=call.inline_message_id,
                                              reply_markup=keyboard)
            else:
                bot.edit_message_reply_markup(message_id=call.message.message_id,
                                              chat_id=call.from_user.id, reply_markup=keyboard)
            bot.answer_callback_query(call.id)
        elif name == 'cart':
            send_user_cart(user_id, text_button=False)
            bot.answer_callback_query(call.id)
        elif name == 'order':
            text = order_info(user_id)['text']
            keyboard = types.InlineKeyboardMarkup()

            menu_button = types.InlineKeyboardButton(text=FOOD_MENU_TEXT,
                                                     callback_data='food_menu][')
            place_order_button = types.InlineKeyboardButton(text=PLACE_ORDER_TEXT,
                                                            callback_data='place_order][')
            keyboard.row(menu_button)
            keyboard.row(place_order_button)
            message = bot.send_message(user_id, text=text, reply_markup=keyboard)
            bot.answer_callback_query(call.id)

        elif name == 'place_order':
            user_info = get_user_info(user_id)
            if user_info['name'] and user_info['phone']:
                bot.send_message(user_id, 'Вы сохранены в боте как ' + user_info[
                    'name'] + '. Номер телефона: ' + str(user_info['phone']) + '.')
                keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

                confirm_button = types.KeyboardButton('Использовать эти данные')
                new_button = types.KeyboardButton('Ввести новые')

                keyboard.row(confirm_button)
                keyboard.row(new_button)

                message = bot.send_message(user_id, 'Использовать эти данные или ввести новые?',
                                           reply_markup=keyboard)
                bot.register_next_step_handler(message, user_info_input_handler)
            else:
                ask_name(user_id)

        elif name == 'confirm_order':
            order_id = data.split('][')[1]
            sql = new_sql()
            sql['cur'].execute('''UPDATE Orders
            SET Status = 1
            WHERE order_id = ?''', (order_id,))
            keyboard = types.InlineKeyboardMarkup()
            confirmed_button = types.InlineKeyboardButton(text=GALOCHKA_TEXT + 'Подтверждено',
                                                          callback_data='null][')
            keyboard.add(confirmed_button)
            text = call.message.text
            new_text = 'Статус:'.join(text.split('Статус:')[:-1]) + 'Подтверждено'
            bot.edit_message_text(message_id=call.message.message_id,
                                  chat_id=call.message.chat.id, text=new_text)
            bot.edit_message_reply_markup(message_id=call.message.message_id,
                                          chat_id=call.message.chat.id, reply_markup=keyboard)
    else:
        bot.answer_callback_query(call.id)


def get_order_cart(order_id):
    cart = new_sql()['cur'].execute('''SELECT food_id, count FROM Order_foods
            WHERE order_id = ?''', (order_id,)).fetchall()
    cart_dict = dict()
    for i in cart:
        cart_dict[i[0]] = i[1]

    return cart_dict


def order_info(user_id=None, order_id=None, for_chat=False):
    try:
        if user_id:
            user_cart = get_user_cart(user_id)
        elif order_id:
            user_cart = get_order_cart(order_id)
            user_id = new_sql()['cur'].execute('''SELECT user_id FROM Orders
                WHERE order_id = ?''', (order_id,)).fetchone()[0]
        if for_chat:
            text = 'Новый заказ:\n\n'
        else:
            text = 'Ваш заказ:\n\n'
        summ = 0
        for i in user_cart.keys():
            food_info = get_food_info_sql(i)
            count = user_cart[i]
            summ_2 = food_info['price'] * count
            summ += summ_2
            if count > 1:
                text_2 = str(count) + ' x ' + food_info['name']
            else:
                text_2 = food_info['name']
            text += '🔸' + text_2 + '—' + str(summ_2) + ' ' + VALUTE + '\n'
        if for_chat:
            user_info = get_user_info(user_id)
            text += '\n' + 'Имя: ' + str(user_info['name']) + '\nНомер телефона: ' + str(
                user_info['phone']) + '\n'
        text += '\n' + 'Итого: ' + str(summ) + ' ' + VALUTE
        return {'text': text, 'summ': summ, 'cart': user_cart}
    except:
        return False


def user_info_input_handler(message):
    try:
        text = message.text
        if text == 'Использовать эти данные':
            confirm_order(message.from_user.id)
        elif text == 'Ввести новые':
            ask_name(message.from_user.id)
        else:
            message = bot.send_message(message.from_user.id, 'Нажимайте по кнопкам')
            bot.register_next_step_handler(message, user_info_input_handler)
    except:
        message = bot.send_message(message.from_user.id, 'Нажимайте по кнопкам')
        bot.register_next_step_handler(message, user_info_input_handler)


def confirm_order(user_id):
    message = bot.send_message(user_id, 'Подтвердить заказ?', reply_markup=confirm_keyboard())
    bot.register_next_step_handler(message, confirm_order_handler)


def confirm_order_handler(message):
    try:
        text = message.text
        if text == CONFIRM_TEXT:
            finish_confirm_order(message.from_user.id)
        elif text == CANCEL_TEXT:
            send_food_menu(message.from_user.id, False)
        else:
            message = bot.send_message(message.from_user.id, 'Нажимайте по кнопкам')
            bot.register_next_step_handler(message, confirm_order_handler)
    except:
        message = bot.send_message(message.from_user.id, 'Нажимайте по кнопкам')
        bot.register_next_step_handler(message, confirm_order_handler)


def finish_confirm_order(user_id):
    try:
        order_id = add_new_order(user_id, order_info(user_id)['summ'])
        print(order_id)
        cart_to_orders_food(user_id, order_id)
        keyboard = types.InlineKeyboardMarkup()
        confirm_button = types.InlineKeyboardButton(text=CONFIRM_TEXT,
                                                    callback_data='confirm_order][' + str(order_id))
        keyboard.add(confirm_button)
        bot.send_message(GROUP_ID, order_info(order_id=order_id, for_chat=True)[
            'text'] + '\n\n' + 'Статус: в обработке',
                         reply_markup=keyboard)

        bot.send_message(user_id, 'Спасибо, ваш заказ оформлен!')
        send_main_menu(user_id, True, False, False, False, False)
        print('asdasdsad')
    except:
        return False


def add_new_order(user_id, summ):
    sql = new_sql()
    sql['cur'].execute('''INSERT INTO Orders(user_id, cost, status) VALUES(?, ?, 0)''',
                       (user_id, summ))
    sql['con'].commit()
    order_id = sql['cur'].execute('''SELECT order_id FROM Orders
    WHERE user_id = ? AND cost = ?''', (user_id, summ)).fetchall()[-1][0]
    return order_id


def cart_to_orders_food(user_id, order_id):
    user_cart = get_user_cart(user_id)
    sql = new_sql()
    for i in user_cart.keys():
        sql['cur'].execute('''INSERT INTO Order_foods(order_id, food_id, count) VALUES(?, ?, ?)''',
                           (order_id, i, user_cart[i]))
    sql['con'].commit()
    delete_user_cart(user_id)


def delete_user_cart(user_id):
    sql = new_sql()
    sql['cur'].execute('''DELETE FROM Cart
    WHERE user_id = ?''', (user_id,))
    sql['con'].commit()


def edit_user_name(user_id, name):
    sql = new_sql()
    sql['cur'].execute('''UPDATE Users
    SET name = ?
    WHERE id = ?''', (name, user_id))
    sql['con'].commit()


def edit_user_phone(user_id, phone):
    sql = new_sql()
    sql['cur'].execute('''UPDATE Users
    SET phone_number = ?
    WHERE id = ?''', (phone, user_id))
    sql['con'].commit()


def ask_name(user_id):
    message = bot.send_message(user_id, 'Введите ваше имя:', reply_markup=cancel_keyboard())
    bot.register_next_step_handler(message, user_name_handler)


def user_name_handler(message):
    try:
        name = message.text
        if name:
            if name == CANCEL_TEXT:
                message = bot.send_message(message.from_user.id, 'Отмена',
                                           reply_markup=food_menu_keyboard())
            else:
                edit_user_name(message.from_user.id, name)
                ask_phone(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, 'Неверный формат')
            ask_name(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_name(message.from_user.id)


def ask_phone(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_button = types.KeyboardButton('Отправить номер телефона', request_contact=True)
    keyboard.row(phone_button)
    cancel_button = types.KeyboardButton(CANCEL_TEXT)
    keyboard.row(cancel_button)
    message = bot.send_message(user_id, 'Введите ваш номер телефона:',
                               reply_markup=keyboard)
    bot.register_next_step_handler(message, user_phone_handler)


def user_phone_handler(message):
    try:
        if message.content_type == 'contact':
            phone = message.contact.phone_number
            edit_user_phone(message.from_user.id, phone)
            confirm_order(message.from_user.id)
        else:
            phone = message.text
            print(message)

            if phone:
                if phone == CANCEL_TEXT:
                    message = bot.send_message(message.from_user.id, 'Отмена',
                                               reply_markup=food_menu_keyboard())
                else:
                    edit_user_phone(message.from_user.id, phone)
                    confirm_order(message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Неверный формат')
                ask_name(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_name(message.from_user.id)


def send_admin_menu(user_id):
    admin_ids = get_admin_ids()
    if user_id in admin_ids:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        button_distribution = types.KeyboardButton('Рассылка')
        button_edit_menu = types.KeyboardButton('Редактор меню')

        keyboard.row(button_distribution, button_edit_menu, types.KeyboardButton('Выйти из админки'))

        today = datetime.date.today()
        week_start = today - datetime.timedelta(datetime.datetime.weekday(today))
        month_start = datetime.date(today.year, today.month, 1)

        sql = new_sql()

        users_count = len(sql['cur'].execute('''SELECT distribution FROM Users''').fetchall())

        day_users_count = len(sql['cur'].execute('''SELECT distribution FROM Users
                WHERE reg_date = ?''', (today,)).fetchall())

        week_users_count = len(sql['cur'].execute('''SELECT distribution FROM Users
                WHERE reg_date >= ?''', (week_start,)).fetchall())

        month_users_count = len(sql['cur'].execute('''SELECT distribution FROM Users
                    WHERE reg_date >= ?''', (month_start,)).fetchall())

        text = 'Это меню админки\n\nПодключенных пользователей: {}\nНовых за сегодня: {}\nНовых за неделю: {}\nНовых за месяц: {}\n'.format(
            str(users_count), str(day_users_count), str(week_users_count), str(month_users_count))

        message = bot.send_message(user_id, text=text, reply_markup=keyboard)

        bot.register_next_step_handler(message, admin_menu_handler)
    else:
        bot.send_message(user_id, text='У вас нет доступа')


def admin_menu_handler(message):
    try:
        send_us_admins = get_send_us_admins()
        if message.reply_to_message:
            if (message.from_user.id,) in send_us_admins:
                text = message.text
                msg_text = message.reply_to_message.text
                msg_user_id = int(msg_text.split('\n')[-1].split('ID: ')[-1])
                message = bot.send_message(msg_user_id, 'Вам пришел ответ от админа:\n' + text)
                bot.register_next_step_handler(message, main_menu_handler)
        else:
            if message.text == 'Рассылка':
                bot.send_message(message.from_user.id, 'Введите текст для рассылки')
                bot.send_message(message.from_user.id, 'Чтобы выйти нажмите кнопку Назад',
                                 reply_markup=back_keyboard())
                bot.register_next_step_handler(message, distribution_confirmation)
            elif message.text == 'Редактор меню':
                send_edit_menu(message.from_user.id)
            elif message.text == 'Выйти из админки':
                send_main_menu(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_name(message.from_user.id)


def send_edit_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    button_add_dish = types.KeyboardButton('Добавление товара')
    button_edit_dish = types.KeyboardButton('Редактор товара')
    button_add_edit_category = types.KeyboardButton('Добавление категорий')
    button_back = types.KeyboardButton('Назад')

    keyboard.row(button_add_dish, button_edit_dish)
    keyboard.row(button_add_edit_category, button_back)

    message = bot.send_message(user_id, text='Меню админки', reply_markup=keyboard)
    bot.register_next_step_handler(message, edit_menu_handler)


def edit_menu_handler(message):
    try:
        if message.text == 'Назад':
            send_admin_menu(message.from_user.id)
        elif message.text == 'Добавление товара':
            add_new_dish(message)
        elif message.text == 'Редактор товара':
            edit_dish(message.from_user.id)
        elif message.text == 'Добавление категорий':
            edit_category(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_name(message.from_user.id)


def edit_category(user_id):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    keyboard.row(types.KeyboardButton('Новая категория'),
                 types.KeyboardButton('Редактировать категорию'))
    keyboard.row(types.KeyboardButton('Удалить категорию'), types.KeyboardButton('Назад'))

    message = bot.send_message(user_id, 'Выберите режим', reply_markup=keyboard)
    bot.register_next_step_handler(message, edit_category_handler)


def edit_category_handler(message):
    try:
        text = message.text
        user_id = message.from_user.id

        if text == 'Новая категория':
            message = bot.send_message(user_id, 'Введите имя категории')
            bot.register_next_step_handler(message, new_category)
        elif text == 'Редактировать категорию':
            send_category_lst(user_id)
            message = bot.send_message(user_id,
                                       'Введите номер категории и новое название на новой строчке')
            bot.register_next_step_handler(message, edit_category_handler_2)
        elif text == 'Удалить категорию':
            send_category_lst(user_id)
            message = bot.send_message(user_id, 'Введите номер категории')
            bot.register_next_step_handler(message, delete_category)
        elif text == 'Назад':
            send_edit_menu(user_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_category(message.from_user.id)


def edit_category_handler_2(message):
    try:
        text = message.text.split('\n')
        number = text[0]
        name = text[1]
        sql = new_sql()
        sql['cur'].execute('''UPDATE Categories
        SET name = ?
        WHERE id = ?''', (name, number))
        sql['con'].commit()
        edit_category(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_category(message.from_user.id)


def new_category(message):
    try:
        name = message.text
        sql = new_sql()
        sql['cur'].execute('''INSERT INTO Categories(name) VALUES(?)''', (name,))
        sql['con'].commit()
        edit_category(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_category(message.from_user.id)


def delete_category(message):
    try:
        number = int(message.text)
        sql = new_sql()
        sql['cur'].execute('''DELETE FROM Categories
            WHERE id = ?''', (number,))
        sql['con'].commit()
        bot.send_message(message.from_user.id, 'Категория удалена')
        edit_category(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_category(message.from_user.id)


def number_to_category(number):
    category = number
    sql_categories = new_sql()['cur'].execute('''SELECT * FROM Categories''').fetchall()

    if category in list(map(lambda s: s[0], sql_categories)):
        for i in sql_categories:
            if i[0] == category:
                return i[1]
    return False


def edit_admin_edit_category(admin_id, add):
    sql = new_sql()
    sql['cur'].execute('''DELETE FROM Edit_dish
        WHERE admin_id = ?''', (admin_id,))
    if add:
        sql['cur'].execute('''INSERT INTO Edit_dish(admin_id) VALUES(?)''', (admin_id,))
    sql['con'].commit()


def edit_dish(admin_id):
    edit_admin_edit_category(admin_id, True)
    send_food_category(admin_id)
    message = bot.send_message(admin_id, 'Чтобы выйти нажмите кнопку Назад',
                               reply_markup=back_keyboard())
    bot.register_next_step_handler(message, edit_dish_handler)


def edit_dish_handler(message):
    try:
        user_id = message.from_user.id
        if message.content_type == 'text':
            if message.text == BACK_TEXT:
                send_edit_menu(user_id)
                edit_admin_edit_category(user_id, False)
        else:
            food_id = int(message.json['caption'])
            send_edit_food_menu(message.from_user.id, food_id)

    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def send_edit_food_menu(user_id, food_id):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_lst = [
        types.KeyboardButton('Название'),
        types.KeyboardButton('Описание'),
        types.KeyboardButton('Количество'),
        types.KeyboardButton('Категория'),
        types.KeyboardButton('Цена'),
        types.KeyboardButton('Фото'),
        types.KeyboardButton('Назад'),
        types.KeyboardButton('Удаление')
    ]

    keyboard.row(*button_lst[:4])
    keyboard.row(*button_lst[4:])

    food_info = get_food_info_sql(food_id)

    sql = new_sql()

    sql['cur'].execute('''UPDATE Edit_dish
                SET food_id = ?
                WHERE admin_id = ?''', (food_id, user_id))

    sql['con'].commit()

    message = bot.send_photo(user_id, photo=food_info['image_id'],
                             caption=get_food_text(food_id),
                             reply_markup=keyboard)
    bot.register_next_step_handler(message, edit_dish_handler_2)


def edit_dish_handler_2(message):
    try:
        text = message.text
        user_id = message.from_user.id
        if text == 'Назад':
            edit_dish(message.from_user.id)
        elif text == 'Название':
            message = bot.send_message(user_id, 'Напишите новое название')
            bot.register_next_step_handler(message, edit_dish_name)
        elif text == 'Описание':
            message = bot.send_message(user_id, 'Напишите новое описание')
            bot.register_next_step_handler(message, edit_dish_desc)
        elif text == 'Количество':
            message = bot.send_message(user_id, 'Напишите новое количество')
            bot.register_next_step_handler(message, edit_dish_weight)
        elif text == 'Цена':
            message = bot.send_message(user_id, 'Напишите новую цену')
            bot.register_next_step_handler(message, edit_dish_price)
        elif text == 'Фото':
            message = bot.send_message(user_id, 'Отправьте новое фото')
            bot.register_next_step_handler(message, edit_dish_image_id)
        elif text == 'Категория':
            send_category_lst(user_id)
            bot.register_next_step_handler(message, edit_dish_category)
        elif text == 'Удаление':
            message = bot.send_message(user_id, 'Точно хотите удалить товар?',
                                       reply_markup=confirm_keyboard())
            bot.register_next_step_handler(message, delete_food_confirm)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def delete_food_confirm(message):
    try:
        if message.text == CONFIRM_TEXT:
            food_id = get_edit_food_id(message.from_user.id)
            sql = new_sql()
            sql['cur'].execute('''DELETE FROM Dish
            WHERE id = ?''', (food_id,))
            sql['con'].commit()
            edit_dish(message.from_user.id)
        else:
            edit_dish(message.from_user.id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def get_edit_food_id(admin_id):
    sql = new_sql()

    food_id = sql['cur'].execute('''SELECT food_id FROM Edit_dish
    WHERE admin_id = ?''', (admin_id,)).fetchall()

    if food_id:
        return food_id[0][0]
    else:
        return False


def edit_dish_name(message):
    try:
        param = message.text
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET name = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def edit_dish_desc(message):
    try:
        param = message.text
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET description = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def edit_dish_weight(message):
    try:
        param = message.text
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET weight = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def edit_dish_price(message):
    try:
        param = float(message.text)
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET price = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def edit_dish_image_id(message):
    try:
        param = message.text
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET image_id = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def edit_dish_category(message):
    try:
        param = int(message.text)
        user_id = message.from_user.id
        food_id = get_edit_food_id(user_id)

        sql = new_sql()
        sql['cur'].execute('''UPDATE Dish
        SET price = ?
        WHERE id = ?''', (param, food_id))
        sql['con'].commit()
        send_edit_food_menu(user_id, food_id)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        edit_dish(message.from_user.id)


def update_new_dish(column_name, value, message):
    sql = new_sql()
    if type(value) == str:
        value = "'" + value + "'"

    sql['cur'].execute("""UPDATE New_dish
    SET {} = {}
    WHERE Admin_id = {}""".format(column_name, value, message.from_user.id))
    sql['con'].commit()


def send_category_lst(user_id):
    sql_categories = new_sql()['cur'].execute('''SELECT * FROM Categories''').fetchall()
    text = ''
    for i in sql_categories:
        row = str(i[0]) + ') ' + i[1] + '\n'
        text += row
    bot.send_message(user_id, 'Введите номер категории\n' + text)


def add_new_dish(message):
    try:
        sql = new_sql()
        sql['cur'].execute('''DELETE from New_dish
        WHERE admin_id = ?''', (message.from_user.id,))
        sql['cur'].execute('''INSERT INTO New_dish(admin_id) VALUES(?)''', (message.from_user.id,))
        sql['con'].commit()

        ask_new_dish_category(message)
    except:
        print('New Food Error')


def ask_new_dish_category(message):
    send_category_lst(message.from_user.id)
    bot.send_message(message.from_user.id, 'Чтобы выйти нажмите кнопку Назад',
                     reply_markup=back_keyboard())
    bot.register_next_step_handler(message, add_new_dish_category)


def add_new_dish_category(message):
    try:
        if message.text == BACK_TEXT:
            send_edit_menu(message.from_user.id)
        else:
            category = number_to_category(int(message.text))

            if category:
                update_new_dish('category', int(message.text), message)
                bot.send_message(message.from_user.id, 'Выбрана категория: ' + category)
                ask_new_dish_name(message)
            else:
                bot.send_message(message.from_user.id, 'Категория отсутствует')
                ask_new_dish_category(message)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_category(message)


def ask_new_dish_name(message):
    bot.send_message(message.from_user.id, 'Введите название')
    bot.register_next_step_handler(message, add_new_dish_name)


def add_new_dish_name(message):
    try:
        update_new_dish('name', message.text, message)
        bot.send_message(message.from_user.id, 'Название: ' + message.text)
        ask_new_dish_description(message)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_name(message)


def ask_new_dish_description(message):
    bot.send_message(message.from_user.id, 'Введите описание')
    bot.register_next_step_handler(message, add_new_dish_description)


def add_new_dish_description(message):
    try:
        update_new_dish('description', message.text, message)
        bot.send_message(message.from_user.id, 'Описание: ' + message.text)
        ask_new_dish_count(message)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_description(message)


def ask_new_dish_count(message):
    bot.send_message(message.from_user.id, 'Введите количество')
    bot.register_next_step_handler(message, add_new_dish_count)


def add_new_dish_count(message):
    try:
        update_new_dish('count', message.text, message)
        bot.send_message(message.from_user.id, 'Количество: ' + message.text)
        ask_new_dish_price(message)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_count(message)


def ask_new_dish_price(message):
    bot.send_message(message.from_user.id, 'Введите стоимость')
    bot.register_next_step_handler(message, add_new_dish_price)


def add_new_dish_price(message):
    try:
        update_new_dish('price', float(message.text), message)
        bot.send_message(message.from_user.id, 'Стоимость: ' + message.text)
        ask_new_dish_image(message)
    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_price(message)


def ask_new_dish_image(message):
    bot.send_message(message.from_user.id, 'Отправьте фотографию')
    bot.register_next_step_handler(message, add_new_dish_image)


def add_new_dish_image(message):
    try:
        print(message.content_type=='text')
        if message.content_type == 'text':
            image_id = message.text
            update_new_dish('image_id', image_id, message)
            confirm_dish(message)
        else:
            bot.send_message(message.from_user.id, 'Неверный формат')
            ask_new_dish_image(message)

    except:
        bot.send_message(message.from_user.id, 'Неверный формат')
        ask_new_dish_image(message)


def confirm_dish(message):
    dish_info = new_sql()['cur'].execute('''SELECT * FROM New_dish
    WHERE admin_id = ?''', (message.from_user.id,)).fetchall()[0]
    sql_categories = new_sql()['cur'].execute('''SELECT * FROM Categories''').fetchall()

    category = dish_info[1]

    if category in list(map(lambda s: s[0], sql_categories)):
        update_new_dish('category', category, message)
        for i in sql_categories:
            if i[0] == category:
                category = i[1]

    print(dish_info)

    text = ''
    text += 'Категория: ' + str(category) + '\n'
    text += 'Название: ' + str(dish_info[2]) + '\n'
    text += 'Описание: ' + str(dish_info[3]) + '\n'
    text += 'Количество: ' + str(dish_info[4]) + '\n'
    text += 'Цена: ' + str(dish_info[5])

    bot.send_message(message.from_user.id, 'Подтвердить?', reply_markup=confirm_keyboard())
    bot.register_next_step_handler(message, new_dish_confirm)


def new_dish_confirm(message):
    if message.text == CONFIRM_TEXT:
        dish_info = new_sql()['cur'].execute('''SELECT * FROM New_dish
            WHERE admin_id = ?''', (message.from_user.id,)).fetchall()[0]
        sql = new_sql()
        sql['cur'].execute(
            '''INSERT INTO Dish(name, image_id, category, description, weight, price) VALUES(?, ?, ?, ?, ?, ?)''',
            (dish_info[2], dish_info[6], dish_info[1], dish_info[3], dish_info[4], dish_info[5]))
        sql['con'].commit()
        bot.send_message(message.from_user.id, 'Товар создан')
    else:
        bot.send_message(message.from_user.id, 'Товар не создан')
    send_admin_menu(message.from_user.id)


def distribution_confirmation(message):
    global distribution_message
    if message.text == BACK_TEXT:
        send_admin_menu(message.from_user.id)
    else:
        distribution_message = message.text

        print(message)

        bot.send_message(message.from_user.id, text='Подтвердите рассылку',
                         reply_markup=confirm_keyboard())

        bot.register_next_step_handler(message, distribution)


def distribution(message):
    try:
        if message.text == CONFIRM_TEXT:
            users = new_sql()['cur'].execute('''
                SELECT id FROM Users
                WHERE distribution = 1
            ''')
            global distribution_message
            print(distribution_message)
            for user_id in users:
                print(user_id)
                bot.send_message(user_id[0], text=distribution_message)
            bot.send_message(message.from_user.id, 'Рассылка успешна')
        else:
            bot.send_message(message.from_user.id, 'Рассылка отменена')
        send_admin_menu(message.from_user.id)
    except:
        message = bot.send_message(message.from_user.id)
        bot.register_next_step_handler(message, 'Неверный формат')

while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        continue
