import pandas as pd
import check_Excell
import numpy

dfstockcode = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]

dfstockcode.columns

# 얻고자하는 DataFrame의 컬럼명을 쓰면
# 시리즈형으로 컬럼에 있는 값을 반환
dfstockcode.종목코드.head()

type(dfstockcode.종목코드)

# 종목코드에 값을 6자리 문자열로 설정
#    종목코드의 숫자값을 6자리 문자열로 변환
#    채우는 자리는 0으로 채우기
dfstockcode.종목코드 = dfstockcode.종목코드.map('{:06d}'.format)

# 필요한 컬럼만으로 DataFrame을 설정
dfstockcode = dfstockcode[['회사명', '종목코드']]

company = dfstockcode.회사명
code = dfstockcode.종목코드

company_list = list(company) # company를 리스트형으로 변경 = 상장 회사 리스트
code_list = list(code)  #code를 리스트형으로 변경 = 상장 회사 코드

stock_list = check_Excell.call_excell_stock() # 내가 만든 stock_list의 종목들
match_code = [] # 내가 만든 종목리스트와 매치되는 종목 코드

def code_search():
    for stock_name in stock_list:
        # 내가만든 AI리스트 - 전체 상장 종목 리스트 매치
        index_Stock_name = company_list.index(stock_name)  #거기서 인덱스 뽑아냄
        match_code.append(code_list[index_Stock_name])  # 내가 만든 AI_list 종목과 매치되는 종목 코드
    return match_code
