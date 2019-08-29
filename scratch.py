import telebot
import requests
import pymongo

creator_name = ''
film_name = ''
cinema_name = ''
time = ''
price = 0
friend_name = ''
id_event= ''

bot_key = '770366044:AAG6Q6WSts1g5ayN8mZFxafEp0a3pvzr3s8'
db_pass = 'test'


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
    client = pymongo.MongoClient("mongodb+srv://test:{}@m0-vg5m1.mongodb.net/test?retryWrites=true&w=majority".format(db_pass))
    db = client.kino_db.get_collection(collection_name)
    return db

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
    # global price;
    # global id_event;
    global creator_name
    global filem_name
    global cinema_name
    global time
    global price
    price = message.text;
    db = db_connection("kino_collection")
    record = {
        'creator_name': creator_name,
        'movie': film_name,
        'cinema': cinema_name,
        'time': time,
        'price': price
    }
    db.insert_one(record)
    bot.send_message(message.from_user.id, 'Ты молодец! \n \n ' + film_name + '  '+ cinema_name + '  ' + price + '  ' + time + '  ' + ' \n \n Осталось пригласить друзей. Отправь приглашения или иди на главное меню.',reply_markup=keyboard2);


keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Создать событие', 'Мои события', 'Приглашения')

@bot.message_handler(commands=['start'])
def start_message(message):
    global creator_name
    creator = bot.get_chat_member(message.chat.id, message.from_user.id)
    creator_name = creator.user.first_name
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
            'Чтобы создать событие тебе нужно будет заполнить 4 параметра: Фильм, Кинотетар, Время сеанса и стоимость билета. Поехали! На какой фильм идем?'
        )
        bot.register_next_step_handler(message, get_film);  # следующий шаг – функция get
