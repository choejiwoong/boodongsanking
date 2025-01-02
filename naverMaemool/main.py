import asyncio
import streamlit as st
from sigungu import RegionInfo
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

# 매물 목록 불러오기 버튼
if st.button("매물 목록 불러오기"):
    if si_combo != "선택 안함" and gungu_combo != "선택 안함":
        with st.spinner("Fetching data..."):
            # 아파트 목록 가져오기
            apt_list_dict = region_info.get_apt_list_dict(si_combo, gungu_combo)
            all_apartment_data = []  # 모든 아파트 데이터를 저장할 리스트

            # 각 아파트에 대해 매물 데이터를 가져오기
            for apt_name in apt_list_dict.values():
                apartment_data = region_info.get_apt_maemool_dict(si_combo, gungu_combo, apt_name)
                parsed_data = region_info.parse_articles(response=apartment_data)
                if parsed_data:  # 데이터가 비어있지 않은 경우 추가
                    all_apartment_data.extend(parsed_data)

            # 모든 데이터를 하나의 DataFrame으로 결합
            if all_apartment_data:
                combined_df = pd.DataFrame(all_apartment_data)
                st.session_state.dataframe = combined_df
                st.success("모든 데이터를 로드 완료!")
            else:
                st.write("데이터를 불러올 수 없습니다. 다시 시도해주세요.")

# 필터 및 데이터 표시
if st.session_state.dataframe is not None:
    df = st.session_state.dataframe

    # 필터 선택 UI
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
        index=area_range.index("24평~30평"),  # default
        key="area_filter",
    )

    # 필터링된 데이터프레임
    filtered_df = df.copy()
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
