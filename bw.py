import time
import mss
import pyautogui
import winsound

STATUS_PIXEL = (613, 998)  # 状态检测
AVAILABLE_COLOR = (255, 102, 153)  # 有票状态颜色
UNAVAILABLE_COLOR = (231, 231, 231)  # 无票状态颜色
LOADING_COLOR = (255, 255, 255)  # 加载中状态颜色
REFRESH_DELAY = 0.1  # 刷新后等待时间
CHECK_INTERVAL = 0.05  # 检测间隔
MAX_LOADING_WAIT = 10  # 最大等待加载时间
RETRY_PIXEL = (432, 797)  # 重试坐标


def get_pixel_color(x, y):
    with mss.mss() as sct:
        monitor = {"left": x, "top": y, "width": 1, "height": 1}
        screenshot = sct.grab(monitor)
        return screenshot.pixel(0, 0)[:3]


def refresh_page():
    pyautogui.hotkey('f5')
    time.sleep(REFRESH_DELAY)
    return time.time()


def click_position(x, y):
    pyautogui.click(x, y)


last_refresh_time = 0  # 记录上次刷新时间
loading_start_time = 0  # 记录开始加载时间

try:
    time.sleep(2)
    while True:
        current_color = get_pixel_color(*STATUS_PIXEL)

        if current_color == AVAILABLE_COLOR:
            pyautogui.click(*STATUS_PIXEL)
            time.sleep(0.01)
            pyautogui.click(239, 516)
            pyautogui.click(506, 509)
            pyautogui.click(121, 618)
            pyautogui.click(*STATUS_PIXEL)
            success_detected = False
            time.sleep(0.1)
            pyautogui.click(*STATUS_PIXEL)
            time.sleep(0.1)
            pyautogui.click(*STATUS_PIXEL)
            start_time = time.time()
            time.sleep(0.05)
            x = False
            while True:
                current_color = get_pixel_color(*RETRY_PIXEL)
                error_color = get_pixel_color(618, 569)
                gr_color = get_pixel_color(*STATUS_PIXEL)
                if current_color == AVAILABLE_COLOR:
                    pyautogui.click(*RETRY_PIXEL)
                elif gr_color == (127, 51, 76):
                    x = True
                    pyautogui.click(431, 759)
                    break
                elif error_color == (51, 51, 51):
                    break
                elif not success_detected and gr_color == (255, 255, 255):
                    pyautogui.click(*STATUS_PIXEL)
                    winsound.Beep(frequency=3000, duration=300)
                    success_detected = True
                if time.time() - start_time > 5:
                    break
                time.sleep(0.05)
            if x:
                pyautogui.click(414, 758)
            else:
                pyautogui.click(60, 137)
            time.sleep(0.2)
            last_refresh_time = refresh_page()
            loading_start_time = 0
        elif current_color == UNAVAILABLE_COLOR:
            loading_start_time = 0
            if time.time() - last_refresh_time > REFRESH_DELAY:
                last_refresh_time = refresh_page()

        elif current_color == (127, 51, 76):
            pyautogui.click(431, 759)

        elif current_color == LOADING_COLOR:
            if loading_start_time == 0:
                loading_start_time = time.time()

            if time.time() - loading_start_time > MAX_LOADING_WAIT:
                last_refresh_time = refresh_page()
                loading_start_time = 0

        else:
            print(f"检测到意外颜色: {current_color} - 等待状态稳定")
            if time.time() - last_refresh_time > MAX_LOADING_WAIT:
                last_refresh_time = refresh_page()
                loading_start_time = 0

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\n程序已手动终止")
