import telebot
import requests
import pymongo
from telebot import types
from bson import ObjectId

creator_name = ''
film_name = ''
cinema_name = ''
time = ''
price = 0
friend_name = ''
id_event= ''
invite_event =''
enter_message =''

bot_key = '770366044:AAG6Q6WSts1g5ayN8mZFxafEp0a3pvzr3s8'
db_pass = '5203065'


bot = telebot.TeleBot(bot_key)

def push_record(cur, record):
    cur.insert_one(record)

def get_record(cur, user_id):
    records = cur.find_one({"user_id": user_id})
    return records

def update_record(cur, record, updates):
    cur.update_one(
        {'_id': record['_id']},
        {'$set': updates},
        upsert=False
    )

def db_connect(collection_name):
    # client = pymongo.MongoClient("mongodb+srv://test:{}@m0-vg5m1.mongodb.net/test?retryWrites=true&w=majority".format(db_pass))
    client = pymongo.MongoClient(
        "mongodb+srv://askar:5203065@cluster0-3myx0.mongodb.net/test?retryWrites=true&w=majority")
    db = client.kino_db.get_collection(collection_name)
    return db

def get_partisipation_events(message):
    db = db_connect("events")
    records = db.find({'agree': "@"+creator_username})
    for i in records:
        bot.send_message(message.from_user.id,
                         i['movie'] + "\n" + i['cinema'] + "\n" + i['time'] + "\n" + i['price'] + "\n" + "Идут: " + str(i['agree'])+ "\n" + "Не идут: " + str(i['not_agree']));


def get_all_events(message): #получаем
    db = db_connect("events")
    # db1= db_connect("invites")
    records = db.find({'creator_id': message.from_user.id})
    # invites = db1.find({'creator_id': message.from_user.id})
    for i in records:
        bot.send_message(message.from_user.id,
                         i['movie'] + "\n" + i['cinema'] + "\n" + i['time'] + "\n" + i['price'] + "\n" + "Идут: " + str(i['agree'])+ "\n" + "Не идут: " + str(i['not_agree']));

def get_film(message): #получаем фильм
    global film_name;
    film_name = message.text;
    bot.send_message(message.from_user.id, 'Хм... А у тебя хороший вкус. А в какой кинотеатр?');
    bot.register_next_step_handler(message, get_cinema);

def get_cinema(message): #получаем кинотеатр
    global cinema_name;
    cinema_name = message.text;
    bot.send_message(message.from_user.id, 'Говорят, что там хороший звук!) А во сколько сеанс??');
    bot.register_next_step_handler(message, get_time);

def get_time(message): #получаем время
    global time;
    time = message.text;
    bot.send_message(message.from_user.id, 'Идеальное время!) Ну и последнее...Цитата Дудя: Сколько стоит билет?');
    bot.register_next_step_handler(message, get_price);

def get_price(message): #получаем стоимость
    global creator_id
    global creator_name
    global film_name
    global creator_username
    global time
    global price
    global agree
    global not_agree
    price = message.text;
    db = db_connect("events")
    record = {
        'creator_id': creator_id,
        'creator_username': creator_username,
        'movie': film_name,
        'cinema': cinema_name,
        'time': time,
        'price': price,
        'agree': ["@"+creator_username],
        'not_agree': [],
    }
    db.insert_one(record)


    fresh = db.find_one(
        {'creator_id': creator_id,
        'creator_username': creator_username,
        'movie': film_name,
        'cinema': cinema_name,
        'time': time,
        'price': price})
    newlink = "https://t.me/Kinoorgbot?start=" + str(fresh['_id'])
    print(newlink)

    bot.send_message(message.from_user.id, 'Tы молодец! Перешли это сообщение, чтобы пригласить друзей!')
    # bot.send_message(message.from_user.id,
    #                  film_name + "\n" + cinema_name + "\n" + price + "\n" + time + "\n")
    keyboard2 = telebot.types.InlineKeyboardMarkup()
    url_button1 = telebot.types.InlineKeyboardButton(text="Ответить", url=str(newlink))
    keyboard2.add(url_button1)
    bot.send_message(message.from_user.id,film_name + "\n" + cinema_name + "\n" + price + "\n" + time + "\n", reply_markup=keyboard2)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    db = db_connect("events")
    hash_id = ObjectId(invite_event)
    invite_record = db.find_one({"_id": hash_id})
    if call.data == "yes":#call.data это callback_data, которую мы указали при объявлении кнопки
        print("Я тут")
        if creator_username not in invite_record['agree']:
            invite_record['agree'].append("@"+creator_username)
            db.update_one({'_id': hash_id}, {'$set': invite_record}, upsert=False)
            bot.answer_callback_query(call.id, text='Спасибо за ответ, мы передадим) ')
        else:
            bot.answer_callback_query(call.id, text='Ты уже записан! Все ок.')
    elif call.data == "no":
        if creator_username not in invite_record['not_agree']:
            invite_record['not_agree'].append("@"+creator_username)
            db.update_one({'_id': hash_id}, {'$set': invite_record}, upsert=False)
            bot.answer_callback_query(call.id, text='Нам очень жаль...')
        else:
            bot.answer_callback_query(call.id, text='Ты уже записан! Все ок.')


keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Создать событие', 'Мои события', 'Куда иду')

@bot.message_handler(commands=['start'])
def start_message(message):
    global enter_message
    global invite_event
    enter_message = message.text.split("/start ")
    if enter_message[0] != "/start":
        invite_event = enter_message[1]
        print(invite_event)
        hash_id = ObjectId(invite_event)
    # invite_event = "5d63d4b74124380cdd5cb31b"
    global creator_id
    global creator_name
    global creator_username
    creator = bot.get_chat_member(message.chat.id, message.from_user.id)
    creator_id = message.from_user.id
    creator_name = creator.user.first_name
    creator_username = creator.user.username
    db1 = db_connect("users")
    record = {
        'creator_id': message.from_user.id,
        'creator_name': creator_name,
        'creator_alias': creator_username,
    }
    if db1.find_one({'creator_id': message.from_user.id}) is None:
            db1.insert_one(record)

    if (invite_event != ""):
        print("Зашли" + str(hash_id))
        keyboard2 = types.InlineKeyboardMarkup();  # наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Иду', callback_data='yes');  # кнопка «Да»
        keyboard2.add(key_yes);  # добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Не иду', callback_data='no');
        keyboard2.add(key_no);
        db = db_connect("events")
        i = db.find_one({"_id": hash_id})
        # question = invite_record['movie'] + "\n" + invite_record['cinema'] + "\n" + invite_record['time'] + "\n" + invite_record['price'] + "\n" + "\n"
        # print(invite_record)
        # print(str(invite_record['_id']))
        question = str(i['movie'] + "\n" + i['cinema'] + "\n" + i['time'] + "\n" + i['price'] + "\n" + "Идут: " + str(i['agree'])+ "\n" + "Не идут: " + str(i['not_agree']));
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard2)
    else: print("Тут пусто")

    bot.send_message(
        message.chat.id,
        'Привет! Спасибо, что ты здесь! Давай я тебе помогу собрать твоих друзей в кино! Выбери действие внизу:',
        reply_markup=keyboard1
    )

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'создать событие':
        bot.send_message(
            message.chat.id,
            'Чтобы создать событие тебе нужно будет заполнить 4 параметра: Фильм, Кинотетар, Время сеанса и стоимость билета. Поехали! \n\nНа какой фильм идем? \nНапример: Король Лев 2'
        )
        bot.register_next_step_handler(message, get_film);  # следующий шаг – функция get
    elif message.text.lower() == 'мои события':
        bot.send_message(
            message.chat.id,
            'Да ты крутой организатор. Лови твои события:  '
        )
        get_all_events(message)
    elif message.text.lower() == 'куда иду':
        bot.send_message(
            message.chat.id,
            'Скорее беги:  '
        )
        get_partisipation_events(message)

bot.polling()
