import telebot, os, time, shutil, json
import introduction.TR_to_gpt as tr
from dotenv import load_dotenv
from hydromet_stations.report_template import doc_report, meteostation_map, table_map_paste

# Подгрузка ключей
load_dotenv()
bot_token = os.environ.get("HYDRO_TEST_BOT_TOKEN")
KEY_convert = os.environ.get("API_Secret_convert")
mapbox_token = os.environ.get("MAPBOX_TOKEN")
bot = telebot.TeleBot(bot_token)
user_status = {}

# Стартовая функция
@bot.message_handler(commands=['start'])
def start(message : telebot.types.Message):

    start_text = '''
Привет, {}!\n 
Я помогу сделать отчёт по инженерно-гидрометеорологическим изысканиям.\n 
Доступны следующие инструменты:
- /start - основная информация о боте;
- /introduction - создание введения;
- /hydromet_stations - предоставление метеорологической изученности по координатам.
    '''.format(message.from_user.first_name)
    
     # ответ с коммандами
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    start_item = telebot.types.KeyboardButton("/start")
    introdiction_item = telebot.types.KeyboardButton("/introduction")
    hydromet_stations_item = telebot.types.KeyboardButton("/hydromet_stations")
    markup.add(start_item, introdiction_item, hydromet_stations_item)

    bot.send_message(message.chat.id, start_text, reply_markup=markup)

# Функция introduction
@bot.message_handler(commands=['introduction'])
# Приветствие
def introduction_start(message : telebot.types.Message):
    start_text = '''Отправь мне файл ТЗ формата docx или pdf. Объем ТЗ не должен превышать шести страниц.'''
    bot.send_message(message.chat.id, start_text)

    user_status[message.chat.id] = 'waiting_for_TRdocument'

@bot.message_handler(content_types=['document'])
# Исполнение функции
def introduction(message : telebot.types.Message):
    try:
        # Проверяем статус пользователя
        if message.chat.id in user_status and user_status[message.chat.id] == 'waiting_for_TRdocument':

            # Получаем информацию о файле
            file_info = bot.get_file(message.document.file_id)
            file_path = file_info.file_path

            # Скачиваем файл    
            downloaded_file = bot.download_file(file_path)

            # Создаём папки
            os.mkdir("introduction/input")
            os.mkdir("introduction/output")

            # Сохраняем файл
            path = "introduction/input"
            file_name = message.document.file_name
            if '.pdf' in file_name:
                file_path = os.path.join(path, "TR.pdf")
            elif '.docx' in file_name:
                file_path = os.path.join(path, "TR.docx")
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)

            bot.reply_to(message, "Файл загружен! Ожидайте Введение в течение 0-5 минут.")

            # Смотрим на формат загруженного файла – docx или pdf
            text_for_chat_gpt = tr.file_compare(file_path)

            # Текст введения, который сгенерил chatgpt
            gpt_answer = tr.TR_introduction(text_for_chat_gpt)
            print('GTP answer was done!')
            print(gpt_answer)

            introduction_dict = json.loads(gpt_answer)
            print(introduction_dict)

            # Путь в котором будет сохраняться Введение
            introduction = os.path.join(path, "Introduction.docx")

            # Путь шаблона
            template = os.path.join("introduction", "template.docx")

            # Создание файла с введением
            doc_report(template, introduction_dict, introduction)

            bot.reply_to(message, "ВВЕДЕНИЕ:")
            # Отправка файла клиенту
            with open(introduction, 'rb') as f:
                bot.send_document(message.chat.id, f)

            # Очистка папок
            shutil.rmtree("introduction/input")
            shutil.rmtree("introduction/output")

            # Обработка файла, отправка результата и т.д.

            # Сбрасываем статус ожидания для данного пользователя
            del user_status[message.chat.id]
        
        else:
            bot.reply_to(message, "Пожалуйста, отправьте документ после ввода команды")
    
    except Exception as e:
        bot.reply_to(message, e)
        # Очистка папок
        shutil.rmtree("introduction/input")
        shutil.rmtree("introduction/output")
        print(e)


# Функция изученности
@bot.message_handler(commands=['hydromet_stations'])
# Приветствие
def introduction_start(message : telebot.types.Message):
    start_text = """Напиши координаты участка изысканий через запятую в десятичном формате. Пример: 55.702969, 37.530752"""
    bot.send_message(message.chat.id, start_text)

    user_status[message.chat.id] = 'waiting_for_coordinates'

@bot.message_handler(content_types=['text'])
# Выполнение функции
def hydromet_stations(message : telebot.types.Message):
    
    if message.chat.id in user_status and user_status[message.chat.id] == 'waiting_for_coordinates':
        bot.reply_to(message, "Обработка... ⏳")
        coordinates = message.text.split(', ')
        coordinates = [float(item) for item in coordinates]
        latitude = coordinates[0]
        longitude = coordinates[1]
        meteostation_map('pk.eyJ1Ijoia2lyaWxsemhiYWtvdiIsImEiOiJjajRpcGp1NWMwYzJrMzJwZ2RzMGhxOG5uIn0.THsBR9cHFM49Zq1yJ85maw',
                          "hydromet_stations/meteostation_map.jpg",
                           latitude,
                           longitude)
        
        table_map_paste(latitude, longitude, "hydromet_stations/meteostations_0.csv",
                                "hydromet_stations/meteostation_map.jpg", 
                                "hydromet_stations/hydromet_stations_template.docx",
                                "hydromet_stations/hydromet_stations_output.docx")
    
        bot.reply_to(message, "Метеорологическая изученность:")
            # Отправка файла клиенту
        with open("hydromet_stations/hydromet_stations_output.docx", 'rb') as f:
            bot.send_document(message.chat.id, f)
        
        del user_status[message.chat.id]

    else: 
        bot.reply_to(message, 'Пожалуйста, отправьте сообщение после ввода команды')

if __name__ == "__main__":
    print('Hydromet_bot started.')
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(15)  # Пауза перед следующей попыткой