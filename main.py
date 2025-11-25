# -*- coding: utf-8 -*-
"""
RFID 기반 음식물쓰레기 데이터 분석을 통한
지역별 탄소발자국 산정 프로그램 - Streamlit 웹앱 버전

필요 패키지: pandas, streamlit
터미널에서:
    pip install pandas streamlit
실행:
    streamlit run rfid_carbon_korea_app.py
"""

import pandas as pd
import streamlit as st

# -------------------------------------------------
# 1. 전역 설정: 음식물쓰레기 1톤당 탄소배출 계수(예시)
# -------------------------------------------------
DEFAULT_EMISSION_FACTOR_PER_TON = 500.0  # 1톤당 500kg CO2e 라고 가정


# -------------------------------------------------
# 2. 데이터 불러오기 + 전처리
# -------------------------------------------------
def load_and_preprocess(uploaded_file) -> pd.DataFrame:
    """
    한국환경공단 '지자체별 RFID 음식물쓰레기 배출량' CSV 파일을 읽고
    기본 전처리를 수행한다.

    예상 컬럼:
    - '배출연도'
    - '배출월'
    - '광역시도'
    - '기초지자체'
    - '배출량(톤)'
    """
    # 한글 CSV라서 encoding="cp949" 또는 "utf-8" 시도
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    required_cols = ["배출연도", "배출월", "광역시도", "기초지자체", "배출량(톤)"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼이 없습니다: {col}")

    # 결측값이 있는 행 제거 (필요시 수정 가능)
    df = df.dropna(subset=required_cols)

    # 숫자형으로 변환 (혹시 문자열이면)
    df["배출연도"] = pd.to_numeric(df["배출연도"], errors="coerce")
    df["배출월"] = pd.to_numeric(df["배출월"], errors="coerce")
    df["배출량(톤)"] = pd.to_numeric(df["배출량(톤)"], errors="coerce")

    # 변환 후 NaN 된 행 제거
    df = df.dropna(subset=["배출연도", "배출월", "배출량(톤)"])

    # 타입 정리
    df["배출연도"] = df["배출연도"].astype(int)
    df["배출월"] = df["배출월"].astype(int)

    return df


# -------------------------------------------------
# 3. 탄소발자국 계산
# -------------------------------------------------
def add_carbon_footprint(df: pd.DataFrame,
                         emission_factor_per_ton: float) -> pd.DataFrame:
    """
    배출량(톤) × 1톤당 탄소배출계수(kg CO2e)를 이용해
    '탄소배출량(kgCO2e)' 컬럼을 추가한다.
    """
    df = df.copy()
    df["탄소배출량(kgCO2e)"] = df["배출량(톤)"] * emission_factor_per_ton
    return df


# -------------------------------------------------
# 4. 집계 함수들
# -------------------------------------------------
def aggregate_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    광역시도 단위로 배출량과 탄소배출량을 합산한다.
    """
    city_stats = df.groupby("광역시도").agg(
        총배출량_톤=("배출량(톤)", "sum"),
        총탄소배출량_kgCO2e=("탄소배출량(kgCO2e)", "sum")
    ).reset_index()

    return city_stats


def aggregate_by_gu(df: pd.DataFrame) -> pd.DataFrame:
    """
    (광역시도, 기초지자체) 단위로 배출량과 탄소배출량을 합산한다.
    """
    gu_stats = df.groupby(["광역시도", "기초지자체"]).agg(
        총배출량_톤=("배출량(톤)", "sum"),
        총탄소배출량_kgCO2e=("탄소배출량(kgCO2e)", "sum")
    ).reset_index()

    return gu_stats


def aggregate_by_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    연-월 단위로 전국 배출량과 탄소배출량을 집계한다.
    """
    ym_stats = df.groupby(["배출연도", "배출월"]).agg(
        총배출량_톤=("배출량(톤)", "sum"),
        총탄소배출량_kgCO2e=("탄소배출량(kgCO2e)", "sum")
    ).reset_index()

    return ym_stats


# -------------------------------------------------
# 5. 감축 시나리오: 배출량 X% 줄이면?
# -------------------------------------------------
def simulate_reduction(df: pd.DataFrame, reduction_rate: float) -> dict:
    """
    전체 배출량을 reduction_rate 비율만큼 줄인다고 가정했을 때
    탄소배출량이 얼마나 줄어드는지 계산한다.

    reduction_rate: 0.1 -> 10% 감축
    반환: 딕셔너리 형태 결과
    """
    original_total = df["탄소배출량(kgCO2e)"].sum()
    reduced_total = original_total * (1 - reduction_rate)
    diff = original_total - reduced_total

    return {
        "원래_총탄소배출량": original_total,
        "감축후_총탄소배출량": reduced_total,
        "감축량": diff,
        "감축률": reduction_rate
    }


# -------------------------------------------------
# 6. Streamlit 메인 앱
# -------------------------------------------------
def main():
    st.set_page_config(page_title="RFID 음식물쓰레기 탄소발자국 분석", layout="wide")
    st.title("📊 RFID 기반 음식물쓰레기 데이터 분석을 통한 지역별 탄소발자국 산정")

    st.markdown(
        """
        이 앱은 **한국환경공단 지자체별 RFID 음식물쓰레기 배출량 CSV 파일**을 업로드하면,

        - 광역시도 / 기초지자체 / 연-월별 배출량을 집계하고  
        - 음식물쓰레기 1톤당 탄소배출 계수(kg CO₂e)를 적용해  
        - **지역별 탄소발자국을 계산**해주는 프로그램입니다.
        """
    )

    # 📂 1) 파일 업로드
    uploaded_file = st.file_uploader(
        "CSV 파일을 업로드하세요 (예: 한국환경공단_지자체별 RFID음식물쓰레기 배출량_....csv)",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("👆 위에서 CSV 파일을 업로드하면 분석을 시작합니다.")
        return

    # ⚙️ 2) 사이드바 설정: 탄소배출 계수 & 감축 시나리오
    st.sidebar.header("⚙️ 분석 설정")

    emission_factor = st.sidebar.number_input(
        "음식물쓰레기 1톤당 탄소배출 계수 (kg CO₂e/톤)",
        min_value=0.0,
        value=float(DEFAULT_EMISSION_FACTOR_PER_TON),
        step=50.0
    )

    reduction_percent = st.sidebar.number_input(
        "감축 시나리오: 가정할 감축률 (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=5.0
    )

    # 📥 3) 데이터 로드 & 전처리
    try:
        df = load_and_preprocess(uploaded_file)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return

    if df.empty:
        st.error("유효한 데이터가 없습니다. CSV 내용을 확인해주세요.")
        return

    st.success(f"데이터 로드 완료! 총 {len(df)}행")
    st.write(f"연도 범위: {df['배출연도'].min()} ~ {df['배출연도'].max()}")

    # 🌍 4) 탄소발자국 계산
    df = add_carbon_footprint(df, emission_factor)

    # 📊 5) 집계
    city_stats = aggregate_by_city(df)
    gu_stats = aggregate_by_gu(df)
    ym_stats = aggregate_by_year_month(df)

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📍 광역시도별 분석", "🏙 시/군/구별 분석", "📆 연-월별 분석", "🌱 감축 시나리오"]
    )

    with tab1:
        st.subheader("광역시도별 총 배출량 및 탄소배출량")
        st.dataframe(city_stats)

        st.markdown("#### 광역시도별 총 탄소배출량 (kg CO₂e)")
        st.bar_chart(data=city_stats.set_index("광역시도")["총탄소배출량_kgCO2e"])

    with tab2:
        st.subheader("(광역시도, 기초지자체)별 총 배출량 및 탄소배출량")
        st.dataframe(gu_stats)

    with tab3:
        st.subheader("연-월별 전국 배출량 및 탄소배출량")
        st.dataframe(ym_stats)

        ym_plot = ym_stats.copy()
        ym_plot["연-월"] = ym_plot["배출연도"].astype(str) + "-" + ym_plot["배출월"].astype(str)
        ym_plot = ym_plot.set_index("연-월")

        st.markdown("#### 연-월별 총 탄소배출량 추이 (kg CO₂e)")
        st.line_chart(ym_plot["총탄소배출량_kgCO2e"])

    with tab4:
        st.subheader("감축 시나리오 분석")

        reduction_rate = reduction_percent / 100.0
        result = simulate_reduction(df, reduction_rate)

        col1, col2, col3 = st.columns(3)
        col1.metric("원래 총 탄소배출량 (kg CO₂e)", f"{result['원래_총탄소배출량']:.2f}")
        col2.metric("감축 후 탄소배출량 (kg CO₂e)", f"{result['감축후_총탄소배출량']:.2f}")
        col3.metric("줄어든 양 (kg C
