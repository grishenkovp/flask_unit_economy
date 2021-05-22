# импорт библиотек
import os
import yaml
from etl import scripts as etl

# Подключаемся к файлу с настройками проекта
with open('settings.yaml') as f:
    settings = yaml.safe_load(f)

# Константы
path_data = settings['PATH']['PATH_DATA']
path_database = settings['PATH']['PATH_DATABASE']
name_database = settings['NAME']['NAME_DATABASE']
name_data = settings['NAME']['NAME_DATA']

# Считываем первичный датасет и трансформируем его. Итоговый результат записываем во временную таблицу
tbl = etl.func_extract_transform(os.path.join(path_data, name_data))

# Датафрейм переводим в список
sales_records = etl.func_val_list(tbl)

# Создаем базу данных и записываем в нее значения
etl.func_sqlite_connection(os.path.join(path_database, name_database), sales_records)
