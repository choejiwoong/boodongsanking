# 공공데이터포털: https://www.data.go.kr/index.do
# 참고하기: https://www.youtube.com/watch?v=e1N3PVwRV_U&list=PLTLlOtUtSDVkBFxVC5cgeZXpE7-4FoL4X

import requests
url = 'https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade'
params = {
    'serviceKey': 'uIpKsI5ZLpNqZwMOkFMo1ey%2BiPufiaF57op3k4kt5gQ5u0UozQGi5c5ZmNs3j1HMJtIWXJn75mVEey4B%2BriCHA%3D%3D',
    'LAWD_CD': '11110',
    'DEAL_YMD': '202407',
    'pageNo': '1',
    'numOfRows': '10',
}
res = requests.get(url, params=params, verify=False)
print(res.text)