# coding: utf-8
import sys
import warnings

sys.path.insert(0, '.')
sys.path.insert(0, '..')

import os
import pandas as pd
import random
from czsc.utils import echarts_plot as plot
from czsc.analyze import KlineAnalyze
from czsc.signals import find_zs,single_Check
import QUANTAXIS as QA

cur_path = os.path.split(os.path.realpath(__file__))[0]

def test_heat_map():
    data = [{"x": "{}hour".format(i), "y": "{}day".format(j), "heat": random.randint(0, 50)}
            for i in range(24) for j in range(7)]
    x_label = ["{}hour".format(i) for i in range(24)]
    y_label = ["{}day".format(i) for i in range(7)]
    hm = plot.heat_map(data, x_label=x_label, y_label=y_label)
    hm.render()


def test_kline_pro():
    file_kline = os.path.join(cur_path, "data/000001.SH_D.csv")
    kline = pd.read_csv(file_kline, encoding="utf-8")
    bars = kline.to_dict("records")
    ka = KlineAnalyze(bars)

    bs = []
    for x in ka.xd_list:
        if x['fx_mark'] == 'd':
            mark = "buy"
        else:
            mark = "sell"
        bs.append({"dt": x['dt'], "mark": mark, mark: x['xd']})

    chart = plot.kline_pro(ka.kline_raw, fx=ka.fx_list, bi=ka.bi_list, xd=ka.xd_list, bs=bs)
    chart.render()

def qaCzsc():
    te = QA.QA_fetch_stock_day_adv('000001','2022-01-01','2022-10-30').to_qfq()
    bars = te.data.round(2).reset_index()
    bars.rename(columns={'code': 'symbol', 'date': 'dt'}, inplace=True)

    ka = KlineAnalyze(bars,)
    zslist = find_zs(ka.bi_list)
    xd_zslist2 = single_Check(bars,zslist) #找出最近
    # 日线出现背驰
    # 查看分钟线是否也背驰并且结束
    '''
    当下处于中枢最后一笔
    获取次级别中枢前一笔+中枢+最后一笔
    '''
    min60 = QA.QA_fetch_stock_min_adv('000001','2022-06-05','2022-11-01',frequence='60min').to_qfq()
    min_bars = min60.data.round(2).reset_index()
    min_bars.rename(columns={'code': 'symbol', 'datetime': 'dt'}, inplace=True)

    min_ka = KlineAnalyze(min_bars,use_xd=True,) # 次级别需要合并笔
    bi_zslist = find_zs(min_ka.bi_list) #获取中枢 用以计算最后次级别的时间长度 看局部中枢背离也可以
    xd_zslist2 = single_Check(min_bars,bi_zslist)
    return bi_zslist

if __name__ == '__main__':
    qaCzsc()