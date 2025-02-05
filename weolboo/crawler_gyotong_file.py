# 단발성 코드임, csv를 저장해야함

import pandas as pd
import csv

# CSV 파일 불러오기
df = pd.read_csv('C:/Users/cbbtng/Downloads/부산교통공사_시간대별 승하차인원_20241231.csv', encoding='cp949')

# 한글 인코딩 처리 (Windows에서 주로 사용)
file_name = 'C:/Users/cbbtng/Downloads/부산교통공사_시간대별 승하차인원_20241231.csv'
df = pd.read_csv(file_name, encoding='cp949')

# 출근시간
work_hours = ['06시-07시', '07시-08시', '08시-09시', '09시-10시']
# 퇴근시간
out_hours = ['16시-17시', '17시-18시', '18시-19시', '19시-20시']

# 출근시간과 퇴근시간의 합계 컬럼 추가
df['출근시간_합계'] = df[work_hours].sum(axis=1)
df['퇴근시간_합계'] = df[out_hours].sum(axis=1)
df['출퇴근시간_합계'] = df['출근시간_합계'] + df['퇴근시간_합계']

# 역번호, 역명, 구분(승차/하차)별 출퇴근 시간 합계
result_by_type = df.groupby(['역번호', '역명', '구분'])[['출근시간_합계', '퇴근시간_합계', '출퇴근시간_합계']].sum().reset_index()

# 역번호, 역명별 (승하차 합친) 출퇴근 시간 총합 추가
result_total = df.groupby(['역번호', '역명'])[['출근시간_합계', '퇴근시간_합계', '출퇴근시간_합계']].sum().reset_index()
result_total['구분'] = '총합'  # 구분 컬럼에 '총합' 표시

# 승차/하차별 데이터와 총합 데이터 합치기
final_result = pd.concat([result_by_type, result_total], ignore_index=True)

# 구분이 '총합'인 데이터를 기준으로 출퇴근_총합 내림차순 정렬
final_result = final_result.sort_values(by=['구분', '출퇴근시간_합계'], ascending=[True, False]).reset_index(drop=True)

# 천 단위 구분기호 추가
for col in ['출근시간_합계', '퇴근시간_합계', '출퇴근_총합']:
    final_result[col] = final_result[col].apply(lambda x: f'{x:,}')

# 결과 출력
print(final_result.head(20))

# 결과 CSV 파일로 저장
final_result.to_csv('C:/Users/cbbtng/Downloads/부산교통공사_출퇴근시간_승하차_합계_총합.csv', index=False, encoding='cp949')
