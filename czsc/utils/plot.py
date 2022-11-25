# coding: utf-8

import pandas as pd
import mplfinance as mpf
import matplotlib as mpl
import matplotlib.pyplot as plt
from .echarts_plot import kline_pro


def ka_to_image(ka, file_image, mav=(5, 20, 120, 250), max_k_count=1000, dpi=50):
    """绘制 ka，保存到 file_image"""
    df = ka.to_df(use_macd=True, ma_params=(5, 20,), max_count=max_k_count)
    df.rename({"open": "Open", "close": "Close", "high": "High",
               "low": "Low", "vol": "Volume"}, axis=1, inplace=True)
    df.index = pd.to_datetime(df['dt'])
    df = df.tail(max_k_count)
    kwargs = dict(type='candle', mav=mav, volume=True)

    bi_xd = [
        [(x['dt'], x['bi']) for _, x in df.iterrows() if x['bi'] > 0],
        # [(x['dt'], x['xd']) for _, x in df.iterrows() if x['xd'] > 0]
    ]

    mc = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='i',
        wick='i',
        volume='in',
        inherit=True)

    s = mpf.make_mpf_style(
        gridaxis='both',
        gridstyle='-.',
        y_on_right=False,
        marketcolors=mc)

    mpl.rcParams['font.sans-serif'] = ['KaiTi']
    mpl.rcParams['font.serif'] = ['KaiTi']
    mpl.rcParams['font.size'] = 48
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['lines.linewidth'] = 1.0

    title = '%s@%s（%s - %s）' % (ka.symbol, ka.name, df.index[0].__str__(), df.index[-1].__str__())
    fig, axes = mpf.plot(df, columns=['Open', 'High', 'Low', 'Close', 'Volume'], style=s,
                         title=title, ylabel='K线', ylabel_lower='成交量', **kwargs,
                         alines=dict(alines=bi_xd, colors=['r', 'g'], linewidths=8, alpha=0.35),
                         returnfig=True)

    w = len(df) * 0.15
    fig.set_size_inches(w, 30)
    ax = plt.gca()
    ax.set_xbound(-1, len(df) + 1)
    fig.savefig(fname=file_image, dpi=dpi, bbox_inches='tight')
    plt.close()

def ka_to_image2(ka, file_image, zs=None, macd=None,max_k_count=1000,
            mav=(5, 20),  dpi=70):
    """绘制 ka，保存到 file_image"""
    df = ka.to_df(use_macd=True, ma_params=(5, 20,), max_count=max_k_count)
    df.rename({"open": "Open", "close": "Close", "high": "High",
               "low": "Low", "vol": "Volume"}, axis=1, inplace=True)
    df.index = pd.to_datetime(df['dt'])
    df = df.tail(max_k_count)
    
    kwargs = dict(type='candle', mav=mav, volume=False,main_panel=0,)

    bi_xd = [
        [(x['dt'], x['bi']) for _, x in df.iterrows() if x['bi'] > 0],
    ]

    mc = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='i',
        wick='i',
        volume='in',
        inherit=True)

    s = mpf.make_mpf_style(
        gridaxis='both',
        gridstyle='-.',
        y_on_right=False,
        marketcolors=mc)
    if macd is not None:
        macd = macd[-max_k_count:]
        add_plot=[
            # mpf.make_addplot(macd,type='scatter',markersize=100,panel=1,marker='^',color='r',secondary_y=False),#黑马底
            # mpf.make_addplot(macd,panel=1,color='b',type='bar',secondary_y=True,alpha=0.9), #测试买新号
            mpf.make_addplot(macd,panel=1,color='g',secondary_y=False,alpha=0.9),
        ]
    mpl.rcParams['font.sans-serif'] = ['KaiTi']
    mpl.rcParams['font.serif'] = ['KaiTi']
    mpl.rcParams['font.size'] = 48
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['lines.linewidth'] = 1.0

    title = '%s（%s - %s）' % (ka.symbol, df.index[0].__str__(), df.index[-1].__str__())
    if macd is not None:
        fig, axes = mpf.plot(df, 
                        addplot=add_plot,
                        fill_between=dict(y1=zs[0][-max_k_count:],y2=zs[1][-max_k_count:] ,alpha=0.5,color='g'),
                        # fill_between=dict(y1=y1values,y2=y2value,where=where_values,alpha=0.5,color='g')
                        columns=['Open', 'High', 'Low', 'Close', 'Volume'], style=s,
                         title=title, ylabel='K线', ylabel_lower='成交量', **kwargs,
                         alines=dict(alines=bi_xd, colors=['r', 'g'], linewidths=2, alpha=0.35),
                         returnfig=True,
                         )
    else:
        fig, axes = mpf.plot(df, 
                        fill_between=dict(y1=zs[0][-max_k_count:],y2=zs[1][-max_k_count:] ,alpha=0.5,color='g'),
                        # fill_between=dict(y1=y1values,y2=y2value,where=where_values,alpha=0.5,color='g')
                        columns=['Open', 'High', 'Low', 'Close', 'Volume'], style=s,
                         title=title, ylabel='K线', ylabel_lower='成交量', **kwargs,
                         alines=dict(alines=bi_xd, colors=['r', 'g'], linewidths=2, alpha=0.35),
                         returnfig=True,
                         )

    w = len(df) * 0.15
    fig.set_size_inches(w, 30)
    ax = plt.gca()
    ax.set_xbound(-1, len(df) + 1)
    # plt.show()
    fig.savefig(fname=file_image, dpi=dpi, bbox_inches='tight')
    

def ka_to_echarts(ka, width: str = "1500px", height: str = '800px'):
    """用 pyecharts 绘制分析结果

    :param ka: KlineAnalyze
    :param width: str
    :param height: str
    :return:
    """
    symbol = ka.kline_raw[0]['symbol']
    title = "{} - {}".format(symbol, ka.name)
    chart = kline_pro(ka.kline_raw, fx=ka.fx_list, title=title,
                      bi=ka.bi_list, xd=ka.xd_list, width=width, height=height)
    return chart
