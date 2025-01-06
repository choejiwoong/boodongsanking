from PublicDataReader import Kosis
import pandas as pd
#### 아직 못끝냄
#### 여기 참고: https://wooiljeong.github.io/python/pdr-kosis-ex1/

# KOSIS 공유서비스 Open API 사용자 인증키
service_key = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="

# 인스턴스 생성하기
api = Kosis(service_key)
df = api.get_data(
    "통계자료",
    orgId="101",
    tblId="DT_1B04005N",
    objL1="ALL",
    objL2="0",
    itmId="T2 T3 T4",
    prdSe="M",
    startPrdDe="202211",
    endPrdDe="202211",
)
pv = df.pivot(index=["분류값ID1","분류값명1","수록시점"], columns=["항목명"], values="수치값").reset_index()
pv.columns.name = None
pv['수록시점'] = pd.to_datetime(pv['수록시점'], format="%Y%m")
numCols = ["남자인구수","여자인구수","총인구수"]
for col in numCols:
    pv[col] = pd.to_numeric(pv[col])

print(pv)