import datetime
import requests
import apimoex
import pandas as pd
import sqlite3 as sl

db_path = 'stonck_db'

#
def create_table_stonk(con):
    sql_create_table_stonck = f"""
        CREATE TABLE STONCK (
            index_st INTEGER,
            NAME TEXT,
            BOARDID TEXT,
            TRADEDATE DATA,
            CLOSE DECIMAL,
            VOLUME INTEGER,
            VALUE INTEGER
        );
    """
    with con:
        con.execute(sql_create_table_stonck)

def create_table_persons(con):
    sql_create_table_person = f"""
        CREATE TABLE PERSONS (
            index_ps INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            tg_id TEXT,
            portfolio NTEXT
        );
    """
    with con:
        con.execute(sql_create_table_person)


def connect_bd(name):
    con = sl.connect(f'{db_path}\{name}.db')
    return con


def insert_data_persons(data):
    con = connect_bd('xmas_hack')
    sql_insert_person = """
    INSERT INTO PERSONS (tg_id, portfolio) values (?, ?)
    """
    with con:
        con.executemany(sql_insert_person, data)

def take_user_portfolio(tg_id):
    con = connect_bd('xmas_hack')
    persons_portfolio = pd.read_sql(f'SELECT portfolio FROM PERSONS WHERE tg_id = {tg_id}', con)
    return persons_portfolio

def take_all_data(con):
    all_persons_df = pd.read_sql('SELECT * FROM STONCK', con)
    return all_persons_df

def take_all_data_by_value(con):
    all_persons_df = pd.read_sql('SELECT TRADEDATE, NAME, AVG(VALUE) as SORT FROM STONCK GROUP BY NAME, TRADEDATE', con)
    return all_persons_df

def take_all_data_by_volume(con):
    all_persons_df = pd.read_sql('SELECT TRADEDATE, NAME, AVG(VOLUME) as SORT FROM STONCK GROUP BY NAME, TRADEDATE', con)
    return all_persons_df


def take_all_data_by_avg(con):
    all_persons_df = pd.read_sql(
        """WITH TMP AS 
        (SELECT 
            NAME,
            CLOSE,
            TRADEDATE,
            LAG(CLOSE) OVER (PARTITION BY NAME, TRADEDATE ORDER BY TRADEDATE) as CLOSE2 
            FROM STONCK 
            WHERE CLOSE > 0) 
        SELECT 
            TRADEDATE,
            NAME, 
            AVG(LOG(1 + CLOSE - CLOSE2)) AS SORT
        FROM TMP 
        GROUP BY NAME, TRADEDATE
        """,
        con)
    return all_persons_df


def take_all_stonck_name_MOEX():
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"
    params = {
        "iss.only": "securities",
        "securities.columns": "SECID",
        "securities.market": "shares"
    }

    response = requests.get(url, params=params)

    all_securities = []
    for security in response.json()["securities"]["data"]:
        all_securities.append(security[0])

    return all_securities


def take_all_stonck_data(all_securities, date_start):
    status = 0
    with requests.Session() as session:
        for securities in all_securities:
            data = apimoex.get_board_history(session, securities, start=date_start)
            if data:
                df = pd.DataFrame(data)
                df.insert(loc=0, column="NAME", value=securities)
                if status == 0:
                    all_df = df
                    status = 1
                else:
                    all_df = pd.concat([all_df, df])
            # df.set_index('TRADEDATE', inplace=True)

    return all_df.reset_index(drop=True)


if __name__ == '__main__':
    con = connect_bd('xmas_hack')
    create_table_stonk(con)
    create_table_persons(con)
    all_securities = take_all_stonck_name_MOEX()
    date_start = '2020-01-01'
    all_data = take_all_stonck_data(all_securities, date_start)
    all_data.index.names = ['index_st']
    all_data.to_sql('STONCK', con=con, if_exists='append')

