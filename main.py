import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# 0. Global settings
# --------------------------
# Emission factor: 1 kg food waste -> 0.047 kgCO2e
EMISSION_FACTOR_FOOD_WASTE = 0.047  # kgCO2e / kg


st.title("RFID Food Waste Dashboard")

st.write(
    """
This app visualizes **RFID-based food waste data**  
and estimates the **carbon footprint** using a fixed emission factor.
Upload the K-eco CSV file (지자체별 RFID 음식물쓰레기 배출량).
"""
)

# --------------------------
# 1. File upload
# --------------------------
uploaded_file = st.file_uploader(
    "Upload the K-eco RFID food waste CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    # 2. Load data (Korean encoding) and clean column names
    df = pd.read_csv(uploaded_file, encoding="cp949")
    df.columns = [c.strip() for c in df.columns]

    st.subheader("📄 Data preview")
    st.write("Columns in this file:", list(df.columns))
    st.dataframe(df.head())

    # 3. Check required columns
    required_cols = {"배출연도", "배출월", "광역시도", "기초지자체", "배출량(톤)"}

    if not required_cols.issubset(df.columns):
        st.error(
            "This app expects the original K-eco CSV format with columns: "
            "'배출연도', '배출월', '광역시도', '기초지자체', '배출량(톤)'.\n\n"
            f"Current columns: {list(df.columns)}"
        )
    else:
        # --------------------------
        # 4. Create English region names
        # --------------------------
        region_map = {
            "서울특별시": "Seoul",
            "부산광역시": "Busan",
            "대구광역시": "Daegu",
            "인천광역시": "Incheon",
            "광주광역시": "Gwangju",
            "대전광역시": "Daejeon",
            "울산광역시": "Ulsan",
            "세종특별자치시": "Sejong",
            "경기도": "Gyeonggi",
            "강원도": "Gangwon",
            "충청북도": "Chungbuk",
            "충청남도": "Chungnam",
            "전라북도": "Jeonbuk",
            "전라남도": "Jeonnam",
            "경상북도": "Gyeongbuk",
            "경상남도": "Gyeongnam",
            "제주특별자치도": "Jeju",
        }

        df["Region"] = df["광역시도"].map(region_map).fillna("Other regions")
        df["Municipality"] = df["기초지자체"]

        # --------------------------
        # 5. Half-year period column
        # --------------------------
        df["배출월"] = df["배출월"].astype(int)
        df["half"] = df["배출월"].apply(lambda m: 1 if m <= 6 else 2)
        df["Period"] = df["배출연도"].astype(str) + " H" + df["half"].astype(str)

        # (선택) 2017 H2 ~ 2020 H1 구간만 사용하고 싶다면 필터링
        mask = ~((df["배출연도"] == 2017) & (df["half"] == 1)) & \
               ~((df["배출연도"] == 2020) & (df["half"] == 2))
        df_period = df[mask]

        # --------------------------
        # 6. Line chart: Waste by period (ton)
        # --------------------------
        st.subheader("📈 Food waste by period")

        period_group = (
            df_period
            .groupby("Period", as_index=False)["배출량(톤)"]
            .sum()
            .sort_values("Period")
        )

        fig1, ax1 = plt.subplots()

        ax1.plot(period_group["Period"], period_group["배출량(톤)"], marker="o")

        for x, y in zip(period_group["Period"], period_group["배출량(톤)"]):
            ax1.text(x, y, f"{y:,.0f}", ha="center", va="bottom", fontsize=8)

        ax1.set_title("Carbon footprint (based on food waste)")
        ax1.set_xlabel("Period (Year H1/H2)")
        ax1.set_ylabel("Waste (ton)")  # y축: 배출량(톤) -> Waste (ton)
        plt.xticks(rotation=45)

        st.pyplot(fig1)

        # --------------------------
        # 7. Pie chart: Food waste share by region
        # --------------------------
        st.subheader("🥧 Food waste by region (share)")

        region_group = (
            df_period
            .groupby("Region", as_index=False)["배출량(톤)"]
            .sum()
            .sort_values("배출량(톤)", ascending=False)
        )

        fig2, ax2 = plt.subplots(figsize=(6, 6))

        ax2.pie(
            region_group["배출량(톤)"],
            labels=region_group["Region"],
            autopct="%.1f%%",
            startangle=90,
        )
        ax2.set_title("Food waste by region (ton)")
        ax2.axis("equal")  # keep circle shape

        st.pyplot(fig2)

        # --------------------------
        # 8. Total carbon footprint from the uploaded data
        # --------------------------
        st.subheader("📊 Total carbon footprint (from this dataset)")

        # Total waste (ton) -> convert to kg -> apply emission factor
        total_waste_ton = df_period["배출량(톤)"].sum()
        total_emission_tonCO2e = total_waste_ton * EMISSION_FACTOR_FOOD_WASTE  # tCO2e
        total_emission_kgCO2e = total_emission_tonCO2e * 1000

        st.write(f"- Total food waste: **{total_waste_ton:,.0f} ton**")
        st.write(f"- Total carbon footprint: **{total_emission_kgCO2e:,.1f} kgCO₂e**")
        st.write(f"- Total carbon footprint: **{total_emission_tonCO2e:,.2f} tCO₂e**")

# --------------------------
# 9. Simple calculator (user input)
# --------------------------
st.subheader("🧮 Food waste → carbon footprint calculator")

waste_kg_input = st.number_input(
    "Enter food waste amount (kg):",
    min_value=0.0,
    step=1.0,
)

if st.button("Calculate carbon footprint"):
    emission_kg = waste_kg_input * EMISSION_FACTOR_FOOD_WASTE
    emission_ton = emission_kg / 1000

    st.success(f"Carbon footprint: **{emission_kg:.3f} kgCO₂e**")
    st.write(f"(= **{emission_ton:.5f} tCO₂e**)")
