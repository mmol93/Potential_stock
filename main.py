from selenium import webdriver
from datetime import datetime
import get_sotckCode
import check_Excell
import numpy
import controlExcel
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## 가능성 종목 검토 툴

### 종목들 각종 계산 및 정보 스크래핑하기

print("실시 날짜: " + str(datetime.now().strftime("%Y/%m/%d, %H:%M")))

print("종목명 / 현재가 / 이평5일과 차이 / 5일간 주가 변봐량 / CCI / MACD / 외국인 연속 / 기관 연속 / PER / PBR")

stock_list = check_Excell.call_excell_stock()
stockCode_list = get_sotckCode.code_search()

path = "C:/selenium/chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")

print("len(stock_list): " + str(len(stock_list)))

## 각 종목들 사이트(네이버)에 접속하여 정보 가져오기
i = 0
try:
    # 시작하기 전에 엑셀의 '추천 종목' 부분 기록되어 있는 데이터 삭제
    controlExcel.delete_data()

    # 종목 1개씩 실시(test : 1로 설정하여 종목 1개에 대해서만 실시하게 하기), 나중에느 len(stock_list)로 변경하기
    while i < len(stock_list) / 2:  # 이유는 모르겠지만 엑셀에서 리스트 가져올 때 1번 복사해서 또 넣음;;
        driver = webdriver.Chrome("C:/selenium/chromedriver", options=options)
        url_1 = "https://finance.naver.com/item/sise.nhn?code="  # 네이버 주식_ 개별종목 앞 주소(시세부분)
        url = url_1 + stockCode_list[i]
        driver.get(url)
        price_list = []

        # 똑같은 iframe이 2개 있어서
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[8])  # 아래의 데이터를 갖고 있는 iframe이 8번째에 있음

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

        # 최근 5일간 변화가 1.5%를 넘은적이 있는지 확인한다
        five_change_counter_plus = 0
        five_change_counter_minus = 0

        for j in range(0, 6):
            five_change_rate = round((int(price_list[j]) - int(price_list[j+1])) / int(price_list[j]) * 100, 2)
            # 현재가 기준 최근 6일간 시세에서 몇 %이상 변동이 있었는지 판단한다
            if five_change_rate >= 1.5:
                five_change_counter_plus += 1
            elif five_change_rate <= -1.5:
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
        # MP: 당일의 고, 저, 종가의 평균
        MP = (int(price_list[0]) + int(high_price_list[0]) + int(low_price_list[0])) / 3

        # MAMP & MD 동시 계산(특성상 동시에 계산해야함
        # MAMP: MP(고, 저, 종)의 이동평균
        # MD: MAMP의 표준편차

        MAMP_list = []
        MD_list = []
        for j in range(0, 10):
            MAMP = (int(price_list[j]) + int(high_price_list[j]) + int(low_price_list[j])) / 3
            MAMP_list.append(MAMP)

        # 10일치 데이터니 이평은 모든 요소 합에 나누기 10
        MAMP = sum(MAMP_list) / 10
        MD = numpy.std(MAMP_list)

        # CCI에 대한 정보는 참고서 참조
        CCI = (MP - MAMP) // (0.015 * MD)

        # print(high_price_list)
        # print(low_price_list)
        # print("MP:", MP)
        # print("MAMP:", MAMP)
        # print("MD:", MD)
        # print("CCI:", CCI)

        # MACD 계산
        avg_ten = 0
        for j in range(0, 10):
            avg_ten = avg_ten + int(price_list[j])

        avg_ten = avg_ten // 10

        MACD = round((avg_five - avg_ten) / avg_ten * 100, 2)

        driver.switch_to.default_content()

        ## 외국인 & 기관 연속 수급 비교
        # 참조하는 페이지가 다르기 때문에 새로운 url을 설정하여 접속한다
        url_1 = "https://finance.naver.com/item/main.nhn?code="
        url = url_1 + stockCode_list[i]

        driver.get(url)

        xpath_counter = 0
        xpath_num = 2
        forign_buyingHistory_unit = ""
        foreign_buyingHistory_value = 0

        # 먼저 외국인 수급 확인
        try:
            # 현재 표에 있는 외국인 기간 데이터를 모두 얻음(6일치)
            while xpath_num <= 7:
                xpath = "//*[@id='content']/div[2]/div[2]/table/tbody/tr["

                forign_buyingHistory = driver.find_element_by_xpath(
                    xpath + str(xpath_num) + "]/td[3]/em").text

                # 처음(오늘날짜)에는 +, - 상관없이 카운터에 무조건 +1을 함
                # 그리고 +인지 -인지 forign_buyingHistory_unit에 기록
                # 단, 오늘 날짜에 데이터가 없을 경우 break 실시
                if xpath_counter == 0 and forign_buyingHistory[0] == "+":
                    forign_buyingHistory_unit = "+"
                    xpath_counter += 1
                elif xpath_counter == 0 and forign_buyingHistory[0] == "-":
                    forign_buyingHistory_unit = "-"
                    xpath_counter += 1

                # 최초 카운터 이후 직전에 얻은 단위(+,-)와 비교하면서 일치하면 count +1
                elif xpath_counter >= 1 and forign_buyingHistory[0] == forign_buyingHistory_unit:
                    xpath_counter += 1
                else:
                    forign_buyingHistory_message = "(" + str(forign_buyingHistory_unit) + str(xpath_counter) + "일간)"
                    break;
                xpath_num += 1
            forign_buyingHistory_message = "(" + str(forign_buyingHistory_unit) + str(xpath_counter) + "일간)"
            foreign_buyingHistory_value = xpath_counter
        except:
            forign_buyingHistory_message = "수급정보 없음"

        # 기관 수급 확인
        # 위에서 사용한 변수 초기화
        xpath_counter = 0
        xpath_num = 2
        company_buyingHistory_unit = ""
        company_buyingHistory_value = 0
        try:
            # 현재 표에 있는 기관의 기간 데이터를 모두 얻음(6일치)
            while xpath_num <= 7:
                xpath = "//*[@id='content']/div[2]/div[2]/table/tbody/tr["

                company_buyingHistory = driver.find_element_by_xpath(
                    xpath + str(xpath_num) + "]/td[4]/em").text

                # 처음(오늘날짜)에는 +, - 상관없이 카운터에 무조건 +1을 함
                # 그리고 +인지 -인지 forign_buyingHistory_unit에 기록
                # 단, 오늘 날짜에 데이터가 없을 경우 break 실시
                if xpath_counter == 0 and company_buyingHistory[0] == "+":
                    company_buyingHistory_unit = "+"
                    xpath_counter += 1
                elif xpath_counter == 0 and company_buyingHistory[0] == "-":
                    company_buyingHistory_unit = "-"
                    xpath_counter += 1

                # 최초 카운터 이후 직전에 얻은 단위(+,-)와 비교하면서 일치하면 count +1
                elif xpath_counter >= 1 and company_buyingHistory[0] == company_buyingHistory_unit:
                    xpath_counter += 1
                else:
                    company_buyingHistory_message = "(" + str(company_buyingHistory_unit) + str(xpath_counter) + "일간)"
                    break
                xpath_num += 1
            company_buyingHistory_message = "(" + str(company_buyingHistory_unit) + str(xpath_counter) + "일간)"
            company_buyingHistory_value = xpath_counter
        except:
            company_buyingHistory_message = "수급정보 없음"

        # 조건에 따른 결과 출력
        total = ""
        # 0. 급등 0번 + 급락 0번 이상 + 외국인 3일 연속 구매 = 외국인 풀매수
        if forign_buyingHistory_unit == "+" and foreign_buyingHistory_value >= 3 and five_change_counter_plus == 0 and five_change_counter_minus >= 0:
            total = "0순위 외국인 풀매수"
            # 해당 종목명을 '매수추천' 시트에 기록
            controlExcel.add_stock(stock_list[i], url)
        # 1. 5일 이평선 위 + CCI(40이하) + 최근 급등 1번 있음 + 외국인이 구매 시작 = 매수 고려
        elif present_diff_avgFive > 0 and CCI <= 40 and five_change_counter_plus > 0 and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 0:
            total = "매수 고려1"
            controlExcel.add_stock(stock_list[i], url)
        # 2. 5일 이평선 아래 + CCI(40이하) + 급락 2번 이상 = 주시하기 or 뉴스 확인
        elif present_diff_avgFive < 0 and five_change_counter_minus > 1:
            total = "뉴스 확인2"
        # 3. 5일 이평선 위 + CCI(80 이상) + 최근 급등 2번 + 외국인 매수 2번 이상= 매수 고려
        elif present_diff_avgFive > 0 and CCI >= 80 and five_change_counter_plus > 1 and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value >= 2:
            total = "올라 타기3"
        # 4. 5일 이평선 아래 + CCI(40이하) + 최근 급락 1번 + 외국인 매수 2번 = 매수 고려
        elif present_diff_avgFive < 0 and CCI <= 40 and five_change_counter_minus >= 1 and foreign_buyingHistory_value > 1 and forign_buyingHistory_unit == "+":
            total = "매수 고려4"
            controlExcel.add_stock(stock_list[i], url)
        # 5 CCI(40이하) + 외국인/기관 매수 = 매수 고려
        elif CCI <= 40 and five_change_counter_plus == 0 and five_change_counter_minus == 0 and MACD < 0 and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 0:
            total = "MACD 매수 고려5"
            controlExcel.add_stock(stock_list[i], url)
        # 6 CCI(40이하) + 최근 급락/급등 없음 + 외국인 매수 = 눌림목
        elif CCI <= 40 and five_change_counter_plus == 0 and five_change_counter_minus == 0 and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 0:
            total = "눌림목"
            controlExcel.add_stock(stock_list[i], url)
        # 7 5일 이평선 위 + CCI(40이하) + 최근 5일간 급락/급등(+- 1.5%) 없음 + 외국인/기관 매수 2번 이상 = 매수고려
        elif present_diff_avgFive > 0 and CCI <= 40 and five_change_counter_plus == 0 and five_change_counter_minus == 0 and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 1:
            total = "매수 고려7"
            controlExcel.add_stock(stock_list[i], url)
        # 8 최근 변동 1번 이하 + 외국인 2일 연속 매수 + 기관 2일 연속매수 + 이동선위 = 매수고려
        elif (five_change_counter_plus <= 1 or five_change_counter_minus <= 1) and forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 1 and company_buyingHistory_unit == "+" and company_buyingHistory_value > 1 and present_diff_avgFive > 0:
            total = "매수 고려8"
            # 해당 종목명을 '매수추천' 시트에 기록
            controlExcel.add_stock(stock_list[i], url)
        # 9 외국인 2일 연속 매수 + 기관 2일 연속 매수 = 외국인 기관 양매수
        elif forign_buyingHistory_unit == "+" and foreign_buyingHistory_value > 1 and company_buyingHistory_unit == "+" and company_buyingHistory_value > 1:
            total = "기관 외국인 이틀 양매수9"
            # 해당 종목명을 '매수추천' 시트에 기록
            controlExcel.add_stock(stock_list[i], url)
        # 10 6일동안 변동 +, - 한 개도 없음 = 차트보기
        elif five_change_counter_plus == 0 and five_change_counter_minus == 0:
            total = "6일간 큰변동 없음"
        # 11 기관 매수 연속 3번 이상 + 급등 0번 + 급락 0번 = 기관 풀매수
        elif company_buyingHistory_unit == "+" and company_buyingHistory_value >= 3 and five_change_counter_plus == 0 and five_change_counter_minus == 0 :
            total = "0순위 기관 풀매수"
            # 해당 종목명을 '매수추천' 시트에 기록
            controlExcel.add_stock(stock_list[i], url)
        # 직접 분석
        else:
            total = "X"

        ### 박스권 설정
        # 종목명 설정
        # if (stock_list[i] == "더존비즈온"):
        #     # 현재 시세와 박스권 가격 비교
        #     if (int(price_list[0]) <= 100000):
        #         total = "박스권 최하단"


        ## 각 종목들의 PER, PBR 알아내기
        try:
            url1 = "https://finance.naver.com/item/main.nhn?code="
            url2 = stockCode_list[i]
            url = url1 + url2    # 다음 금융의 '기업정보'탭
            driver.get(url)

            xpath = "//*[@id='_per']" # PER에 대한 xpath

            PERValue = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, xpath))).text
        except TimeoutException:
            PERValue = "PER없음"
        try:
            xpath = "//*[@id='_pbr']" # PBR에 대한 xpath

            PBRValue = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, xpath))).text
        except TimeoutException:
            PBRValue = "PBR없음"

        # 출력할 데이터 설정
        result_list = []
        result_list.append(stock_list[i])   # 종목명
        result_list.append(price_list[0])   # 종목 시세
        result_list.append(str(round(present_diff_avgFive, 2)) + "%")  # 현재 시세와 5일 이동평균 차이(%)
        result_list.append("+(" + str(five_change_counter_plus) + ")")    # 5일간 +1.5% 간적 있는지 카운터
        result_list.append("-(" + str(five_change_counter_minus) + ")")   # 5일간 -1.5% 간적 있는지 카운터
        result_list.append("CCI: " + str(CCI)) # CCI
        result_list.append("MACD: " + str(MACD))    # MACD
        result_list.append(forign_buyingHistory_message)    # 외국인 연속수급
        result_list.append(company_buyingHistory_message)   # 기관 연속 수급
        result_list.append(total)
        result_list.append(PERValue)
        result_list.append(PBRValue)
        result_list.append(url)     # 현재 참조하고있는 페이지

        print(result_list)
        i += 1
        result_list.clear()

    driver.quit()

except TimeoutException:
    print("--통신 에러 발생--")
    driver.quit()
