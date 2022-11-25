# coding: utf-8
import sys
import warnings

sys.path.insert(0, '.')
sys.path.insert(0, '..')
import talib
import os
import pandas as pd
import numpy as np
import random
from czsc.utils import echarts_plot as plot
from czsc.utils.plot import ka_to_image2
from czsc.analyze import KlineAnalyze
from czsc.signals import find_zs,single_Check
import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QADate_trade import (
    QA_util_get_pre_trade_date,
    QA_util_get_real_date,
    trade_date_sse
) 

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

def checkType():
    '''
    根据近1年数据的2/3笔分型结果
    确定当前形态
            形态       背驰类型
    返回有： aAbBc   b/c  a/bc   A/B
            aAb     ab
            abc     ac
    '''
    return

def zs2ListPic(zslist,kbars):
    '''
    将多个中枢转成list
    '''
    z1=np.zeros(len(kbars))
    z2=np.zeros(len(kbars))
    for j in zslist: 
        y1 = []
        y2 = []
        if not j['end_point']:
            for i in kbars.dt:
                if j['start_point']['dt']< i:
                    y1.append(j['ZD'])
                    y2.append(j['ZG'])
                else:
                    y1.append(0)
                    y2.append(0)
        else:
            for i in kbars.dt:
                if j['start_point']['dt']< i <j['end_point']['dt']:
                    y1.append(j['ZD'])
                    y2.append(j['ZG'])
                else:
                    y1.append(0)
                    y2.append(0)
        z1+=y1
        z2+=y2
    z1 = np.where(z1==0,np.nan,z1)
    z2 = np.where(z2==0,np.nan,z2)
    return [z1,z2]

def qaCzsc():
    end_eDate = '2022-11-03'
    end_sDate = '2022-09-01'
    end_sDate = '2022-10-12'
    code='000010'

    start_date = QA_util_get_pre_trade_date(end_sDate,250) #近一年的数据
    start_index = trade_date_sse.index(end_sDate)
    end_index = trade_date_sse.index(end_eDate,1)
    te = QA.QA_fetch_stock_day_adv(code,start_date,end_eDate).to_qfq()
    testData = te.data.round(2)
    for i in range(start_index,end_index):
        tempData = testData[testData.index.get_level_values(0)<=trade_date_sse[i]]
        bars = tempData.reset_index()
        bars.rename(columns={'code': 'symbol', 'date': 'dt','volume':'vol'}, inplace=True)
        ka = KlineAnalyze(bars,)
        zslist = find_zs(ka.bi_list)
        if ka.bi_list[-1]['fx_mark']=='d' and str(ka.bi_list[-1]['end_dt'])[:10]==trade_date_sse[i]: #大趋势刚出现底分型，
            # todo 当前出现背驰（多种处理逻辑，1、aAbBc 2、aAb  3、abc）
            # 第一买点 第二买点 第三买卖点逻辑处理
            # 根据背离段进次级别验证是否也出现背驰现象
            print(trade_date_sse[i])
            zsPic2 = zs2ListPic(zslist,bars)
            ka_to_image2(ka,'d:\\'+code+str(trade_date_sse[i])[5:10]+'.jpg',zs= zsPic2)

            min60 = QA.QA_fetch_stock_min_adv(code,
                        str(ka.bi_list[-4]['dt'])[:10], # str(ka.bi_list[-2]['dt'])[:10],
                        str(ka.bi_list[-1]['dt'])[:10],frequence='30min').to_qfq()
            #待添加
            num = len(min60[min60.index.get_level_values(0)>ka.bi_list[-2]['dt']])+1
            # 增加数量
            #  macd将背驰数据绘制到图中
            min_bars = min60.data.round(2).reset_index()
            min_bars.rename(columns={'code': 'symbol', 'datetime': 'dt','volume':'vol'}, inplace=True)
            diff, dea, macd = talib.MACD(min60['close'], fastperiod=12, slowperiod=26, signalperiod=9)

            min_ka = KlineAnalyze(min_bars,use_xd=False,) # 次级别需要合并笔
            bi_zslist = find_zs(min_ka.bi_list) #获取中枢 用以计算最后次级别的时间长度 看局部中枢背离也可以
            # xd_zslist2 = single_Check(min_bars,bi_zslist)
            bi_zsPic2 = zs2ListPic(bi_zslist,min_bars)
            ka_to_image2(min_ka,'d:\\'+code+str(trade_date_sse[i])[5:10]+'min.jpg',zs= bi_zsPic2,macd=macd,max_k_count=num)
            # exit()
        # xd_zslist2 = single_Check(bars,zslist) #找出最近
        # 1、当前出现低分型
        # 2、分型之后
    '''
    1、确定是否出现日分型
    2、如果出现日分型后,验证是否到底,通过区间套方法:验证次级别是否出现背驰
    3、次级别背驰的多种验证方法
    '''
    # te = QA.QA_fetch_stock_day_adv(code,'2022-01-01',end_eDate).to_qfq()
    # bars = te.data.round(2).reset_index()
    # bars.rename(columns={'code': 'symbol', 'date': 'dt'}, inplace=True)
    # ka = KlineAnalyze(bars,)
    # zslist = find_zs(ka.bi_list)

    # if ka.bi_list[-1]['fx_mark']=='d' and str(ka.bi_list[-1]['end_dt'])[:10]==end_sDate: #大趋势刚出现底分型，
    #     # todo 当前出现背驰（多种处理逻辑，1、aAbBc 2、aAb  3、abc）
    #     # 第一买点 第二买点 第三买卖点逻辑处理
    #     # 根据背离段进次级别验证是否也出现背驰现象
    #     print(end_eDate)
    # xd_zslist2 = single_Check(bars,zslist) #找出最近
    # # 日线出现背驰
    # # 查看分钟线是否也背驰并且结束
    # '''
    # 当下处于中枢最后一笔
    # 获取次级别中枢前一笔+中枢+最后一笔
    # f=open("d:\\30bi.txt","w")
    # f.write(str(min_ka.bi_list))
    # f.close()
    # '''
    # min60 = QA.QA_fetch_stock_min_adv(code,'2022-09-15','2022-11-04',frequence='30min').to_qfq()
    # min_bars = min60.data.round(2).reset_index()
    # min_bars.rename(columns={'code': 'symbol', 'datetime': 'dt'}, inplace=True)

    # min_ka = KlineAnalyze(min_bars,use_xd=False,) # 次级别需要合并笔
    # bi_zslist = find_zs(min_ka.bi_list) #获取中枢 用以计算最后次级别的时间长度 看局部中枢背离也可以
    # xd_zslist2 = single_Check(min_bars,bi_zslist)
    return bi_zslist

if __name__ == '__main__':
    qaCzsc()