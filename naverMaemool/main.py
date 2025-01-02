import asyncio
import streamlit as st
from sigungu import RegionInfo
from real_estate import RealEstateFetcher
import pandas as pd

# RegionInfo 객체 생성
region_info = RegionInfo()

# Streamlit App 설정
st.set_page_config(layout="wide")
st.title("네이버 아파트 매물 리스트")
st.write("Displaying real estate data from Naver Land API.")
st.write("bot 크롤링 막혔을 시: https://fin.land.naver.com/?content=recent")

# 세션 상태 초기화
if "si_combo" not in st.session_state:
    st.session_state.si_combo = None
if "gungu_combo" not in st.session_state:
    st.session_state.gungu_combo = None
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

# 콤보박스 콜백 함수
def update_region():
    if st.session_state.si_combo != st.session_state.si_select:
        st.session_state.si_combo = st.session_state.si_select
    if st.session_state.gungu_combo != st.session_state.gungu_select:
        st.session_state.gungu_combo = st.session_state.gungu_select
    # 데이터 초기화 (필요한 경우)
    if "dataframe" in st.session_state:
        del st.session_state.dataframe

# 시 콤보 박스: 변경 시 새로고침 대신 콜백
si_combo = st.selectbox(
    "시를 선택해 주세요.",
    ["선택 안함"] + list(region_info.get_si_dict().keys()),
    index=0,
    key="si_select",
    on_change=update_region,  # 콜백 연결
)
# 군구 콤보 박스: 변경 시 새로고침 대신 콜백
gungu_combo = st.selectbox(
    "군구를 선택해 주세요.",
    ["선택 안함"] + list(region_info.get_gungu_dict(si_name=si_combo).keys()),
    index=0,
    key="gungu_select",
    on_change=update_region,  # 콜백 연결
)

# 데이터 가져오기
async def fetch_data(si_name, gungu_name):
    region_data = region_info.get_dong_list(si_name, gungu_name)
    fetcher = RealEstateFetcher(region_data=region_data)
    df = fetcher.get_dataframe()
    return df

# 매물 목록 불러오기 버튼
if st.button("매물 목록 불러오기"):
    if si_combo != "선택 안함" and gungu_combo != "선택 안함":
        with st.spinner("Fetching data..."):
            st.session_state.dataframe = asyncio.run(fetch_data(si_combo, gungu_combo))
            if st.session_state.dataframe is not None:
                st.success("데이터 로드 완료!")
            else:
                st.write("데이터 로드에 실패했습니다.")

# 필터 및 데이터 표시
if st.session_state.dataframe is not None:
    df = st.session_state.dataframe

    # 필터 선택 UI
    trad_tp_filter = st.selectbox(
        "매매/전세 선택:",
        ["전체"] + df["매매/전세"].unique().tolist(),
        key="trad_tp_filter",
    )
    apt_filter = st.text_input(
        "아파트 이름 입력:",
        "",  # 기본값을 공백으로 설정
        placeholder="아파트 명을 공백을 제외하고 입력해주세요",  # 워터마크 텍스트처럼 보이게
        key="apt_filter",
    )
    # 평 단위로 면적 범위 선택 콤보 박스
    # 면적이 문자열로 되어 있을 경우 숫자로 변환
    df["면적"] = pd.to_numeric(df["면적"], errors="coerce")  # 변환 불가능한 값은 NaN으로 처리
    df["면적_평"] = round(df["면적"] / 3.3)  # 면적을 평 단위로 변환
    # 면적 범위 선택: '~24평', '24평~34평', '34평~40평', '40평~'
    area_range = [
        "~24평",
        "24평~30평",
        '30평~40평',
        "40평~",
    ]
    area_filter = st.selectbox(
        "면적 범위 선택 (평):",
        area_range,
        index=area_range.index("24평~30평"), # default
        key="area_filter",
    )

    # 필터링된 데이터프레임
    # 매매/전세 필터링
    filtered_df = df.copy()
    if trad_tp_filter != "전체":
        filtered_df = filtered_df[filtered_df["매매/전세"] == trad_tp_filter]
    # 아파트명 필터링
    if apt_filter.strip():  # 공백을 제거하고 입력값이 있는 경우만 필터링
        filtered_df = filtered_df[filtered_df["아파트명"].str.contains(apt_filter.strip(), case=False, na=False)]
    # 면적 범위에 따라 필터링
    if area_filter == "~24평":
        filtered_df = filtered_df[(filtered_df["면적_평"] >= 0) & (filtered_df["면적_평"] < 24)]
    elif area_filter == "24평~30평":
        filtered_df = filtered_df[(filtered_df["면적_평"] >= 24) & (filtered_df["면적_평"] < 30)]
    elif area_filter == "30평~40평":
        filtered_df = filtered_df[(filtered_df["면적_평"] >= 30) & (filtered_df["면적_평"] < 40)]
    elif area_filter == "40평~":
        filtered_df = filtered_df[filtered_df["면적_평"] >= 40]
    # '면적' 컬럼을 "면적(평)" 형식으로 변경
    filtered_df["면적"] = filtered_df["면적"].apply(lambda x: f"{x/3.3:.0f}평 ({x:.2f}m²)" if pd.notnull(x) else "N/A")
    # '면적_평' 컬럼 삭제
    filtered_df.drop(columns=['면적_평'], inplace=True)

    # 필터링된 데이터프레임 표시
    st.dataframe(filtered_df, use_container_width=True, height=1000)
    # 데이터 개수 표시
    st.write(f"전체 데이터 수: {len(filtered_df)}개")
else:
    st.write("데이터가 없습니다. 지역을 선택하고 데이터를 불러오세요.")
