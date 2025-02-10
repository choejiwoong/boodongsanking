import pandas as pd
import streamlit as st
from streamlit.components.v1 import iframe

# 페이지 기본 설정
st.set_page_config(
    page_icon="🎓",
    page_title="학군분석",
    layout="wide",
)

if 'selected_sido' not in st.session_state:
    st.session_state.selected_sido = None
if 'selected_sigungu' not in st.session_state:
    st.session_state.selected_sigungu = None

if 'fetch_school_achievement' not in st.session_state:
    st.session_state.fetch_school_achievement = None
if 'school_achievement_ranking' not in st.session_state:
    st.session_state.school_achievement_ranking = None

if st.session_state.fetch_school_achievement:
    df = pd.DataFrame(data=st.session_state.fetch_school_achievement)
    # ==============================================================================
    # 광역시별 중학교 학업성취도
    # ==============================================================================
    st.subheader('광역시별 중학교 학업성취도')
    special_city_df = df[df['구분'].str.contains('광역시')]

    # 학업성취도 평균을 float 형식으로 변환
    special_city_df['학업성취도 평균'] = pd.to_numeric(special_city_df['학업성취도 평균'].str.strip("%"), errors='coerce')

    # 95% 이상인 학교 필터링 후 각 광역시별 개수 계산
    achievement_counts = special_city_df[special_city_df['학업성취도 평균'] >= 95] \
        .groupby('구분').size() \
        .reindex(special_city_df['구분'].unique())

    # NaN을 0으로 처리한 후, 정수형으로 변환
    achievement_counts = achievement_counts.fillna(0).astype(int)

    # 내림차순 정렬 후, 동일 수치는 ' = '로 묶기
    sorted_counts = achievement_counts.groupby(achievement_counts).apply(lambda x: ' = '.join(x.index)).to_dict()

    # 95% 이상 중학교 수 요약
    achievement_summary = ' > '.join(
        [f"{cities}: {count}개" for count, cities in sorted(sorted_counts.items(), key=lambda x: x[0], reverse=True)]
    )

    # 학업성취도 평균을 다시 0.0% 형식으로 변환하여 추가 컬럼 생성
    special_city_df['학업성취도 평균'] = special_city_df['학업성취도 평균'].apply(lambda x: f"{x:.1f}%")  # 0.0% 형식

    # 출력: 전체 데이터를 보여주고, 15개 제한 없애기
    special_city_df.set_index('구분', inplace=True)
    st.dataframe(special_city_df, use_container_width=True)

    # 학업성취도 95% 이상 중학교 수 요약 출력
    st.text_area("📝 학업성취도 평균 95% 이상 중학교 수", value=achievement_summary)

    # ==============================================================================
    # 시군구별 중학교 학업성취도
    # ==============================================================================
    st.subheader(f'{st.session_state.selected_sigungu} 중학교 학업성취도')
    df = pd.DataFrame(data=st.session_state.fetch_school_achievement)
    # no_special_city_df = df[df['구분'] == .selected_sigungu]
    # selected_sigungu 값이 '전체'가 아니면 필터링하여 해당 값만 가져오기
    if st.session_state.selected_sigungu != '전체':
        # selected_sigungu에 맞는 데이터만 필터링
        selected_sigungu_df = df[df['구분'] == st.session_state.selected_sigungu]
        no_special_city_df = df[~df['구분'].str.contains('광역시')]

        # 학업성취도 컬럼을 숫자형으로 변환
        no_special_city_df['학업성취도 평균'] = no_special_city_df['학업성취도 평균'].str.strip('%').astype(float)

        # 기준에 맞는 조건을 설정
        criteria = [(95, '95% 이상'), (90, '90% 이상'), (85, '85% 이상'), (80, '80% 이상')]

        result = {}

        # 구분별로 데이터를 처리
        for sigungu in no_special_city_df['구분'].unique():
            sigungu_df = no_special_city_df[no_special_city_df['구분'] == sigungu]
            result[sigungu] = {}
            # 이미 카운트된 학교를 추적할 세트 생성
            counted_schools = set()
            total_count = 0  # 모든 기준을 만족하는 중학교 수를 더할 변수

            for i, (threshold, label) in enumerate(criteria):
                # 첫 번째 기준은 그냥 그 이상
                if i == 0:
                    count = len(sigungu_df[sigungu_df['학업성취도 평균'] >= threshold])
                else:
                    prev_threshold = criteria[i - 1][0]
                    # 현재 기준 값보다 크고 이전 기준 값보다 작은 경우
                    count = len(
                        sigungu_df[(sigungu_df['학업성취도 평균'] >= prev_threshold) &
                                   (sigungu_df['학업성취도 평균'] < threshold)])

                # 이미 카운트된 학교를 제외하고 새로 카운트하기
                count = len([school for school in sigungu_df[sigungu_df['학업성취도 평균'] >= threshold]['학교명']
                             if school not in counted_schools])

                # 현재 기준을 만족하는 학교들을 counted_schools에 추가
                for school in sigungu_df[sigungu_df['학업성취도 평균'] >= threshold]['학교명']:
                    counted_schools.add(school)

                # 해당 기준에 대한 결과 저장
                result[sigungu][label] = count
                # 모든 기준을 만족하는 학교 수 합산
                total_count += count

            # 80% 이상 중학교 수
            result[sigungu]['합계'] = total_count
            # 각 시군구의 총 중학교 수
            result[sigungu]['80% 이상 비율'] = f"{(total_count / len(sigungu_df)) * 100:.0f}%"

        # 결과를 DataFrame으로 변환
        result_df = pd.DataFrame(result).T
        # 1️⃣ 각 기준별 개수 합산
        result_df["90% 이상 총합"] = result_df["95% 이상"] + result_df["90% 이상"]
        result_df["85% 이상 총합"] = result_df["90% 이상 총합"] + result_df["85% 이상"]
        result_df["80% 이상 총합"] = result_df["85% 이상 총합"] + result_df["80% 이상"]

        # 2️⃣ 기준에 맞는 시군구 리스트 추출 (우선순위대로)
        sigungu_90_over_5 = set(result_df.index[result_df["90% 이상 총합"] >= 5])
        sigungu_85_over_5 = set(
            result_df.index[(result_df["85% 이상 총합"] >= 5) & (result_df["90% 이상 총합"] < 5)]) - sigungu_90_over_5
        sigungu_85_under_5 = set(result_df.index[(result_df["85% 이상 총합"] < 5) & (
                    result_df["85% 이상 총합"] > 0)]) - sigungu_90_over_5 - sigungu_85_over_5
        sigungu_85_zero = set(
            result_df.index[result_df["85% 이상 총합"] == 0]) - sigungu_90_over_5 - sigungu_85_over_5 - sigungu_85_under_5

        # 3️⃣ 리스트를 쉼표로 구분된 문자열로 변환
        achievement_summary = (
            "📌 학업성취도 요약\n"
            f"- 90% 이상 5개 이상: {', '.join(sorted(sigungu_90_over_5)) if sigungu_90_over_5 else '없음'}\n"
            f"- 85% 이상 5개 이상: {', '.join(sorted(sigungu_85_over_5)) if sigungu_85_over_5 else '없음'}\n"
            f"- 85% 이상 5개 미만: {', '.join(sorted(sigungu_85_under_5)) if sigungu_85_under_5 else '없음'}\n"
            f"- 85% 이상 0개: {', '.join(sorted(sigungu_85_zero)) if sigungu_85_zero else '없음'}"
        )

        selected_sigungu_df['학업성취도 평균'] = selected_sigungu_df['학업성취도 평균'].apply(
            lambda x: f"{float(x.strip('%')):.1f}%" if isinstance(x, str) else f"{x:.1f}%"
        )
        selected_sigungu_df.set_index("구분", inplace=True)
        st.dataframe(selected_sigungu_df, use_container_width=True)  # 시군구별 중학교는 전체 출력
        st.subheader(f"{st.session_state.selected_sido} 중학교 학업성취도")
        st.dataframe(result_df, use_container_width=True)
        st.text_area("📝 학업성취도 평가", value=achievement_summary)
        st.subheader(f"{st.session_state.selected_sido} 학원가 분포")
        # 통계지리정보서비스 생활업종 통계지도
        st.markdown("""
        <style>
        .stylish-button {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 14px 28px;
            font-size: 18px;
            font-weight: bold;
            color: white !important;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            border-radius: 10px;
            text-decoration: none;
            transition: 0.3s;
            margin-bottom: 30px; /* 버튼 아래 여백 추가 */
        }
        .stylish-button:hover {
            background: linear-gradient(135deg, #5a7be0, #9168d8);
        }
        </style>
        <a class="stylish-button" href="https://sgis.kostat.go.kr/view/bizStats/bizStatsMap" target="_blank">
            🚀 통계지리정보서비스 생활업종 통계지도로 이동
        </a>
        """, unsafe_allow_html=True)
        st.text_area("📝 학원가 분포 평가")

        st.subheader(f"{st.session_state.selected_sigungu} 학군(초등학교/중학교)")
        # Google My Maps 공유 링크 (여기에 본인 지도 URL 입력)
        google_maps_url = "https://www.google.com/maps/d/embed?mid=1GqeLe9S_dDf0zRAuGrbK5TNhuyIKBIs&usp=sharing"  # 내 지도 URL로 변경!

        # Streamlit에서 지도 표시 (iframe 사용)
        st.components.v1.iframe(google_maps_url, width=800, height=600)
        st.text_area("📝 중학교 학군 평가")

        ######################################## 여기서 부터 코딩
        # "https: // www.schoolinfo.go.kr / ng / go / pnnggo_a01_l0.do" <= 여기 참고할것

        st.text_area("📝 초등학교 학군 평가")

if st.session_state.school_achievement_ranking:
    st.subheader(f"학군 SUMMARY: {st.session_state.school_achievement_ranking['등급']}")
    st.text_area("지역 내에서 학군지로 선호하는 동네는?")
    st.text_area("학군을 이유로 외부지역에서 넘어오는가?")
    st.text_area("SUMMARY")

