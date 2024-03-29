import time
import datetime
import requests
import os
from dotenv import load_dotenv

import json
import pandas as pd
import numpy as np
import schedule

from pybithumb import Bithumb


# .env 로드하기 위함
load_dotenv() 

user_agent = os.environ.get('user_agent')
header = {'User-Agent':user_agent}
chromedriver_path='./files/chromedriver'

url = 'https://api.bithumb.com/public/ticker/ALL_KRW'


# bithumb 
bithum_conkey = os.environ.get('bithum_conkey')
bithum_seckey = os.environ.get('bithum_seckey')

# 빗썸 로그인
bithumb = Bithumb(bithum_conkey, bithum_seckey)

# 한번에 사고자 하는 코인 비용 (원단위로 입력하자)
mywallet = os.environ.get('mywallet') 
# 수익률 (%)
target_price = os.environ.get('target_price') 
# 손절가 (%)
stop_loss = os.environ.get('stop_loss') 
# 경주마 매매 시작 시간
race_start_time = os.environ.get('race_start_time') 

# UNIX 타임스탬프를 UTC 표준시로 변환하는 함수
def convert_unix_to_utc(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time // 1000)
   
def f_getdata_request():

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    json_data = response.json()

    coin_data = []

    try:
        for coin, details in json_data['data'].items():

            if type(details) != dict:
                print(convert_unix_to_utc(int(details)))

                continue
            coin_name = coin
            # print(details)
            opening_price = details.get("opening_price")
            closing_price = details.get("closing_price")
        #     # print(coin)
            if opening_price is not None and closing_price is not None:
                opening_price = float(opening_price)
                closing_price = float(closing_price)
                coin_data.append({"coin_name": coin_name, "opening_price": opening_price, "closing_price": closing_price})
            else:
                print(f"Missing price information for {coin_name}")
        
        df = pd.DataFrame(coin_data)
        
        return df      

    except json.JSONDecodeError as e:
        print("JSON 데이터가 올바르지 않습니다:", e)
    except Exception as e:
        print("예상치 못한 오류가 발생했습니다:", e)


# 위에서 추출한 dataframe을 가공하여 top coin을 추출
def f_getTopCoin(df):
    df['price_diff'] = df['closing_price'] - df['opening_price']
    df['price_diff_percent'] = df['price_diff'] / df['opening_price'] * 100
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_sorted = df.sort_values(by="price_diff_percent", ascending=False)
    print(df_sorted.head())
    return df_sorted.iloc[0]['coin_name']

# 코인 시장가 매수 
def f_buycoin(coin):
    # 코인 현재가 확인
    current_price = Bithumb.get_current_price(coin)
    # 내가 사고자 하는 금액을 코인 금액으로 나눈 금액 = 즉 코인 개수가 나옴
    current_coin_count = float(mywallet) / float(current_price)

    print("매수 코인금액: "+ str(current_price) +",  코인개수 : "+ str(current_coin_count))
    desc = bithumb.buy_market_order(coin,current_coin_count)
    # print(desc)

    return desc

MAX_RETRY = 3  # 최대 재시도 횟수
def get_last_order_price(desc):
    retry_count = 0

    while retry_count < MAX_RETRY:
        try:
            last_order_status = bithumb.get_order_completed(desc)
            last_order_price = last_order_status['data']['contract'][0]['price']
            return last_order_price  # 값을 얻으면 반복문 탈출

        except Exception as e:
            print(f"Error occurred: {e}")
            retry_count += 1
            print(f"Retrying... (Retry count: {retry_count})")

    print("Failed to retrieve last order price after multiple attempts.")
    return None  # 최대 재시도 횟수를 초과한 경우 None 반환 혹은 다른 에러 처리 방법 선택 가능


# 목표가 도달하는지 확인하는 함수
def f_check_price(coin, last_order_price, topcoin_openprice):
    my_balance = bithumb.get_balance(coin)
    current_price = bithumb.get_current_price(coin)
    total_unit = my_balance[0]
    
    # 현재가와 내 매수가 비교
    diff_price = (float(current_price)  - float(last_order_price)) / float(last_order_price) * 100
    print(diff_price)

    ### 매도 조건
    # 목표가 이상일때 매도
    
    if float(diff_price) >= float(target_price):
        print("이익 매도 시작(diff_price): "+ str(diff_price))
        f_sellcoin(coin, total_unit)
        return False
    # 손절 % 에 도달하면서 시초가가 깨졌을때 매도를 한다.
    elif (float(diff_price) <= float(stop_loss) and float(current_price) <= float(topcoin_openprice)) :
        print("손절 매도 시작(diff_price): "+ str(diff_price))
        f_sellcoin(coin, total_unit)
        return False
    else:
        return True
    

def f_sellcoin(coin, total_unit):
    desc = bithumb.sell_market_order(order_currency=coin, unit=float(total_unit), payment_currency="KRW")
    print("매도 : " +coin+ " " + str(total_unit))
    print(desc)

has_run = False  # 함수 실행 여부를 나타내는 전역 변수

def f_start():
    global has_run
    print("start: "+ str(datetime.datetime.now().time()))
    has_run = True

def start():
    
    print("coin trade program start & now: "+ str(datetime.datetime.now().time()))

    # 특정 시간에 실행되게 함
    schedule.every().day.at(race_start_time).do(f_start) # KST 기준
    
    while True:
        schedule.run_pending()
        if has_run:
            break
        time.sleep(1)

def main():
    # 코인 데이터 전체 확인
    df = f_getdata_request()

    # top coin 추출
    topcoin = f_getTopCoin(df)
    print(topcoin)
    
    # topcoin의 opening price
    topcoin_openprice = df.loc[df["coin_name"] == topcoin, 'opening_price'].values[0]

    # 시장가매수
    desc = f_buycoin(topcoin)
    print(desc)

    time.sleep(2)
    # 매수했던 내역에 대해서 확인하여 매수 가격 확인
    result = bithumb.user_transactions(0,20,1,topcoin)
    # print(result["data"][0]["price"])
    last_order_price = result["data"][0]["price"]
    print("매수가: ", last_order_price)

    # 매도 될때까지 수익률 조회하다가 원하는 수익률이 되면 전량 매도
    while True:
        check_status = f_check_price(topcoin, last_order_price, topcoin_openprice)
        time.sleep(1)
        if check_status == False:
            break

    

if __name__ == '__main__':
    
    start()
    main()
    
