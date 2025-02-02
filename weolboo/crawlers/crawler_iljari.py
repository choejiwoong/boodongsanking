####  산업별, 동별 사업체수 및 종사자수
#### 아직 안 끝남....
#### 여기 참고: https://kosis.kr/statHtml/statHtml.do?orgId=543&tblId=DT_54301_D001003&vw_cd=MT_OTITLE&list_id=202A_543_54301_D&scrId=&seqNo=&lang_mode=ko&obj_var_id=&itm_id=&conn_path=MT_OTITLE&path=%252FstatisticsList%252FstatisticsListIndex.do
from PublicDataReader import Kosis

# KOSIS 공유서비스 Open API 사용자 인증키
service_key = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="

# 인스턴스 생성하기
api = Kosis(service_key)

df = api.get_data(
    "통계표설명",
    "분류항목",
    orgId="543",
    tblId="DT_54301_D001003"
)

df_filtered = df.loc[df["분류ID"]=="BSM"]

for index, row in df_filtered.iterrows():
    print(row)

# df = api.get_data(
#     "통계자료",
#     ORG_ID="543",
#     TBL_ID="DT_54301_D001003",
#     C1_NM="1110100BW",
#     # startPrdDe="202211",
#     # endPrdDe="202211",
# )
# print(df)