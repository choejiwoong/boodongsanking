### 미분양데이터 불러오기
### 완성됨
from PublicDataReader import Kosis

# KOSIS 공유서비스 Open API 사용자 인증키
service_key = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="

# Kosis 객체 생성
kosis = Kosis(service_key)

df = kosis.get_data(
    "통계자료",
    orgId='101',
    tblId='DT_1YL202004E',
    objL1="13102871087A.0004", #부산 미분양
    objL2="ALL",
    itmId="ALL",
    prdSe="M",
    startPrdDe="202004",
    endPrdDe="202404"
)
df_filtered = df[(df['분류값명1']=='부산')&(df['분류값명2']=='연제구')]

# 각 행에서 필요한 정보를 뽑아서 보기 좋은 이름으로 딕셔너리로 변환
for index, row in df_filtered.iterrows():
    miboonyang_info = {
        "수록시점": row['수록시점'],
        "수치값": row['수치값'],
    }

    print(miboonyang_info)
