import asyncio
import streamlit as st
from sigungu import RegionInfo
from real_estate import RealEstateFetcher

# RegionInfo 객체 생성
region_info = RegionInfo()

# Streamlit App 설정
st.set_page_config(layout="wide")
st.title("네이버 아파트 매물 리스트")
st.write("Displaying real estate data from Naver Land API.")

# 세션 상태 초기화
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

# 콤보박스 콜백 함수
def update_region():
    st.session_state.selected_option = st.session_state.region_select
    st.session_state.dataframe = None  # 데이터 초기화

# 콤보 박스: 변경 시 새로고침 대신 콜백
selected_option = st.selectbox(
    "콤보박스를 선택해 주세요.",
    ["선택 안함"] + ["해운대구", "수영구", "동래구", "남구", "연제구", "부산진구", "강서구"],
    index=0,
    key="region_select",
    on_change=update_region,  # 콜백 연결
)

# 데이터 가져오기
async def fetch_data(sigungu_name):
    region_data = region_info.get_region_data(sigungu_name)
    fetcher = RealEstateFetcher(region_data=region_data)
    df = fetcher.get_dataframe()
    return df

# 매물 목록 불러오기 버튼
if st.button("매물 목록 불러오기"):
    if selected_option != "선택 안함":
        with st.spinner("Fetching data..."):
            st.session_state.dataframe = asyncio.run(fetch_data(selected_option))
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

    # 필터링된 데이터프레임
    filtered_df = df.copy()
    if trad_tp_filter != "전체":
        filtered_df = filtered_df[filtered_df["매매/전세"] == trad_tp_filter]
    if apt_filter.strip():  # 공백을 제거하고 입력값이 있는 경우만 필터링
        filtered_df = filtered_df[filtered_df["아파트명"].str.contains(apt_filter.strip(), case=False, na=False)]

    # 필터링된 데이터프레임 표시
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.write("데이터가 없습니다. 지역을 선택하고 데이터를 불러오세요.")
