### kb 매매지수/전세지수 불러오기
### 여기 참고함: https://wooiljeong.github.io/python/pdr-kbland/
### 완료함
import requests
import pandas as pd

def get_price_index(월간주간구분코드, 매물종별구분, 매매전세코드, **kwargs):
    """
    KB통계 - 주택가격동향조사 - 가격지수

    Parameters
    ----------
    월간주간구분코드 : str
        월간주간구분코드
        01: 월간
        02: 주간
    매물종별구분 : str
        매물종별구분
        01: 아파트
        08: 연립
        09: 단독
        98: 주택종합
    매매전세코드 : str
        매매전세코드
        01: 매매
        02: 전세
    **kwargs : dict
        그 외 필요한 파라미터
        지역코드 : str
    """
    url = "https://data-api.kbland.kr/bfmstat/weekMnthlyHuseTrnd/priceIndex"

    # 매물종별구분이 '01'이 아니면 월간주간구분코드는 '01'
    if 매물종별구분 != "01":
        월간주간구분코드 = "01"
    params = {
        "월간주간구분코드": 월간주간구분코드,
        "매물종별구분": 매물종별구분,
        "매매전세코드": 매매전세코드,
    }
    params.update(kwargs)
    try:
        res = requests.get(url, params=params, verify=False)
        data = res.json()['dataBody']['data']
    except Exception as e:
        print(e)
        return
    result_code = res.json()['dataBody']['resultCode']
    if str(result_code) != "11000":
        print(data['message'])
        return
    n_data_list = len(data['데이터리스트'][0]['dataList'])
    n_date_list = len(data['날짜리스트'])
    n_date_str = len(data['날짜리스트'][0])
    columns = data['날짜리스트']
    df = pd.DataFrame(data['데이터리스트'])
    values = pd.DataFrame(
        df['dataList'].values.tolist()).iloc[:, :n_date_list]
    values.columns = columns
    df = pd.concat([df[['지역코드', '지역명']], values], axis=1)
    df2 = pd.melt(df, id_vars=['지역코드', '지역명']).rename(
        columns={'variable': '날짜', 'value': '가격지수'})
    if n_date_str == 6:
        df2['날짜'] = pd.to_datetime(df2['날짜'], format='%Y%m')
    elif n_date_str == 8:
        df2['날짜'] = pd.to_datetime(df2['날짜'], format='%Y%m%d')
    df2 = df2.sort_values(['지역코드', '날짜'], ascending=[
        True, True]).reset_index(drop=True)
    # 코드 정보 부여
    code_df = pd.DataFrame({
        "월간주간구분": [월간주간구분코드],
        "매물종별구분": [매물종별구분],
        "거래구분": [매매전세코드],
    })
    code_df = pd.concat([code_df] * len(df2), ignore_index=True)
    df2 = pd.concat([code_df, df2], axis=1)
    return df2

params = {
    '지역코드':'2600000000', # 부산
    'type': 'false',
    '메뉴코드': '1',
}

df_maemae = get_price_index('01', '01', '01', **params)
df_jeonse = get_price_index('01', '01', '02', **params)
print(df_maemae[df_maemae['지역명'] == '연제구']) # 연제구 kb월간매매지수 불러오기
print(df_jeonse[df_jeonse['지역명'] == '연제구']) # 연제구 kb월간전세지수 불러오기
