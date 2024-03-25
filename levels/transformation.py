import pandas as pd
import zipfile
import shutil
import os

def zip_folder(folder_path, zip_path_output):
    """
    Архивирует папку, включая все подпапки и файлы, в ZIP-файл.

    :param folder_path: Путь к папке, которую нужно заархивировать.
    :param zip_path: Путь, где будет сохранен ZIP-архив.
    """
    with zipfile.ZipFile(zip_path_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Корневая директория и все поддиректории
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Создаем относительный путь файла для сохранения структуры папок в архиве
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=os.path.dirname(folder_path))
                # Добавляем файл в архив
                zipf.write(file_path, arcname=arcname)

def GB_to_Profiles_tranformation(chat_id, folder_name, zip_path_input, zip_path_output):
    #Создание папки
    folder_path = os.path.join(folder_name, chat_id)
    os.makedirs(folder_path, exist_ok=True)

    # Открытие ZIP архива для чтения
    with zipfile.ZipFile(zip_path_input, "r") as z:

        file_names = z.namelist()

        for file_name in file_names:
            # Извлечение содержимого файла в память
            with z.open(file_name) as f:
                GB_profile_df = pd.read_csv(f, sep=",")

                # Удаление лишних столбцов
                GB_profile_df = GB_profile_df.drop(["ID","X","Y","Distance (Segment)","Distance 3D (Segment)","Distance 3D (Total)","Slope (Degrees)","Slope (Percent)","Segment Index"], axis=1)
                
                """
                # Удаление строк через одну, пока размер не станет 50 или меньше
                while len(GB_profile_df) > 50:
                    # Получаем индексы строк, которые нужно удалить (каждый второй индекс)
                    indices_to_drop = GB_profile_df.index[1::2]
                    # Удаляем строки
                    GB_profile_df = GB_profile_df.drop(indices_to_drop)
                """
                 
                Profiles_profile = GB_profile_df
                
                Profiles_profile = Profiles_profile.rename(columns={"Elevation" : "H,m", "Distance (Total)" : "B,m"})
                Profiles_profile["N"] = ""
                Profiles_profile["L,km"] = ""
                Profiles_profile["C"] = ""
                Profiles_profile = Profiles_profile[["N", "L,km", "B,m", "H,m", "C"]]
                Profiles_profile.loc[0, "N"] = 1
                Profiles_profile.loc[0, "L,km"] = 0

                file_name = file_name.replace(".csv", '')
                Profiles_profile.to_csv(os.path.join(folder_path, f"{file_name}.txt"), sep="\t", index=False, encoding="utf-8")

    # Удаление input zip
    if os.path.exists(zip_path_input):
        os.remove(zip_path_input)
        print(f'Архив "{zip_path_input}" успешно удален.')
    
    else:
        print(f'Архив "{zip_path_input}" не найден.')
   
    # Архивируем папку с преобразованными профилями
    zip_folder(folder_path, zip_path_output)

    # Удаление папки с преобразованными профилями
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f'Папка "{folder_path}" и все ее содержимое успешно удалены.')
    
    else:
        print(f'Папка "{folder_path}" не найдена.')


if __name__  == "__main__":
    GB_to_Profiles_tranformation("chat_id", "levels", "levels/Profiles.zip", "levels/zip_path_output.zip")