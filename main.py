import streamlit as st
import pandas as pd

st.title("🌆 도시 열섬현상 & ⚡ 전력수요 분석 (2025)")

# -------------------------------
# 1. 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")

    # 날짜 변환
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
    power["일시"] = pd.to_datetime(power["일시"])

    return seoul, yangpyeong, power

seoul, yangpyeong, power = load_data()

# -------------------------------
# 2. 탭 구성
# -------------------------------
tab1, tab2 = st.tabs(["🌆 열섬 분석", "⚡ 전력 연결"])

# ===============================
# [탭1] 열섬 분석
# ===============================
with tab1:
    st.header("🌆 서울 vs 양평 열섬현상 분석")

    # 데이터 병합
    df = pd.merge(
        seoul[["일시", "기온(°C)"]],
        yangpyeong[["일시", "기온(°C)"]],
        on="일시",
        suffixes=("_서울", "_양평")
    )

    # 파생 변수
    df["기온차(서울-양평)"] = df["기온(°C)_서울"] - df["기온(°C)_양평"]
    df["시간"] = df["일시"].dt.hour
    df["월"] = df["일시"].dt.month

    # ① 연간 기온 변화
    st.subheader("① 1년간 기온 변화")
    st.line_chart(df.set_index("일시")[["기온(°C)_서울", "기온(°C)_양평"]])

    # ② 시간별 평균 기온차
    st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
    hourly_diff = df.groupby("시간")["기온차(서울-양평)"].mean()
    st.bar_chart(hourly_diff)

    # ③ 월별 평균 기온차
    st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
    monthly_diff = df.groupby("월")["기온차(서울-양평)"].mean()
    st.bar_chart(monthly_diff)

# ===============================
# [탭2] 전력 연결
# ===============================
with tab2:
    st.header("⚡ 기온과 전력수요의 관계")

    # 데이터 병합 (서울 기온 + 전력)
    df2 = pd.merge(
        seoul[["일시", "기온(°C)"]],
        power[["일시", "전력수요(MWh)"]],
        on="일시"
    )

    # 파생 변수
    df2["월"] = df2["일시"].dt.month

    # ① 산점도 (기온 vs 전력)
    st.subheader("① 기온 vs 전력수요 (산점도)")
    st.scatter_chart(df2, x="기온(°C)", y="전력수요(MWh)")

    # ② 기온 구간별 평균 전력수요
    st.subheader("② 기온 구간별 평균 전력수요")

    # 기온 구간 나누기 (5도 단위)
    bins = list(range(-20, 45, 5))
    df2["기온구간"] = pd.cut(df2["기온(°C)"], bins)

    temp_power = df2.groupby("기온구간")["전력수요(MWh)"].mean()
    st.bar_chart(temp_power)

    # ③ 월별 평균 전력수요
    st.subheader("③ 월별 평균 전력수요")

    monthly_power = df2.groupby("월")["전력수요(MWh)"].mean()
    st.bar_chart(monthly_power)

# -------------------------------
# 하단 설명
# -------------------------------
st.markdown("### 🔍 해석 힌트")
st.write("""
- 🌆 열섬현상: 서울 기온이 양평보다 높을수록 강함
- 🌙 보통 밤에 열섬현상이 더 뚜렷함
- ⚡ 전력수요: 기온이 너무 높거나 낮을 때 증가하는 경향 (냉방/난방)
""")
