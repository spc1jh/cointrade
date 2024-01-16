# cointrade

빗썸 경주마매매 

## 사전 준비

파이썬 설치
    - 최소 : 3.7 버전 이상  
    - 권장 : 3.10 버전 이상

## 설정 추가

- .env 파일 생성
```
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

## pip 인스톨

```
pip install pybithumb requests schedule numpy pandas python-dotenv

```


## 실행

```
python bithumb_racehorse.py
```
