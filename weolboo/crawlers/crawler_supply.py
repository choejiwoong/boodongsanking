### 미분양데이터 불러오기
### 완성됨
import PublicDataReader as pdr
from PublicDataReader import Kbland
from PublicDataReader import HousingLicense
import pandas as pd
import requests
from PublicDataReader import Kosis

# 인스턴스 생성하기
# 국토교통부 API
kbland = Kbland()
# ==============================================================================
# 아파트_입주물량
# ==============================================================================
"""
params
------
기간구분: 0: 월별, 1: 년별, 2: 반기별
법정동코드: 법정동코드 10자리
"""
params = {
    "기간구분": 1,
    "법정동코드": "2647000000", # 연제구
}

df = kbland.아파트_입주물량(**params)
print(df)

# ==============================================================================
# 국토교통부 주택인허가정보: 아직 service_key 승인이 안남(2025.02.02.)
# 라이브러리 관련 문서: https://wooiljeong.github.io/python/pdr-housing-license/
# ==============================================================================

# service_key = "9bg1tTFeumrhYeac4TTMmKVoiH5BV2qRxRlwEm%2FgFZB2vrjW%2BPpwQgFI0s7p5w9ipE7%2FqtijjWOmrxwEODkyMA%3D%3D"
# api = HousingLicense(service_key)
#
# df = api.get_data(
#     service_type="기본개요",
#     sigungu_code="41135",
#     bdong_code="11000",
#     bun="542",
#     ji="",
# )
#
# print(df.head(1))