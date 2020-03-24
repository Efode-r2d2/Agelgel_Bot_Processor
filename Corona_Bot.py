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
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYzU5MWViZjM2OWI1ZWZlYTZkYWFlMjRjZjU0MmRkMDIwNTAxODAxNzIxMmRiNTQyZWVjOTYwYzg4MTU0NDBkNjUyN2I2NTVmOGFlZTZiMmUiLCJpYXQiOjE1ODQ5ODMxNTUsIm5iZiI6MTU4NDk4MzE1NSwiZXhwIjoxNjE2NTE5MTU1LCJzdWIiOiIzIiwic2NvcGVzIjpbXX0.kIFfhozDNU9B3pZmQm7H5rD7MqUtBo7c8uXQpElJS4aGpxgbr_3Z-ksLUJXEqBNkjy9f5VDQOVCubjEwXuLQkZmejwaT1VHBBV24FJpEVGL-KH7ugkGnA2ReKI50uDpfp3KAgiw-0H6SZX-8eTiT8b0jo7lXFOmqQbJxqxvUPokXVRLBTGWzKCUCujIyAZgYJ_PZrCr48n3alZlvJ-pnuCuCva9H7ApJ7Glk9dRbWya0pLuhHxVL7rWOkQVz5C-LQRXD-x0n_Hn1q8HqrWZ6bp1LH7HAoRhob4aB0Xs8CVyRjtkm7S8LOY9ZAb5UZ7SJz997U3CAOXbZWRwbw3HSowK-3qjEOj2o7oxxM1jrM0zJoWLVWPF2CfnvhjnTuuBOxsXlHNLfDkvBaggJ25M-loMIPSN1XHJeFqalVe-ktWdmxYarWT6MFs70_omUrDQJX_JNM-dvxvsGmcxlCfGTHpGSj8kXdsZAezh8jVub-W2viCi6AZoHBrjCZJo2r11DO5Qkles3Wzx0ZLmfIFhFyhaVstKJF8bMhMUrLxdPAoZ8-_weQYOUJT676WeaLpUz7KkKt_eO8iINSOPVdEmS1TC59lxXTEOjI0LQnvx9pNeiiciCEH4BHiQMpFP6QNiha8zjqmj8B7JO3VJLZOPjmzIai5IOMtbb3y2ylh8EuXo'))
    return req.json()


def start(bot, update):
    user_id = update.message.chat_id
    if database.check_user(user_id):
        parent_id = 0;
        database.update_parent_id(user_id, parent_id)
    menus = []
    req = get_request('nav_menus_list/1')
    for i in req['result']:
        menus.append(i['name'])
        if not database.check_menu(i['id']):
            database.insert_menu(i['id'], i['name'], i['parent'])
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
