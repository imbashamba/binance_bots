from binance_f import RequestClient
from binance_f.model import *
from binance_f.constant.test import *
from binance_f.base.printobject import *
from datetime import datetime
from requests import ConnectionError
import time
from b_globals import g_api_key, g_secret_key, g_candle_size, STOP_PRICE, AMOUNT

request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)

# STOP_PRICE = 10253
# CANDLE_SIZE = CandlestickInterval.MIN1
# AMOUNT=6

candles = {
	1: CandlestickInterval.MIN1,
	3: CandlestickInterval.MIN3,
	5: CandlestickInterval.MIN5
}

CANDLE_SIZE = candles[g_candle_size]

RECV_WINDOW=6000000

print("======= Kline/Candlestick Data =======")
last_date = None
prev_price = 0
stop_type = None
while True:
	try:
		result = request_client.get_candlestick_data(symbol="BTCUSDT", interval=CANDLE_SIZE, 
												startTime=None, endTime=None, limit=1)
		time.sleep(2)
		res = result[0]
		if not stop_type:
			first_price = float(res.close,)
			stop_type = OrderSide.BUY if STOP_PRICE > first_price else OrderSide.SELL
			print("STOP TYPE: ", stop_type)
		if not last_date:
			last_date = res.closeTime
		elif last_date != res.closeTime:
			print(datetime.fromtimestamp(int(res.closeTime)/1000))
			print('prev: ', prev_price, 'cur: ', res.close)

			if (stop_type == OrderSide.BUY and (prev_price > STOP_PRICE and float(res.close,) > STOP_PRICE)) or (stop_type==OrderSide.SELL and (prev_price < STOP_PRICE and float(res.close,) < STOP_PRICE)):
				print('placing order')
				result = request_client.post_order(symbol="BTCUSDT", side=stop_type, ordertype=OrderType.MARKET, quantity=AMOUNT)
				print(result)
				break
			prev_price = float(res.close)
			last_date = res.closeTime
	except ConnectionError as e:
		print(e)
		time.sleep(5)
		
		
# PrintMix.print_data(result)
# for res in result:
# 	print(datetime.fromtimestamp(int(res.closeTime)/1000))
# 	print(res.closeTime, res.close)
print("======================================")
