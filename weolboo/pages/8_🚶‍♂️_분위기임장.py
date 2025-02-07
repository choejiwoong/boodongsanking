from streamlit.components.v1 import iframe
import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_icon="🚶‍♂️",
    page_title="분위기임장",
    layout="wide",
)

st.header("분위기임장")

# Google My Maps 공유 링크 (여기에 본인 지도 URL 입력)
google_maps_url = "https://www.google.com/maps/d/embed?mid=1GqeLe9S_dDf0zRAuGrbK5TNhuyIKBIs&usp=sharing"  # 네 지도 URL로 변경!

# Streamlit에서 지도 표시 (iframe 사용)
st.components.v1.iframe(google_maps_url, width=800, height=600)

# 초기 데이터프레임 생성
data = {
    "카테고리": ["직장", "", "교통", "학군", "", "환경", "", "", "", "", ""],
    "세부 항목": [
        "직장의 규모", "직장인의 모습",
        "출퇴근 혼잡도",
        "학원가의 종류", "면학 분위기",
        "택지", "거주지 상권", "유해 시설", "지형", "거주민 분위기 (연령대)"
    ],
    "상": [False, False, False, False, False, False, False, False, False, False],
    "중": [False, False, False, False, False, False, False, False, False, False],
    "하": [False, False, False, False, False, False, False, False, False, False]
}

st.subheader("📌 분위기임장 체크리스트")

# ✅ 각 열의 길이를 맞춤 (10행으로 통일)
data = {
    "카테고리": ["직장", "직장", "교통", "학군", "학군", "환경", "환경", "환경", "환경", "환경"],
    "세부 항목": [
        "직장의 규모", "직장인의 모습",
        "출퇴근 혼잡도",
        "학원가의 종류", "면학 분위기",
        "택지", "거주지 상권", "유해 시설", "지형", "거주민 분위기 (연령대)"
    ],
    "상": [False] * 10,
    "중": [False] * 10,
    "하": [False] * 10,
    "비고": [  # 추가 설명
        "정장, 작업복",
        "",
        "",
        "영재학원, 입시컨설팅(플랜카드)",
        "입시플랜카드, 대형학원",
        "",
        "유기농마트, 초록마을, 한살림, 명품의류편집샵, 필라테스샵, 네일샵, 영어유치원, 영어학원, 정신과, 심리치료",
        "유흥시설, 공장, 교도소, 비행장 등",
        "",
        "옷차림, 표정, 말투"
    ],
}

# DataFrame 생성
df = pd.DataFrame(data)

# ✅ 체크박스 포함된 데이터프레임 (수정 가능)
edited_df = st.data_editor(df, key="checklist", num_rows="dynamic")

# ✅ 선택된 체크박스 개수 개별 합산
total_high = edited_df["상"].sum()
total_mid = edited_df["중"].sum()
total_low = edited_df["하"].sum()

# ✅ 체크 개수 출력
check_text = f"상: {int(total_high)} 개 / 중: {int(total_mid)} 개 / 하: {int(total_low)} 개"

# ✅ 추가 의견 입력
additional_comments = st.text_area("📝 추가 의견 입력", value=check_text)