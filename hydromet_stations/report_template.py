from docxtpl import DocxTemplate
from docx import Document
from geopy import distance
from docx.shared import Inches
import pandas as pd
from io import BytesIO
from PIL import Image
import requests
import datetime

# Функция, которая будет обновлять и сохранять doc
# template  – шаблон файла на вход
# context - словарь
# report - имя или путь для нового обновленного файла 
def doc_report(template, context, report):
    doc = DocxTemplate(template)
    doc.render(context)
    doc.save(report)

# Cортировки по удалённости
def distanse_sorting(object_latitude, object_longitude, meteostations_path):
    meteostations = pd.read_csv(meteostations_path, sep=';')
    
    # Функция для расчёта расстояния до метеостанции
    def distanse_from_object(row):
        return int(distance.geodesic((object_latitude, object_longitude), (row["Latitude"], row["Longitude"])).km)
    
    # Функция для расчёта периода наблюдений
    def period(row):
        return datetime.datetime.now().year - int(row['ОТКРЫТИЕ'][-4:])

    meteostations["Distance_from_object"] = meteostations.apply(distanse_from_object, axis=1)
    meteostations["Period"] = meteostations.apply(period, axis=1)
    meteostations_100_km = meteostations[meteostations["Distance_from_object"] <= 100].sort_values(by='Distance_from_object')
    return meteostations_100_km
    
# Карта метостанций
def meteostation_map(mapbox_access_token, save_path, latitude, longitude):

    base_url = f"https://api.mapbox.com/styles/v1/kirillzhbakov/clpvgcma1001q01pj1yqqcxem/static/{longitude},{latitude},8,0/700x700?access_token={mapbox_access_token}"

    # Выполнение запроса
    response = requests.get(base_url)

    # Конвертация изображения в формат PIL
    image = Image.open(BytesIO(response.content))
    image = image.convert('RGB')
    image.save(save_path, format='JPEG')

# Вставка таблицы и карты в .docx
def table_map_paste(object_latitude, object_longitude, meteostations_path, meteostation_map_path, path_doc_input, path_doc_output):
    # Считывание данных из CSV и фильтрация до 100 км
    meteostations_100_km = distanse_sorting(object_latitude, object_longitude, meteostations_path)

    # Открытие документа
    doc = Document(path_doc_input)  

    # Получение таблицы из документа
    table_meteo_0 = doc.tables[0]  
    table_meteo_1 = doc.tables[1]

    # Перебор данных из DataFrame и заполнение таблицы в документе
    for index, row in meteostations_100_km.iterrows():
        new_row_0 = table_meteo_0.add_row().cells
        new_row_1 = table_meteo_1.add_row().cells
        new_row_0[0].text = str(row['НАЗВАНИЕ'])  
        new_row_0[1].text = str(row['ВМО'])
        new_row_0[2].text = str(row['ТИП'])  
        new_row_0[3].text = str(row['УГМС'])  
        new_row_0[4].text = str(row['Latitude'])  
        new_row_0[5].text = str(row['Longitude'])  
        new_row_0[6].text = str(row['ВЫС'])

        new_row_1[0].text = str(row['НАЗВАНИЕ'])  
        new_row_1[1].text = str(row['ВМО'])
        new_row_1[2].text = str(row['ОТКРЫТИЕ'])    
        new_row_1[3].text = str(row['ЗАКРЫТИЕ'])  
        new_row_1[4].text = str(row['Period'])   
        new_row_1[5].text = str(row['ИЗМЕНЕНИЯ']) 
        new_row_1[6].text = str(row['Distance_from_object'])  

    # Вставка карты метеостанций
    doc.add_picture(meteostation_map_path, width=Inches(5.5))

    # Сохранение обновленного документа
    doc.save(path_doc_output)  