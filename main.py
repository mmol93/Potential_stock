from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import os
import shutil
import time
import get_sotckCode
import check_Excell


print("종목명 / 현재가 / 이평5일과 차이  / 외국인 연속 / 기관 연속 / 5일간 주가 변봐량 / CCI / RSI")

### 종목들 각종 계산 및 정보 스크래핑하기

stock_list = check_Excell.call_excell_stock()
stockCode_list = get_sotckCode.code_search()

path = "C:/selenium/chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")

driver = webdriver.Chrome("C:/selenium/chromedriver", options=options)
url_1 = "https://finance.naver.com/item/sise.nhn?code="     # 네이버 주식_ 개별종목 앞 주소(시세부분)

## 각 종목들 사이트(네이버)에 접속하여 정보 가져오기
i = 0

# 종목 1개씩 실시(test : 1로 설정하여 종목 1개에 대해서만 실시하게 하기), 나중에느 int(price_list[0])로 변경하기
while i < 1:
    url = url_1 + stockCode_list[i]
    driver.get(url)
    driver.switch_to.frame("day")   # iframe 부분의 데이터 열기
    price_list = []

    # 5일간의 시세 가져오기 - C
    for j in range(3, 8):
        xpath = "/html/body/table[1]/tbody/tr[" + str(j) + "]/td[2]"
        price_item_comma = driver.find_element_by_xpath(xpath).text

        price_item = price_item_comma.replace(",", "")  # 시세에 ,(콤마)가 있기 때문에 이를 제거해야 계산 가능
        price_list.append(price_item)

    # 5일 이동평균 계산(// : 소수점 버리는 나눗셈) - C
    avg_five = (int(price_list[0]) + int(price_list[1]) + int(price_list[2])
                + int(price_list[3]) + int(price_list[4])) // 5

    # 현재가와 5일 이동평균 얼마나 차이 나는지 계산(%) - C
    present_diff_avgFive = round((int(price_list[0]) - avg_five) / avg_five * 100, 2)

    i += 1

## 외국인 기관 수급 정보는 url이 다르기 때문에 다시 접속해야한다

driver.quit()