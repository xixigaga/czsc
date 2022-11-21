# coding: utf-8
import sys
import os
sys.path.insert(0, os.path.abspath('.'))  #便于代码调试
import os
import pandas as pd
import random
from czsc.utils import echarts_plot as plot
from czsc.analyze import CZSC, RawBar
from czsc.enum import Freq
from czsc.signals.utils import get_zs_seq
from czsc.signals.bxt import check_three_bi
import QUANTAXIS as QA

cur_path = os.path.split(os.path.realpath(__file__))[0]


def test_heat_map():
    data = [{"x": "{}hour".format(i), "y": "{}day".format(j), "heat": random.randint(0, 50)}
            for i in range(24) for j in range(7)]
    x_label = ["{}hour".format(i) for i in range(24)]
    y_label = ["{}day".format(i) for i in range(7)]
    hm = plot.heat_map(data, x_label=x_label, y_label=y_label)
    file_html = 'render.html'
    hm.render(file_html)
    assert os.path.exists(file_html)
    os.remove(file_html)


def test_kline_pro():
    file_kline = os.path.join(cur_path, "data/000001.SH_D.csv")
    kline = pd.read_csv(file_kline, encoding="utf-8")
    bars = [RawBar(symbol=row['symbol'], id=i, freq=Freq.D, open=row['open'], dt=row['dt'],
                   close=row['close'], high=row['high'], low=row['low'], vol=row['vol'])
            for i, row in kline.iterrows()]
    ka = CZSC(bars)
    # ka.open_in_browser()
    zslist = get_zs_seq(ka.bi_list) #获取中枢
    temp = check_three_bi(ka.bi_list[-3:],ka.freq)
    file_html = 'czsc_render.html'
    chart = ka.to_echarts()
    chart.render(file_html)
    # assert os.path.exists(file_html)
    # os.remove(file_html)

def qaCzsc():

    te = QA.QA_fetch_stock_day_adv('000001','2022-01-01','2022-11-02').to_qfq()
    
    bars = [RawBar(symbol=row.name[1], dt=row.name[0],id=i, freq=Freq.D, open=row['open'], 
                   close=row['close'], high=row['high'], low=row['low'], vol=row['volume'],amount=row['amount'])
            for i, row in te.data.iterrows()]
    ka = CZSC(bars,use_xd=True) #获取最后
    zslist = get_zs_seq(ka.bi_list) #获取中枢 用以计算最后次级别的时间长度
    '''
    当下处于中枢最后一笔
    获取次级别中枢前一笔+中枢+最后一笔
    '''
    min60 = QA.QA_fetch_stock_min_adv('000002','2022-07-05','2022-11-01',frequence='60min').to_qfq()
    min_bars = [RawBar(symbol=row.name[1], dt=row.name[0],id=i, freq=Freq.D, open=row['open'], 
                   close=row['close'], high=row['high'], low=row['low'], vol=row['volume'],amount=row['amount'])
            for i, row in min60.data.iterrows()]
    min_ka = CZSC(min_bars)
    min_zslist = get_zs_seq(min_ka.bi_list) #获取中枢 用以计算最后次级别的时间长度
    return min_zslist

if __name__ == '__main__':
    qaCzsc()

    