import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# ===========================
# ✅ 한글 폰트 설정 (그래프 깨짐 방지)
# ===========================
if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":  # Mac
    plt.rc("font", family="AppleGothic")
else:  # Linux (Streamlit Cloud 등)
    plt.rc("font", family="NanumGothic")

plt.rcParams["axes.unicode_minus"] = False


# ===========================
# ✅ 음식물쓰레기 배출계수
# ===========================
EMISSION_FACTOR_FOOD_WASTE = 0.047  # kgCO2e / kg

st.title("RFID 음식물쓰레기 배출량 시각화 & 탄소발자국 계산기")

st.write("""
한국환경공단 **'지자체별 RFID 음식물쓰레기 배출량' CSV** 파일을 업로드하면  
반기별 탄소발자국과 광역시도별 배출 비율을 그래프로 보여주고,  
직접 입력한 음식물쓰레기 배출량으로 탄소 발생량도 계산합니다.
""")

# ===========================
# ✅ 파일 업로드
# ===========================
uploaded_file = st.file_uploader(
    "한국환경공단 '지자체별 RFID 음식물쓰레기 배출량' CSV 파일을 업로드하세요",
    type=["csv"]
)

if uploaded_file is not None:

    # ===========================
    # ✅ CSV 한글 인코딩 대응
    # ===========================
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    st.subheader("📄 업로드한 데이터 미리보기")
    st.dataframe(df.head())

    # ===========================
    # ✅ 반기 컬럼 생성
    # ===========================
    df["half"] = df["배출월"].apply(lambda m: 1 if m <= 6 else 2)
    df["연도반기"] = df["배출연도"].astype(str) + " H" + df["half"].astype(str)

    # 2017 H1, 2020 H2 제외
    mask = ~((df["배출연도"] == 2017) & (df["half"] == 1)) & \
           ~((df["배출연도"] == 2020) & (df["half"] == 2))
    df_period = df[mask]

    # ===========================
    # ✅ 반기별 집계
    # ===========================
    half_group = (
        df_period
        .groupby("연도반기", as_index=False)["배출량(톤)"]
        .sum()
        .sort_values("연도반기")
    )

    half_group["탄소배출량(tCO2e)"] = half_group["배출량(톤)"] * EMISSION_FACTOR_FOOD_WASTE

    # ===========================
    # ✅ 반기별 그래프
    # ===========================
    st.subheader("📈 반기별 탄소발자국 (2017 H2 ~ 2020 H1)")

    fig1, ax1 = plt.subplots()

    ax1.plot(half_group["연도반기"], half_group["탄소배출량(tCO2e)"], marker="o")

    for x, y in zip(half_group["연도반기"], half_group["탄소배출량(tCO2e)"]):
        ax1.text(x, y, f"{y:,.1f}", ha="center", va="bottom", fontsize=8)

    ax1.set_title("반기별 탄소발자국")
    ax1.set_xlabel("기간 (연도 H반기)")
    ax1.set_ylabel("탄소 배출량 (tCO2e)")
    plt.xticks(rotation=45)

    st.pyplot(fig1)

    # ===========================
    # ✅ 광역시도 파이차트
    # ===========================
    st.subheader("🥧 광역시도별 음식물쓰레기 배출 비율")

    region_group = (
        df_period
        .groupby("광역시도", as_index=False)["배출량(톤)"]
        .sum()
        .sort_values("배출량(톤)", ascending=False)
    )

    fig2, ax2 = plt.subplots(figsize=(6, 6))

    ax2.pie(
        region_group["배출량(톤)"],
        labels=region_group["광역시도"],
        autopct="%.1f%%",
        startangle=90
    )
    ax2.set_title("광역시도별 음식물쓰레기 배출 비율")
    ax2.axis("equal")

    st.pyplot(fig2)

    # ===========================
    # ✅ 전체 탄소 배출량
    # ===========================
    st.subheader("📊 업로드 데이터 기준 전체 탄소배출량")

    total_waste_ton = df_period["배출량(톤)"].sum()
    total_emission_t = total_waste_ton * EMISSION_FACTOR_FOOD_WASTE
    total_emission_kg = total_emission_t * 1000

    st.write(f"- 총 음식물쓰레기 배출량: **{total_waste_ton:,.0f} 톤**")
    st.write(f"- 총 탄소 배출량: **{total_emission_kg:,.1f} kgCO2e**")
    st.write(f"- 총 탄소 배출량: **{total_emission_t:,.2f} tCO2e**")

# ===========================
# ✅ 계산기
# ===========================
st.subheader("🧮 직접 입력하는 음식물쓰레기 탄소발생량 계산기")

waste_kg_input = st.number_input(
    "음식물쓰레기 배출량을 입력하세요 (kg 단위):",
    min_value=0.0,
    step=1.0
)

if st.button("탄소 배출량 계산하기"):
    emission_kg = waste_kg_input * EMISSION_FACTOR_FOOD_WASTE
    emission_ton = emission_kg / 1000

    st.success(f"탄소 배출량: **{emission_kg:.3f} kgCO2e**")
    st.write(f"(= **{emission_ton:.5f} tCO2e**)")
