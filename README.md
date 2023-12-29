# cointrade
코인 트레이딩용 

## 사전 준비

파이썬 3.7 버전 이상

### 설정 추가

1) .env 파일 생성
```
# 크롤링 설정 부분
user_agent= 'User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'

## 빗썸용
bithum_conkey = ""
bithum_seckey = ""

# 한번에 사고자 하는 코인 비용 (원단위로 입력하자)
mywallet = 50000 
# 수익률 (%)
target_price = 5 
# 손절가 (%)
stop_loss = -5

```

2) chromedriver 다운로드 

```
https://chromedriver.chromium.org/downloads
```

## pip 인스톨

```
pip install pybithumb
pip install requests
pip install schedule

```

## 

