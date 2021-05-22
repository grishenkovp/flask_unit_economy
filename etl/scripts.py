# импорт библиотек
from typing import List, Tuple, Dict, Set
import pandas as pd
import sqlite3
import datetime as dt


def func_extract_transform(path: str) -> pd.DataFrame:
    """Предварительная обработка датасета"""
    # Считываем датасет
    df = pd.read_csv(path, sep=',')
    # Приводим названия столбцов датасета к нижнему регистру
    list_col = list(map(str.lower, df.columns))
    df.columns = list_col
    # Избавляемся от времени и трансформируем строку-дату в правильный формат
    df['invoicedate'] = df['invoicedate'].apply(lambda x: x.split(' ')[0])
    df['invoicedate'] = pd.to_datetime(df['invoicedate'], format='%m/%d/%Y')
    # Рассчитываем сумму покупки по каждому товару
    df['amount'] = df['quantity'] * df['unitprice']
    # Удаляем ненужные для дальнейшего анализа столбцы
    df = df.drop(['stockcode', 'description', 'quantity', 'unitprice'], axis=1)
    # Заполняем строки, где не указан номер покупателя, константой 777777
    values = {'customerid': 777777}
    df = df.fillna(value=values)
    df['customerid'] = df['customerid'].astype('int')
    # Округляем общую сумму покупки до целового числа
    df = df.round({'amount': 0})
    df['amount'] = df['amount'].astype('int')
    # Удаляем все строки, в которых есть пропуски перед группировкой
    df = df.dropna()
    # Группируем строки, чтобы прийти к детализации до уровня одного чека
    df_result = df.groupby(by=['invoiceno', 'invoicedate', 'customerid', 'country']).agg({'amount': sum}).reset_index()
    # Трансформируем даты в текст для упрощения загрузки в БД
    df_result['invoicedate'] = df_result['invoicedate'].dt.strftime('%Y-%m-%d')
    return df_result


def func_val_list(df: pd.DataFrame) -> List:
    """Трансформируем датафрейм в список списков"""
    val_list = df.values.tolist()
    return val_list


def func_sqlite_connection(con: str, records: List):
    """Создаем базу данных.  Создаем таблицу для записей фактов продаж и заполняем ее значениями из датасета"""
    sqlite_connection = None
    try:
        # Создаем соединение
        sqlite_connection = sqlite3.connect(con)
        # Создаем курсор
        cur = sqlite_connection.cursor()
        # Создаем таблицу
        cur.execute("""CREATE TABLE IF NOT EXISTS sales (
                        invoiceno TEXT NOT NULL,
                        invoicedate TEXT NOT NULL,
                        customerid INTEGER NOT NULL,
                        country TEXT NOT NULL,
                        amount INTEGER NOT NULL)""")
        # Добавляем записи
        cur.executemany("INSERT INTO sales VALUES(?,?,?,?,?)", records)
        # Сохраняем транзакцию
        sqlite_connection.commit()
        # Закрываем курсор
        cur.close()
    except sqlite3.Error as err:
        print("Ошибка выполнения запроса", err)
    finally:
        # Закрываем соединение
        if sqlite_connection is not None:
            sqlite_connection.close()
            print("Соединение закрыто!")
