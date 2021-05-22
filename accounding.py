import pandas as pd
import numpy as np
import sqlite3
import os
from sql import scripts
import yaml

# # опции отображения
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.expand_frame_repr', False)

# Подключаемся к файлу с настройками проекта
with open('settings.yaml') as f:
    settings = yaml.safe_load(f)

# Константы
path_data = settings['PATH']['PATH_DATA']
path_database = settings['PATH']['PATH_DATABASE']
name_database = settings['NAME']['NAME_DATABASE']
name_data = settings['NAME']['NAME_DATA']

# Открываем соединение
sqlite_connection = sqlite3.connect(os.path.join(path_database, name_database))
cur = sqlite_connection.cursor()


def select(sql) -> pd.DataFrame:
    """Запрос к БД"""
    return pd.read_sql(sql, sqlite_connection)


# Запросы к БД
tbl_sales_group_total = select(scripts.sales_group)
tbl_sales_metrics_total = select(scripts.sales_metrics)
tbl_crr_churn_rate_total = select(scripts.crr_churn_rate)


def tbl_pivot(values: str,
              df: pd.DataFrame=tbl_sales_group_total,
              index: str ='month_cohort',
              columns: str ='month_sale') -> pd.DataFrame:
    """Вспомогательная страница для построения сводной"""
    columns_list = []
    index_list = []
    columns_list.append(columns)
    index_list.append(index)
    df_pivot = pd.pivot_table(df,
                              values=values,
                              index=index,
                              columns=columns_list,
                              aggfunc=np.sum,
                              fill_value='')
    df_pivot = df_pivot.\
                        reset_index().\
                        rename_axis(None, axis=1).\
                        set_index(index_list)
    return df_pivot


def tbl_revenue() -> pd.DataFrame:
    """Сводная таблица по продажам в разрезе когорт в абсолютном выражении"""
    return tbl_pivot('revenue')

def tbl_revenue_percent() -> pd.DataFrame:
    """Сводная таблица по продажам в разрезе когорт в относительном выражении"""
    return tbl_pivot('percent_revenue')

def tbl_count_customer() -> pd.DataFrame:
    """Сводная таблица по количеству клиентов в разрезе когорт в абсолютном выражении"""
    return tbl_pivot('count_customer')

def tbl_percent_count_customer() -> pd.DataFrame:
    """Сводная таблица по продажам в разрезе когорт в относительном выражении"""
    return tbl_pivot('percent_count_customer')


def tbl_sales_metrics() -> pd.DataFrame:
    """Сводная таблица с основными метриками"""
    df_sales_metrics = tbl_sales_metrics_total.set_index('month_sale')
    return df_sales_metrics


def tbl_crr_churn_rate()-> pd.DataFrame:
    """Сводная таблица по уровню удержания и оттока клиентов"""
    df_crr_churn_rate = tbl_crr_churn_rate_total.set_index('month_sale')
    return df_crr_churn_rate
