# Windows専用： ウィンドウのサイズと位置を設定する
# Usage: python winsize.py <正規表現> <X座標> <Y座標> <幅> <高さ>
# タイトルが正規表現にマッチした最初のウィンドウがターゲット

import sys
import re
import win32gui
import win32con

def set_window_size(regex_pattern, x, y, width, height):
    try:
        pattern = re.compile(regex_pattern)
    except re.error as e:
        print(f"Error: Invalid regex pattern: {e}")
        return

    target_hwnd = []

    # コールバック関数
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if pattern.search(title):
                target_hwnd.append(hwnd)
                return False  # 最初に見つかった時点で列挙を終了する
        return True

    # ウィンドウの列挙開始
    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        # callback内でFalseを返すと例外が発生することがあるため、無視して続行
        pass

    if target_hwnd:
        hwnd = target_hwnd[0]
        actual_title = win32gui.GetWindowText(hwnd)
        print(f"Found window: '{actual_title}' (HWND: {hwnd})")

        # 1. 最小化・最大化状態をチェックし、必要なら通常状態に戻す
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 2. ウィンドウを最前面に持ってくる (オプション：操作を確実にするため)
        # win32gui.SetForegroundWindow(hwnd)

        # 3. 位置とサイズの変更
        # 参照: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            x, y, width, height,
            win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW | win32con.SWP_ASYNCWINDOWPOS
        )
        print(f"Moved and resized to: {x}, {y}, {width}x{height}")
    else:
        print(f"No window found matching pattern: {regex_pattern}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python winsize.py <Regex> <X> <Y> <Width> <Height>")
        sys.exit(1)

    try:
        # 引数のパース
        reg_arg = sys.argv[1]
        nx, ny, nw, nh = map(int, sys.argv[2:])

        set_window_size(reg_arg, nx, ny, nw, nh)
    except ValueError:
        print("Error: X, Y, Width, and Height must be integers.")

