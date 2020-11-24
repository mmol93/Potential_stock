from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import os
import shutil
import time
import get_sotckCode
import check_Excell

## 종목들 각종 계산 및 정보 스크래핑하기

stock_list = check_Excell.call_excell_stock()
stockCode_list = get_sotckCode.code_search()

path = "C:/selenium/chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")

driver = webdriver.Chrome("C:/selenium/chromedriver", options=options)
url_1 = "https://finance.naver.com/item/sise.nhn?code="     # 네이버 주식_ 개별종목 앞 주소(시세부분)

# 각 종목들 사이트(네이버)에 접속하여 정보 가져오기
