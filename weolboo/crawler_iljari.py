####  산업별, 동별 사업체수 및 종사자수
#### 아직 안 끝남....
from PublicDataReader import Kosis
import pandas as pd
# https://github.com/WooilJeong/PublicDataReader/blob/main/assets/docs/kosis/Kosis.md
# 최대 출력할 행 수와 열 수 설정
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 출력 너비 제한 없애기
pd.set_option('display.max_colwidth', None)  # 열의 최대 너비를 제한하지 않음

# KOSIS 공유서비스 Open API 사용자 인증키
service_key = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="

# 인스턴스 생성하기
api = Kosis(service_key)

# df = api.get_data(
#     "KOSIS통합검색",
#     searchNm="시군구별 종사자수"
# )
# print(df.head)
# 시군구별(8개시), 산업별, 규모별, 사업체수 및 종사자수(성별): 118 / DT_118N_SAUPN75 (광역시)
# 시군구별(9개도), 산업별, 규모별, 사업체수 및 종사자수(성별): 118 / DT_118N_SAUPN78

# item = api.get_data(
#     "통계표설명",
#     "분류항목",
#     orgId='118',
#     tblId='DT_118N_SAUPN75',
# )
# print(item)

df = api.get_data(
    service_name="통계자료",  # 서비스명: '통계자료'로 수정
    orgId="118",  # 기관 ID
    tblId="DT_118N_SAUPN75",  # 통계표 ID
    objL1="15118ZONE2012_212113",  # 분류1(첫번째 분류코드) = 지역별 ex) 연제구
    objL2="190326INDUSTRY_10S0", # 분류2(두번째 분류코드) = 산업분류별 ex) 전체: 190326INDUSTRY_10S0
    objL3="15118SIZES_0700", # 분류3(세번째 분류코드) = 규모별 ex) 전규모
    itmId="16118ED_9A",  # 항목 = 사업체수/종사자수 ex) 사업체수: 16118ED_1 / 종사자수: 16118ED_9A
    prdSe="Y",  # 수록주기
    startPrdDe="2022",  # (시점기준) 시작수록시점
    endPrdDe="2022",  # (시점기준) 종료수록시점
)
# print(df['수치값'].sum())
print(df)
