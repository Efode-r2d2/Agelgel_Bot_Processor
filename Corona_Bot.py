from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler
import requests
from Database import Database

'''

'''
updater = Updater(token="1105786287:AAEse9mWu9fNeKAoSernjVZK98v01pRjiT0")
dispatcher = updater.dispatcher

URL = "https://api.botmanager.negarit.net/api/"
database = Database()


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_request(route):
    req = requests.get(url=URL + route, auth=BearerAuth(
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNDQ1OGUxM2QyZTU3YjNkZjdkYzU2Njc1ZGZlYzE3NWIyY2EyM2I1YmRmZjFhN2ZlMDEwYjM0ZWFlNGI1MGFjNGRiZjhjODU4NjZiOWMzYmEiLCJpYXQiOjE1ODUyMzU0NjUsIm5iZiI6MTU4NTIzNTQ2NSwiZXhwIjoxNjE2NzcxNDY1LCJzdWIiOiIzIiwic2NvcGVzIjpbXX0.A83eklDs6PgdqmpnI05eB-bsytF39UTd9lqqE__C72CkjKouMt3XyouwbQi2D7ztANvgmZNlSfsOmyfqx6pIqro0IKR5MhcSB5YFwHas80NRjpRa2oPJY_mzKe8ss-0cHUDhCNjaolKMs4_gkAHFmSsjAUhRQ034NN_oDGXG1FttHkSd7kAN4_k-dgmRBEgiv5_DhLAdir9Xl2CHygU09wousDlHylgPaVdc8aWZUPOFmOXRecTvPC4K35Ai-uuxvf5FKx3eXKoS9I37-tqJ48hSeBeTEq3AdP6fLXUfFVosLOgx3jPiH-_rlQE1DdAMyfpGlL8AjpLFhDeNm8w4Y0t7idkXhQotkhA6M6bcRX0zW-PPLXSDPSb2kZahBCjOtY1OVuzWt5f_WueYgrINxzZDRwLzFdxJUwLWKRrof1hocZIG6rAkxulhjLUBv7NZAge_6ns4CWDXdVKT1RwCzBt1FZuufyz_qgpSgxnk_4DI3DICUxZHigOG8SrBhw9rJ4Mw2CTRezppNjIufyRZH3S3Yu60WCWzaItybeo-FkIuxs4gv6WzsNTp5Qa6aOk77EsquePh6eCKVtFCOFuV4Lc4T3Mt7sqMxwf06DTTx9cJashG7ZPTFN1zPsPrtucE_pQri3AF1l6KdbSZt-me27osIUy5jwWPcd67jhBcjtQ'))
    return req.json()


def start(bot, update):
    user_id = update.message.chat_id
    if database.check_user(user_id):
        parent_id = 0
        database.update_parent_id(user_id, parent_id)
    menus = []
    print("here i am")
    req = get_request('nav_menus_list/1')
    print(req)
    for i in req['result']:
        print("Menu",i['name'])
        menus.append(i['name'])
        print(menus)
        print("menus grouped", menus)
    keyboard = [menus[x:x + 2] for x in range(0, len(menus), 2)]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("Please choose your language?",
                              reply_markup=reply_markup)


def handle_menu(bot, update):
    user_id = update.message.chat_id
    print(user_id)
    if database.check_user(user_id):
        parent_id = database.get_parent_id(user_id)
        print("Parent ID", parent_id)
    else:
        parent_id = 0
        database.add_status(user_id, parent_id)
    print("Parent ID Starts with", parent_id)
    print(update.message.text)
    req = get_request('get_parents/' + str(parent_id) + '/' + update.message.text)
    results = req['result']
    print("Results", results)
    parent_id = results['parent']
    print("Parent", parent_id)
    parent_id = results['id']
    childs = []
    action = results['action']
    for i in results['childrens']:
        childs.append(i['name'])
    keyboard = [childs[x:x + 2] for x in range(0, len(childs), 2)]
    reply_markup1 = ReplyKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True)
    if len(keyboard) > 0:
        update.message.reply_text("...", reply_markup=reply_markup1)
        database.update_parent_id(user_id, parent_id)
    if action is not None:
        act_req = get_request('menus_bot/' + str(action))
        menu_result = act_req['result']
        for i in menu_result:
            menu_items = []
            for j in i['menu_items']:
                menu_items.append(InlineKeyboardButton(j['name'], callback_data=j['action']))
            keyboard = [menu_items[x:x + 1] for x in range(0, len(menu_items), 1)]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(i['name'] + "\n" + i['text'], reply_markup=reply_markup)
            bot.send_photo(chat_id=user_id, photo=i['image_url'])


def menu_actions(bot, update):
    query = update.callback_query
    act_req = get_request('menus_bot/' + str(query.data))
    menu_result = act_req['result']
    print(menu_result)
    print("Menu Items", menu_result[0]['menu_items'])
    menu_items_result = menu_result[0]['menu_items']
    menu_items = []
    for j in menu_items_result:
        print(j['name'])
        menu_items.append(InlineKeyboardButton(j['name'], callback_data=j['action']))
    keyboard = [menu_items[x:x + 1] for x in range(0, len(menu_items), 1)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(menu_result[0]['name'] + "\n" + menu_result[0]['text'],
                          chat_id=update.callback_query.message.chat_id,
                          message_id=update.callback_query.message.message_id, reply_markup=reply_markup)


user_info_handler = MessageHandler(Filters.text, handle_menu)
dispatcher.add_handler(user_info_handler)
updater.dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(menu_actions))
updater.start_polling()
