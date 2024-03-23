import telebot, os, time, shutil, json
import introduction.TR_to_gpt as tr
from dotenv import load_dotenv
from hydromet_stations.report_template import doc_report, station_map, table_map_paste
from levels.transformation import GB_to_Profiles_tranformation

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
- /hydromet_stations - предоставление гидрометеорологической изученности по координатам.
- /gb_to_profiles_transform - трансформация профилей global mapper в профили Profiles.
    '''.format(message.from_user.first_name)
    
     # ответ с коммандами
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    start_item = telebot.types.KeyboardButton("/start")
    introdiction_item = telebot.types.KeyboardButton("/introduction")
    hydromet_stations_item = telebot.types.KeyboardButton("/hydromet_stations")
    gb_to_profiles_transform = telebot.types.KeyboardButton("/gb_to_profiles_transform")
    markup.add(start_item, introdiction_item, hydromet_stations_item, gb_to_profiles_transform)

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
        # Проверяем статус пользователя (introduction)
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
        
        # Проверяем статус пользователя (GB_transform)
        elif message.chat.id in user_status and user_status[message.chat.id] == "waiting_for_gb_profile_zip":
            # Получаем информацию о файле
            file_info = bot.get_file(message.document.file_id)
            file_path = file_info.file_path

            # Скачиваем файл    
            downloaded_file = bot.download_file(file_path)

            # Сохраняем файл
            path = "levels"
            file_name = message.document.file_name
            file_path = os.path.join(path, str(message.chat.id) +".zip")
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)

            bot.reply_to(message, "Обработка... ⏳")

            output_zip = f"levels/{message.chat.id}_output.zip"
            GB_to_Profiles_tranformation(str(message.chat.id), "levels", file_path, output_zip)

            bot.reply_to(message, "zip-архив с файлами для Profiles:")
            # Отправка файла клиенту
            with open(output_zip, 'rb') as f:
                bot.send_document(message.chat.id, f)
            
            # Удаление output zip
            if os.path.exists(output_zip):
                os.remove(output_zip)
                print(f'Архив "{output_zip}" успешно удален.')

            del user_status[message.chat.id]

        else:
            bot.reply_to(message, "Пожалуйста, отправьте документ после ввода команды или пришлите верный формат файла")
    
    except Exception as e:
        bot.reply_to(message, e)
        # Очистка папок
        if os.path.exists("introduction/input"):
            shutil.rmtree("introduction/input")

        if os.path.exists("introduction/output"):
            shutil.rmtree("introduction/output")
        print(e)

# Функция изученности
@bot.message_handler(commands=['hydromet_stations'])
# Приветствие
def introduction_start(message : telebot.types.Message):
    start_text = """Напиши координаты участка изысканий через запятую и пробел в десятичном формате. Пример: 55.70, 37.53"""
    bot.send_message(message.chat.id, start_text)

    user_status[message.chat.id] = 'waiting_for_coordinates'

# Функция трансформации из GB профиля в формат profiles
@bot.message_handler(commands=['gb_to_profiles_transform'])
def GB_to_profiles_transform_start(message : telebot.types.Message):
    user_status[message.chat.id] = "waiting_for_gb_profile_zip"
    text = """Отправь zip-архив содержащий профили, сделанные в Global Mapper в формате .csv. В ответ я пришлю zip-архив с txt файлами пригодными для открытия в программе Profiles"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
# Выполнение функции
def hydromet_stations(message : telebot.types.Message):
    
    if message.chat.id in user_status and user_status[message.chat.id] == 'waiting_for_coordinates':
        bot.reply_to(message, "Обработка... ⏳")
        coordinates = message.text.split(', ')
        coordinates = [float(item) for item in coordinates]
        latitude = coordinates[0]
        longitude = coordinates[1]
        
        # Карта метостанций
        station_map(
                    mapbox_token,
                    "hydromet_stations/meteostation_map.jpg",
                    latitude,
                    longitude,
                    "https://api.mapbox.com/styles/v1/kirillzhbakov/clpvgcma1001q01pj1yqqcxem/static"
                    )
        print("Meteostation map created.")

        # Карта гидрологических постов
        station_map(
                    mapbox_token,
                    "hydromet_stations/hydrostation_map.jpg",
                    latitude,
                    longitude,
                    "https://api.mapbox.com/styles/v1/kirillzhbakov/clrbxrhvz009d01pi0ziz45sj/static"
                    )
        print("Hydrostation map created.")

        # Вставка карт и таблиц в документ
        table_map_paste(
                        latitude, longitude,
                        "hydromet_stations/meteostations_0.csv", "hydromet_stations/meteostation_map.jpg",
                        "hydromet_stations/hydro_stations.csv", "hydromet_stations/hydrostation_map.jpg",
                        "hydromet_stations/hydromet_stations_template.docx", "hydromet_stations/hydromet_stations_output.docx"
                        )
        print("Output docx created.")
    
        bot.reply_to(message, "Гидрометеорологическая изученность:")
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