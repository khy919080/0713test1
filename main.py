import streamlit as st
import pandas as pd

st.title("🌆 도시 열섬현상 분석 (서울 vs 양평)")

# -------------------------------
# 1. 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

    # 날짜 형식 변환
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

    return seoul, yangpyeong

seoul, yangpyeong = load_data()

# -------------------------------
# 2. 데이터 병합
# -------------------------------
df = pd.merge(
    seoul[["일시", "기온(°C)"]],
    yangpyeong[["일시", "기온(°C)"]],
    on="일시",
    suffixes=("_서울", "_양평")
)

# 기온 차이 계산
df["기온차(서울-양평)"] = df["기온(°C)_서울"] - df["기온(°C)_양평"]

# 시간/월 정보 추가
df["시간"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

# -------------------------------
# 3. 그래프 ①: 연간 기온 변화
# -------------------------------
st.subheader("① 1년간 기온 변화 (서울 vs 양평)")

chart_df = df.set_index("일시")[["기온(°C)_서울", "기온(°C)_양평"]]
st.line_chart(chart_df)

# -------------------------------
# 4. 그래프 ②: 시간별 평균 기온차
# -------------------------------
st.subheader("② 시각별 평균 기온차 (서울 - 양평)")

hourly_diff = df.groupby("시간")["기온차(서울-양평)"].mean()

st.bar_chart(hourly_diff)

# -------------------------------
# 5. 그래프 ③: 월별 평균 기온차
# -------------------------------
st.subheader("③ 월별 평균 기온차 (서울 - 양평)")

monthly_diff = df.groupby("월")["기온차(서울-양평)"].mean()

st.bar_chart(monthly_diff)

# -------------------------------
# 6. 간단한 해석 도움
# -------------------------------
st.markdown("### 🔍 해석 가이드")
st.write("""
- 값이 **양수**이면 → 서울이 더 따뜻함 (열섬현상)
- 값이 **클수록** → 열섬현상이 강함
- 보통 밤에 차이가 더 크게 나타남
""")
