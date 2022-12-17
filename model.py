# Загрузка библиотек
import datetime
import math

import numpy as np
import pandas as pd

from Take_all_stonck import connect_bd, take_all_data_by_value, \
    take_all_data_by_volume, take_all_data_by_avg, take_all_data


def get_portfolio_new(user_data):
    count_stonck = 10
    type_p = 2
    today = datetime.datetime.now()
    horizon = today - datetime.timedelta(days=30 * int(user_data[1]))

    con = connect_bd('xmas_hack')

    all_data = take_all_data(con)
    all_data['TRADEDATE'] = pd.to_datetime(all_data['TRADEDATE'])
    all_data = all_data[all_data['TRADEDATE'] > horizon]

    if type_p == 1:
        all_data_for_name_avg = take_all_data_by_avg(con)
        all_data_for_name_avg['TRADEDATE'] = pd.to_datetime(all_data_for_name_avg['TRADEDATE'])
        all_data_for_name_avg = all_data_for_name_avg[all_data_for_name_avg['TRADEDATE'] > horizon]
        add_name = all_data_for_name_avg.groupby('NAME').mean('SORT').sort_values('SORT', ascending=False).head(
            count_stonck).index.to_list()
    elif type_p == 2:
        all_data_for_name_value = take_all_data_by_value(con)
        all_data_for_name_value['TRADEDATE'] = pd.to_datetime(all_data_for_name_value['TRADEDATE'])
        all_data_for_name_value = all_data_for_name_value[all_data_for_name_value['TRADEDATE'] > horizon]
        add_name = all_data_for_name_value.groupby('NAME').mean('SORT').sort_values('SORT', ascending=False).head(
            count_stonck).index.to_list()
    elif type_p == 3:

        all_data_for_name3_volume = take_all_data_by_volume(con)
        all_data_for_name3_volume['TRADEDATE'] = pd.to_datetime(all_data_for_name3_volume['TRADEDATE'])
        all_data_for_name3_volume = all_data_for_name3_volume[all_data_for_name3_volume['TRADEDATE'] > horizon]
        add_name = all_data_for_name3_volume.groupby('NAME').mean('SORT').sort_values('SORT', ascending=False).head(
            count_stonck).index.to_list()

    all_data = all_data.set_index('TRADEDATE')[['NAME', 'CLOSE']].dropna(subset='CLOSE')
    all_data = all_data[all_data['NAME'].isin(add_name)]
    all_price = all_data[all_data.index > today - datetime.timedelta(days=2)].groupby('NAME').max()
    all_data.index = pd.to_datetime(all_data.index)

    df = pd.pivot_table(all_data, values='CLOSE', index='TRADEDATE', columns='NAME')
    df.index = pd.to_datetime(df.index)

    pers = df.pct_change().apply(lambda x: np.log(1 + x))

    cov_matrix = df.pct_change().apply(lambda x: np.log(1 + x)).cov()

    #corr_matrix = df.pct_change().apply(lambda x: np.log(1 + x)).corr()

    # Доходы по дням D (M,Y) (месяц, год)
    ind_er = df.resample('D').last().pct_change().mean()


    # Доходность портфеля
    w = [1 / len(ind_er) for x in range(1, len(ind_er) + 1)]
    port_er = (w * ind_er).sum()

    # Волатильность определяется годовым стандартным отклонением. Мы умножаем на 250, потому что в году 250 торговых дней.
    ann_sd = df.pct_change().apply(lambda x: np.log(1 + x)).std().apply(lambda x: x * np.sqrt(250))

    assets = pd.concat([ind_er, ann_sd], axis=1)
    assets.columns = ['Returns', 'Volatility']

    p_ret = []  # Определить пустой массив для доходности портфеля
    p_vol = []  # Определить пустой массив для волатильности портфеля
    p_weights = []  # Определить пустой массив для весов активов

    num_assets = len(df.columns)
    num_portfolios = 10000

    for portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights = weights / np.sum(weights)
        p_weights.append(weights)
        returns = np.dot(weights,
                         ind_er)  # Доходность - это произведение индивидуальной ожидаемой доходности актива и его весов
        p_ret.append(returns)
        var = cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()  # Portfolio Variance
        sd = np.sqrt(var)  # Ежедневное стандартное отклонение
        ann_sd = sd * np.sqrt(
            250)  # Годовое стандартное отклонение = волатильность
        p_vol.append(ann_sd)

    data = {'Returns': p_ret, 'Volatility': p_vol}

    for counter, symbol in enumerate(df.columns.tolist()):
        data[symbol] = [w[counter] for w in p_weights]

    portfolios = pd.DataFrame(data)

    # Дальше надо пройтись по границе и найти лучшие решения
    # min_vol_port = portfolios.iloc[portfolios['Volatility'].idxmin()]

    # Поиск оптимального портфеля
    rf = int(user_data[0])  # Риск
    if rf == 1:
        optimal_risky_port = portfolios.iloc[portfolios['Volatility'].idxmin()]
    elif rf == 2:
        optimal_risky_port = portfolios.iloc[((portfolios['Returns'] - 0.5) / portfolios['Volatility']).idxmin()]
    elif rf == 3:
        optimal_risky_port = portfolios.iloc[portfolios['Returns'].idxmax()]

    ans_tmp = pd.concat([optimal_risky_port[2:], all_price], axis=1)
    ans_tmp.columns = ['persent', 'prise']

    def quantity_stocks(all_sum, ans_tmp):
        answer = ''
        for i, row in ans_tmp.iterrows():
            try:
                count_stonck = math.floor(all_sum * row['persent'] / row['prise'])
            except:
                count_stonck = 0
            if count_stonck > 0:
                answer += f'{i} - {count_stonck} шт.\n'

        return answer

    answer = quantity_stocks(int(user_data[2]), ans_tmp)
    answer = f'Доходность: {optimal_risky_port[0]:.2%}\nРиски: {optimal_risky_port[1]:.2%}\n\n' + answer

    print(answer)

    return answer

if __name__ == '__main__':
    get_portfolio_new([1, 12, 100000])
