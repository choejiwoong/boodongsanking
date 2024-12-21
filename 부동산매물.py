import requests
import pandas as pd
import time
import json
#이거 참고하기: https://thisiswhoiam.tistory.com/44

keyword = '부산광역시 해운대구'

url = f'https://m.land.naver.com/search/result/{keyword}#mapFullList'
headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}
res = requests.get(url, headers=headers, verify=False)
main_url = res.url.split('/*/*')[0]
lat = main_url.split('/')[4].split(':')[0] #위도
lon = main_url.split('/')[4].split(':')[1] #경도
z = main_url.split('/')[4].split(':')[2] #축적
cortarNo = main_url.split('/')[4].split(':')[3] #지역코드
# mapping 고정값
btm = float(lat) - 0.1221837
top = float(lat) + 0.1221837
lft = float(lon) - 0.2343178
rgt = float(lon) + 0.2343178
buildingType = 'APT' #아파트

keyList = ['atclNo', 'atclNm', 'rletTpNm', 'tradTpNm', 'bildNm', 'flrInfo', 'prc', 'sameAddrMaxPrc', 'sameAddrMinPrc', 'sameAddrCnt', 'direction', 'spc1', 'spc2']
#매물번호, 건물명, 건물유형, 거래유형, 동, 해당층/전체층, 가격, 동일 매물 최고 가격, 동일 매물 최저 가격, 동일 매물 개수, 방향, 공급, 전용

def extractList(page):
    # rletTpCd: 건물 유형 (아파트, 아파트분양권, 상가 등)
    # tradTpCd: 거래 유형 (A1: 매매, B1: 전세, B2: 월세)
    # page: 1 페이지에 매물 20개 크롤링 가능
    sub_url = f'https://m.land.naver.com/cluster/ajax/articleList?rletTpCd={buildingType}&tradTpCd=A1&z={z}&lat={lat}&lon={lon}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&showR0=&page={str(page)}'
    res = requests.get(sub_url, headers=headers, verify=False)
    data = json.loads(res.text)
    print(data)
    time.sleep(1)
    return res

print(extractList(1))


