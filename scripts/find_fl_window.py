import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user32.EnumWindows.argtypes = [WNDENUMPROC, ctypes.c_void_p]
user32.EnumWindows.restype = ctypes.c_bool

windows = []

def enum_windows_callback(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)
    cls = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls, 256)
    is_vis = user32.IsWindowVisible(hwnd)
    windows.append({
        "hwnd": hwnd,
        "pid": pid.value,
        "title": title.value,
        "class": cls.value,
        "visible": is_vis,
    })
    return True

cb = WNDENUMPROC(enum_windows_callback)
user32.EnumWindows(cb, 0)

print(f"Total windows found: {len(windows)}")
fl_windows = [w for w in windows if w["pid"] == 24808]
print(f"Windows belonging to PID 24808 (FL64): {len(fl_windows)}")
for w in fl_windows:
    print(w)
