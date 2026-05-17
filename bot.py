import telebot
from telebot import types
import db
import stats
from datetime import date

TOKEN = 'токен'
bot = telebot.TeleBot(TOKEN)
u = {} 

def main_kb():
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add('Записать день', 'Статистика')
    k.add('История', 'Очистить', 'Помощь')
    return k

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 'Ас салам алейкум! Трекер настроения.', reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Помощь')
def help_h(m):
    t = "Как пользоваться:\n\n1 Записать день — ввод данных.\n2 Статистика — графики и среднее.\n3 Инсайты — влияние сна.\n4 История — последние записи.\n5 Очистить — удалить всё."
    bot.send_message(m.chat.id, t, reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Записать день')
def add_d(m):
    u[m.chat.id] = {'s': 'set', 'd': date.today().isoformat(), 'set': 0}
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row('1 😞', '2 😐', '3 🙂', '4 😊', '5 🤩')
    bot.send_message(m.chat.id, 'Настроение (1-5):', reply_markup=k)

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 'set')
def get_m(m):
    try:
        v = int(m.text.split()[0])
        if 1 <= v <= 5:
            u[m.chat.id]['set'] = v
            u[m.chat.id]['s'] = 'work'
            k = types.ReplyKeyboardMarkup(resize_keyboard=True)
            k.row('0.5', '1', '2', '4', 'Другое')
            bot.send_message(m.chat.id, 'Часов работы:', reply_markup=k)
        else:
            bot.send_message(m.chat.id, 'Жми кнопку.')
    except:
        bot.send_message(m.chat.id, 'Ошибка.')

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 'work')
def get_w(m):
    cid = m.chat.id
    txt = m.text.strip().replace(',', '.')
    if txt == 'Другое':
        u[cid]['s'] = 'w_in'
        bot.send_message(cid, 'Пиши число:', reply_markup=types.ReplyKeyboardRemove())
        return
    try:
        u[cid]['w'] = float(txt)
        ask_sl(cid)
    except:
        bot.send_message(cid, 'Пиши число.')

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 'w_in')
def get_wi(m):
    try:
        u[m.chat.id]['w'] = float(m.text.replace(',', '.'))
        ask_sl(m.chat.id)
    except:
        bot.send_message(m.chat.id, 'Не число.')

def ask_sl(cid):
    u[cid]['s'] = 'sleep'
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row('6', '7', '8', '9', 'Другое')
    bot.send_message(cid, 'Часов сна:', reply_markup=k)

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 'sleep')
def get_sl(m):
    cid = m.chat.id
    txt = m.text.strip().replace(',', '.')
    if txt == 'Другое':
        u[cid]['s'] = 's_in'
        bot.send_message(cid, 'Пиши число:', reply_markup=types.ReplyKeyboardRemove())
        return
    try:
        u[cid]['sl'] = float(txt)
        ask_com(cid)
    except:
        bot.send_message(cid, 'Пиши число.')

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 's_in')
def get_sli(m):
    try:
        u[m.chat.id]['sl'] = float(m.text.replace(',', '.'))
        ask_com(m.chat.id)
    except:
        bot.send_message(m.chat.id, 'Не число.')

def ask_com(cid):
    u[cid]['s'] = 'com'
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add('Пропустить')
    bot.send_message(cid, 'Комментарий?', reply_markup=k)

@bot.message_handler(func=lambda m: m.chat.id in u and u[m.chat.id]['s'] == 'com')
def save(m):
    cid = m.chat.id
    d = u[cid]
    com = None if m.text == 'Пропустить' else m.text
    db.add_record(cid, d['d'], d['set'], d['w'], d['sl'], com)
    del u[cid]
    bot.send_message(cid, 'Сохранено.', reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Статистика')
def show_st(m):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton('Неделя', callback_data='st_7'))
    k.add(types.InlineKeyboardButton('Месяц', callback_data='st_30'))
    k.add(types.InlineKeyboardButton('Инсайты', callback_data='st_ins'))
    k.add(types.InlineKeyboardButton('График', callback_data='st_chart'))
    bot.send_message(m.chat.id, 'Выбери:', reply_markup=k)

@bot.callback_query_handler(func=lambda c: c.data.startswith('st_'))
def proc_st(c):
    cid = c.message.chat.id
    days = 7 if c.data == 'st_7' else 30 if c.data == 'st_30' else 365
    if c.data == 'st_ins': days = 365
    
    recs = db.get_records(cid, days)
    if not recs:
        bot.send_message(cid, 'Нет данных.', reply_markup=main_kb())
        bot.answer_callback_query(c.id)
        return

    if c.data == 'st_ins':
        bot.send_message(cid, stats.get_insights(recs))
    elif c.data == 'st_chart':
        f = f'chart_{cid}.png'
        stats.create_chart(recs, f)
        with open(f, 'rb') as ph:
            bot.send_photo(cid, ph, caption='График')
        import os
        if os.path.exists(f): os.remove(f)
    else:
        am = sum(r['set'] for r in recs)/len(recs)
        aw = sum(r['work_hours'] for r in recs)/len(recs)
        asn = sum(r['sleep_hours'] for r in recs)/len(recs)
        bot.send_message(cid, f'Среднее:\nНастр: {am:.1f}\nРабота: {aw:.1f}ч\nСон: {asn:.1f}ч')
    
    bot.answer_callback_query(c.id)
    bot.send_message(cid, 'Меню:', reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'История')
def show_h(m):
    recs = db.get_records(m.chat.id, 365)
    if not recs:
        bot.send_message(m.chat.id, 'Пусто.', reply_markup=main_kb())
        return
    txt = 'История:\n'
    for r in recs[-5:]:
        txt += f"{r['date']} | {r['set']} | {r['work_hours']}ч | {r['sleep_hours']}ч\n"
    bot.send_message(m.chat.id, txt, reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Очистить')
def clear_d(m):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton('Да', callback_data='cl_y'))
    k.add(types.InlineKeyboardButton('Нет', callback_data='cl_n'))
    bot.send_message(m.chat.id, 'Удалить всё?', reply_markup=k)

@bot.callback_query_handler(func=lambda c: c.data.startswith('cl_'))
def conf_cl(c):
    if c.data == 'cl_y':
        db.clear_user_data(c.message.chat.id)
        bot.send_message(c.message.chat.id, 'Удалено.', reply_markup=main_kb())
    else:
        bot.send_message(c.message.chat.id, 'Отмена.', reply_markup=main_kb())
    bot.answer_callback_query(c.id)

if __name__ == '__main__':
    db.init_db()
    print('Run')
    bot.polling(none_stop=True)
