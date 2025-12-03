import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# ===========================
# ✅ 폰트 파일 경로 직접 지정 (최종 해결)
# ===========================
FONT_PATH = r"C:\Windows\Fonts\MALGUNSL.TTF"

font_prop = font_manager.FontProperties(fname=FONT_PATH)
font_name = font_prop.get_name()

# matplotlib에 폰트 강제 등록
rc("font", family=font_name)

# 마이너스 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False


# ===========================
# ✅ Streamlit 테스트 앱
# ===========================
def main():
    st.title("한글 폰트 최종 테스트")
    st.write("아래 차트의 한글이 정상 출력되면 설정 성공입니다.")

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1])

    ax.set_title("한글 차트 제목")
    ax.set_xlabel("가로축 레이블")
    ax.set_ylabel("세로축 레이블")

    st.pyplot(fig)


if __name__ == "__main__":
    main()
