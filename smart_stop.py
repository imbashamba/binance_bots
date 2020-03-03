from binance_f import RequestClient
from binance_f.model import *
from binance_f.constant.test import *
from binance_f.base.printobject import *
from datetime import datetime
from requests import ConnectionError
import time

# API ключи и параметры стопа задаются в соседнем файле b_globals
from b_globals import g_api_key, g_secret_key, g_candle_size, STOP_PRICE, AMOUNT

request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)

# Варианты свечек, которые мы умеем
candles = {
	1: CandlestickInterval.MIN1,
	3: CandlestickInterval.MIN3,
	5: CandlestickInterval.MIN5
}

CANDLE_SIZE = candles[g_candle_size]

print("======= Kline/Candlestick Data =======")

last_date = None #дата закрытия свечки, для определения наступления новой
prev_price = 0 #пред.цена
stop_type = None #тип стопа продажа/покупка. Если текущая цена первой полученной свечки выше Стоп_цены, поставится в продажу. Иначе - в покупку

while True:
	try:
		# запросим последнюю свечку с биржи
		result = request_client.get_candlestick_data(symbol="BTCUSDT", interval=CANDLE_SIZE, 
												startTime=None, endTime=None, limit=1)
		
		time.sleep(2) # получаем данные раз в 2 секунды
		res = result[0]

		if not stop_type:
			# если тип стопа не определён (первая свечка после старта проги), определим его
			first_price = float(res.close,)
			stop_type = OrderSide.BUY if STOP_PRICE > first_price else OrderSide.SELL
			print("STOP TYPE: ", stop_type)

		if not last_date:
			# запомним дату первой свечки
			last_date = res.closeTime

		elif last_date != res.closeTime:
			# если дата закрытия не совпадает с запомненной, значит у нас новая свеча! запускаем анализ
			print(datetime.fromtimestamp(int(res.closeTime)/1000))
			print('prev: ', prev_price, 'cur: ', res.close)

			if (stop_type == OrderSide.BUY and (prev_price > STOP_PRICE and float(res.close,) > STOP_PRICE)) or (stop_type==OrderSide.SELL and (prev_price < STOP_PRICE and float(res.close,) < STOP_PRICE)):
				print('placing order')
				print('AMOUNT', AMOUNT)
				try:
					result = request_client.post_order(symbol="BTCUSDT", side=stop_type, ordertype=OrderType.MARKET, quantity=AMOUNT)
					print(result)
				except Exception as e:
					# иногда ордер не срабатывает с первого раза по рандомной причине, пробуем второй раз для надёги
					print(e)
					time.sleep(5)
					print('EXCEPTION WHEN MAKING ORDER, TRY NEW ONE')
					result = request_client.post_order(symbol="BTCUSDT", side=stop_type, ordertype=OrderType.MARKET, quantity=AMOUNT)
				break
			prev_price = float(res.close)
			last_date = res.closeTime
	except ConnectionError as e:
		print(e)
		time.sleep(5)
		
print("======================================")
