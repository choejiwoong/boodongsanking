import streamlit as st
import folium
from streamlit.components.v1 import iframe
import pandas as pd
from folium import Icon, Popup, IFrame, Tooltip
# 위경도는 여기 참고
# https://blog.naver.com/kiakass/222449339999

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏖",
    page_title="환경분석",
    layout="wide",
)

st.header("환경분석")




# Tooltip HTML 내용 (마우스 올렸을 때 표시)
#     <div style="font-family: 'Do Hyeon', sans-serif;
#                 font-size: 12px;
#                 line-height: 1.6;
#                 color: black;
#                 white-space: nowrap;">
tooltip_html_apt1 = """
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <div style="font-size: 12px; 
                    white-space: nowrap;">
            <strong>연산롯데캐슬골드포레</strong>
        </div>
        <div style="font-size: 12px; 
                    white-space: nowrap;
                    margin-top: 10px;">
            <strong>\n5.5/4.3</strong>
        </div>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Do+Hyeon&display=swap" rel="stylesheet">
"""

# 지도 생성 (부산시 연제구 중심)
map_center = [35.17318611, 129.082075]
m = folium.Map(location=map_center, zoom_start=13.5)

# 마커에 Tooltip 추가 (마우스 올렸을 때 표시)
# {'pink', 'gray', 'darkgreen', 'lightgray', 'green', 'black', 'orange', 'lightblue', 'lightgree', 'purple', 'darkblue', 'cadetblue', 'darkred', 'beige', 'darkpurple', 'red', 'blue', 'white', 'lightred'}.
folium.Marker(
    [35.173883, 129.081865],
    tooltip=Tooltip(tooltip_html_apt1, sticky=True),
    icon=Icon(color="beige", icon='landmark', prefix='fa')
).add_to(m)

# folium 지도를 HTML로 변환하여 Streamlit에 표시
m.save('map_with_tooltip.html')

# 지도 HTML 불러오기
with open('map_with_tooltip.html', 'r', encoding='utf-8') as f:
    map_html = f.read()

# Streamlit에서 지도 표시
st.components.v1.html(map_html, width=700, height=500)
