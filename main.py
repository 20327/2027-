import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 맑은고딕 Semilight 폰트 경로
FONT_PATH = r"C:\Windows\Fonts\MALGUNSL.TTF"

# 폰트 등록
font_prop = font_manager.FontProperties(fname=FONT_PATH)
font_name = font_prop.get_name()
rc("font", family=font_name)

# 마이너스 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False

# 한글 출력 테스트
plt.figure()
plt.plot([1, 2, 3], [3, 2, 1])
plt.title("한글 제목 테스트")
plt.xlabel("가로축")
plt.ylabel("세로축")
plt.show()
