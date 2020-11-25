from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import os
import shutil
import time
import get_sotckCode
import check_Excell


print("종목명 / 현재가 / 이평5일과 차이  5일간 주가 변봐량 / CCI / MACD / 외국인 연속 / 기관 연속")

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
    price_list = []
    # 똑같은 iframe이 2개 있어서
    iframes = driver.find_elements_by_tag_name("iframe")

    driver.switch_to.frame(iframes[8])

    # 10일간의 시세 가져오기 - C
    # 즉, price_list 에는 10일치의 시세가 들어있음
    for j in range(3, 16):
        # 5일을 분기로 나뉘어져있기 때문에 조건으로 xpath 분기를 나누어줘야함
        if 3 <= j <= 7 or 11 <= j <= 15:
            xpath = "/html/body/table[1]/tbody/tr[" + str(j) + "]/td[2]"
            price_item_comma = driver.find_element_by_xpath(xpath).text

            price_item = price_item_comma.replace(",", "")  # 시세에 ,(콤마)가 있기 때문에 이를 제거해야 계산 가능
            price_list.append(price_item)
    # 5일 이동평균 계산(// : 소수점 버리는 나눗셈) - C
    avg_five = (int(price_list[0]) + int(price_list[1]) + int(price_list[2])
                + int(price_list[3]) + int(price_list[4])) // 5

    # 현재가와 5일 이동평균 얼마나 차이 나는지 계산(%) - C
    present_diff_avgFive = round((int(price_list[0]) - avg_five) / avg_five * 100, 2)

    # 최근 5일간 변화가 3%를 넘은적이 있는지 확인한다
    five_change_counter_plus = 0
    five_change_counter_minus = 0

    for j in range(0, 4):
        five_change_rate = round((int(price_list[0]) - int(price_list[j])) / int(price_list[j]), 2)
        # 현재가 기준 최근 5일간 시세에서 3%이상 변동이 있었는지 판단한다
        if five_change_rate >= 3:
            five_change_counter_plus += 1
        elif five_change_rate <= -3:
            five_change_counter_minus += 1

    # CCI 계산(10일치만 계산한다)
    # CCI 계산식은 "참고서" 확인
    # 시세에서 각 일자별 고가, 저가 확인이 필요하다
    high_price_list = []
    low_price_list = []

    # 고가 10일치 가져오기
    for j in range(3, 16):
        # 5일을 분기로 나뉘어져있기 때문에 조건으로 xpath 분기를 나누어줘야함
        if 3 <= j <= 7 or 11 <= j <= 15:
            xpath = "/html/body/table[1]/tbody/tr[" + str(j) + "]/td[5]"
            price_item_comma = driver.find_element_by_xpath(xpath).text

            high_price_item = price_item_comma.replace(",", "")  # 시세에 ,(콤마)가 있기 때문에 이를 제거해야 계산 가능
            high_price_list.append(high_price_item)

    # 저가 10일치 가져오기
    for j in range(3, 16):
        # 5일을 분기로 나뉘어져있기 때문에 조건으로 xpath 분기를 나누어줘야함
        if 3 <= j <= 7 or 11 <= j <= 15:
            xpath = "/html/body/table[1]/tbody/tr[" + str(j) + "]/td[6]"
            price_item_comma = driver.find_element_by_xpath(xpath).text

            low_price_item = price_item_comma.replace(",", "")  # 시세에 ,(콤마)가 있기 때문에 이를 제거해야 계산 가능
            low_price_list.append(low_price_item)

    # MP 계산
    MP = (int(price_list[0]) + int(high_price_list[0]) + int(low_price_list[0])) // 3

    # MAMP 계산
    MAMP_list = []
    for j in range(0, 10):
        MAMP = (int(price_list[j]) + int(high_price_list[j]) + int(low_price_list[j])) // 3
        MAMP_list.append(MAMP)
    # 10일치 데이터니 이평은 모든 요소 합에 나누기 10
    MAMP = sum(MAMP_list) // 10

    MD = abs(MP - MAMP)

    CCI = (MP - MAMP) // (0.015 * MD)

    # MACD 계산
    avg_ten = 0
    for j in range(0, 10):
        avg_ten = avg_ten + int(price_list[j])

    avg_ten = avg_ten // 10

    MACD = round((avg_five - avg_ten) / avg_ten, 2)

    i += 1


driver.quit()