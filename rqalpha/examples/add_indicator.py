from rqalpha.api import *

# Last Change:  2018-01-10 14:01:46
import talib


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = "000001.XSHE"
    context.TIME_PERIOD = 14

    # get_bars_all : 获得一个股票所有的数据，而不是像history_bars一样只是获得指定数量的数据。
    _prices= get_bars_all(context.s1, '1d', "close")
    _rsi_data = talib.RSI(_prices, timeperiod=context.TIME_PERIOD)
    # add_indicator : 将指标保存，以便在策略中直接调用，不用再计算一遍。
    add_indicator(context.s1, '1d', "rsi", _rsi_data)


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    # import datetime
    # _data = get_bars_all(context.s1, dt=datetime.datetime.now())
    # logger.info("length:" + str(len(_data)))
    _rsi = history_bars(context.s1, 1, '1d', 'rsi')
    logger.info(_rsi)

