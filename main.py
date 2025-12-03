import matplotlib.pyplot as plt
from matplotlib import rc
import streamlit as st

# 한글 폰트 설정
rc('font', family='Malgun Gothic')  # Windows 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# Streamlit 앱
def main():
    st.title("한글 폰트 설정 예제")
    st.text("Windows에서 한글 폰트가 올바르게 표시됩니다.")

    # 예제 차트
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1])
    ax.set_title("한글 차트 제목")
    st.pyplot(fig)

if __name__ == '__main__':
    main()
