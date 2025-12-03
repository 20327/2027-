import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import os

# ✅ 폰트 파일 경로 (리눅스 / Streamlit Cloud)
FONT_PATH = "NanumGothic.ttf"

if os.path.exists(FONT_PATH):
    font_manager.fontManager.addfont(FONT_PATH)
    rc("font", family="NanumGothic")
    font_ok = True
else:
    font_ok = False

plt.rcParams["axes.unicode_minus"] = False


# ✅ 테스트 UI
st.title("한글 폰트 테스트")

if font_ok:
    st.success("✅ 한글 폰트 적용 완료")
else:
    st.error("⚠ NanumGothic.ttf 파일이 없습니다. 프로젝트 폴더에 업로드하세요.")

# ✅ 테스트 차트
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [3, 2, 1])
ax.set_title("한글 차트 제목")
ax.set_xlabel("가로축")
ax.set_ylabel("세로축")

st.pyplot(fig)
