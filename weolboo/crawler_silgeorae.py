### 대충 완료함
import pandas as pd
from PublicDataReader import TransactionPrice


# 최대 출력할 행 수와 열 수 설정
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 출력 너비 제한 없애기
pd.set_option('display.max_colwidth', None)  # 열의 최대 너비를 제한하지 않음

service_key = "uIpKsI5ZLpNqZwMOkFMo1ey%2BiPufiaF57op3k4kt5gQ5u0UozQGi5c5ZmNs3j1HMJtIWXJn75mVEey4B%2BriCHA%3D%3D"
api = TransactionPrice(service_key)

# 기간 내 조회
# 아파트 데이터
df = api.get_data(
    property_type="아파트",
    trade_type="매매",
    sigungu_code="26470", # 부산 연제구
    start_year_month="202101",
    end_year_month="202504",
)

for apt_name in df['aptNm'].unique():
    df_filtered = df[
        (df['aptNm'] == apt_name) &
        (df['excluUseAr'].astype(str).str.split('.').str[0] == "59")
    ]

    if df_filtered.empty:
        continue  # 조건에 맞는 데이터가 없으면 건너뜀

    df_filtered.loc[:, 'dealAmount'] = df_filtered['dealAmount'].str.replace(',', '').astype(float)
    # 4층 이상 가장 최신 실거래가
    lastest_row = df_filtered[df_filtered['floor'].astype(int) >= 4].tail(1)

    print(lastest_row)
#     # 최고 실거래가는 그냥 아실에서 확인하는게 나을듯... 입주권이나 이런건 카운팅을 못함
#     max_row = df_filtered[df_filtered['dealAmount'] == df_filtered['dealAmount'].max()]
#     max_value = df_filtered['dealAmount'].max()
#
#     print(f"[{apt_name}] 최고 거래가: {max_value}만원")
#     print(max_row)
#     print('-' * 50)

# # 각 행에서 필요한 정보를 뽑아서 보기 좋은 이름으로 딕셔너리로 변환
# for index, row in df.iterrows():
#     apartment_info = {
#         "아파트명": row['aptNm'],
#         "거래연도": row['dealYear'],
#         "거래월": row['dealMonth'],
#         "거래일": row['dealDay'],
#         "거래금액": row['dealAmount'],
#         "동": row['aptDong'],
#         "층수": row['floor'],
#         "거래구분": row['dealingGbn'],
#         "전용면적": row['excluUseAr'],
#         "준공연도": row['buildYear'],
#         "아파트Seq": row['aptSeq']
#     }
#     print(apartment_info)
