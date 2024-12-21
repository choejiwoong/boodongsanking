import requests
import pandas as pd
import time
import json
#이거 참고하기: https://thisiswhoiam.tistory.com/44

keyword = '경상북도 구미시'

url = f'https://m.land.naver.com/search/result/{keyword}#mapFullList'
headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}

res = requests.get(url, headers=headers, verify=False)
main_url = res.url.split('/*/*')[0]
lat = main_url.split('/')[4].split(':')[0] #위도
lon = main_url.split('/')[4].split(':')[1] #경도
z = main_url.split('/')[4].split(':')[2]
cortarNo = main_url.split('/')[4].split(':')[3] #지역코드
buildingType = 'APT' #아파트

keyList = ['atclNo', 'atclNm', 'rletTpNm', 'tradTpNm', 'bildNm', 'flrInfo', 'prc', 'sameAddrMaxPrc', 'sameAddrMinPrc', 'sameAddrCnt', 'direction', 'spc1', 'spc2']
#매물번호, 건물명, 건물유형, 거래유형, 동, 해당층/전체층, 가격, 동일 매물 최고 가격, 동일 매물 최저 가격, 동일 매물 개수, 방향, 공급, 전용

def extractList(page):
    # rletTpCd: 건물 유형 (아파트, 상가 등)
    # tradTpCd: 거래 유형 (A1: 매매, B1: 전세, B2: 월세)
    # page: 1 페이지에 매물 20개 크롤링 가능
    sub_url = f'https://m.land.naver.com/cluster/ajax/articleList?rletTpCd={buildingType}&tradTpCd=A1%3AB1%3AB2&z={z}&lat={lat}&lon={lon}&cortarNo={cortarNo}&page={str(page)}'
    print(sub_url)
    res = requests.get(sub_url, headers=headers, verify=False)
    data = json.loads(res.text)
    print(data)
    return res

    # dataList = []
    #
    # for i in range(len(res['body'])):
    #     dataEle = []
    #
    #     for ele in keyList:
    #         try:
    #             dataEle.append(res['body'][i][ele])
    #         except:
    #             dataEle.append('')
    #     dataList.append(dataEle)
    #
    # df = pd.DataFrame(dataList, columns=keyList)
    #
    # return df
print(extractList(1))

#
# #################
# collectDf = []
#
# for i in range(1, 1000):
#     time.sleep(10)
#     df = extractList(i)
#
#     if df.shape[0] > 0:
#         collectDf.append(df)
#dd
#     else:
#         print(i)
#         break
#
# print(collectDf)