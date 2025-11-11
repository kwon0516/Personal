import pyautogui
import keyboard
import time
import mouse

def get_rgb_at_cursor():
    x, y = pyautogui.position()
    return pyautogui.screenshot().getpixel((x, y))

def main():
    global region
    x1, y1, x2, y2 = 0, 0, 0, 0
    while True:
        if mouse.is_pressed(button='left'):
            x1, y1 = pyautogui.position()
            print("1st end")
            break
    time.sleep(0.5)

    while True:
        if mouse.is_pressed(button='left'):
            x2, y2 = pyautogui.position()
            print("2nd end")
            break
    time.sleep(0.5)

    # 좌표 정리
    left, top = min(x1, x2), min(y1, y2)
    width, height = abs(x2 - x1), abs(y2 - y1)
    region = (left, top, width, height)
    print(f"영역 지정 완료: {region}")
    # ============================== #
    
    print("Alt+G를 누르면 감지 시작")
    keyboard.wait('alt+g')
    print("감지 시작!")
    x = left + width // 2
    y = top + height // 2
    img = pyautogui.screenshot(region=region)
    base_rgb = img.getpixel((x - left, y - top))
    print(f"기준 RGB: {base_rgb} at ({x}, {y})")
    # x, y = pyautogui.position()
    # base_rgb = pyautogui.screenshot(region=region).getpixel((x, y))
    # print(f"기준 RGB: {base_rgb} at ({x}, {y})")

    while True:
        if keyboard.is_pressed('esc'):
            print("종료합니다.")
            break
        current_rgb = pyautogui.screenshot().getpixel((x, y))
        if current_rgb != base_rgb:
            print(f"RGB 변화 감지! {base_rgb} -> {current_rgb}")
            pyautogui.click(x, y)
            
        # time.sleep(0.05)  # 너무 빠른 반복 방지

if __name__ == "__main__":
	main()
