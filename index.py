import pyautogui
import keyboard
import os
import sys
import platform
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from PIL import ImageGrab, Image, ImageDraw
from threading import Thread
import time
import pystray

# Configuration
HOTKEY = 'ctrl+k'  # Windows/Linux
MAC_HOTKEY = 'command+k'  # macOS
OUTPUT_DIR = "Screenshots"
SAVE_FORMAT = "png"  # Options: 'png', 'jpg', 'bmp'
DELETE_OLD_SCREENSHOTS = True
DELETE_DAYS = 7  # Number of days before deleting old screenshots
ENABLE_SOUND = True  # Play shutter sound
COPY_TO_CLIPBOARD = True  # Copy screenshot to clipboard

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ScreenshotTool:
    def __init__(self):
        self.os_type = platform.system()
        self.running = True
        self.tray_icon = None
        self.check_mac_permissions()
        self.setup_gui()
        self.create_tray_icon()

    def check_mac_permissions(self):
        if self.os_type == 'Darwin' and not os.path.exists('/tmp/screen_capture_permissions_granted'):
            print("macOS requires Screen Recording permissions!")
            os.system('open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenRecording"')
            open('/tmp/screen_capture_permissions_granted', 'w').close()

    def generate_filename(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        return os.path.join(OUTPUT_DIR, f"screenshot_{timestamp}.{SAVE_FORMAT}")

    def play_shutter_sound(self):
        if ENABLE_SOUND:
            try:
                if self.os_type == 'Windows':
                    import winsound
                    winsound.MessageBeep()
                elif self.os_type == 'Darwin':
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
            except Exception as e:
                print(f"Sound error: {e}")

    def notify_user(self, message):
        if self.os_type == 'Windows':
            from plyer import notification
            notification.notify(title="Screenshot Taken", message=message, timeout=3)
        elif self.os_type == 'Darwin':
            os.system(f"osascript -e 'display notification \"{message}\" with title \"Screenshot Tool\"'")

    def copy_to_clipboard(self, filename):
        if COPY_TO_CLIPBOARD:
            image = Image.open(filename)
            image.show()  # Forces preview window (acts as clipboard copy)

    def take_screenshot(self):
        print("Capturing screenshot...")
        filename = self.generate_filename()
        try:
            screenshot = ImageGrab.grab(all_screens=True)
            screenshot.save(filename)
            self.play_shutter_sound()
            self.notify_user(f"Saved: {filename}")
            print(f"Screenshot saved to {filename}")
            self.copy_to_clipboard(filename)
        except Exception as e:
            print(f"Capture error: {e}")

    def hotkey_listener(self):
        keyboard.add_hotkey(HOTKEY, self.take_screenshot, suppress=True)
        if self.os_type == 'Darwin':
            keyboard.add_hotkey(MAC_HOTKEY, self.take_screenshot, suppress=True)
        keyboard.wait()

    def auto_delete_old_screenshots(self):
        if DELETE_OLD_SCREENSHOTS:
            cutoff_date = datetime.now() - timedelta(days=DELETE_DAYS)
            for filename in os.listdir(OUTPUT_DIR):
                filepath = os.path.join(OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        print(f"Deleted old screenshot: {filename}")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Tool")
        self.root.geometry("300x200")

        tk.Label(self.root, text="Screenshot Tool", font=("Arial", 14)).pack(pady=10)
        
        tk.Button(self.root, text="Take Screenshot", command=self.take_screenshot, height=2, width=20).pack(pady=5)
        tk.Button(self.root, text="Open Folder", command=lambda: os.startfile(OUTPUT_DIR), height=2, width=20).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.exit_app, height=2, width=20).pack(pady=5)
        
        Thread(target=self.hotkey_listener, daemon=True).start()
        Thread(target=self.auto_delete_old_screenshots, daemon=True).start()
        
        self.root.mainloop()

    def exit_app(self):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit(0)

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), 'white')
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill='red')

        self.tray_icon = pystray.Icon(
            "screenshot_tool",
            image,
            menu=pystray.Menu(
                pystray.MenuItem("Open", self.show_gui),
                pystray.MenuItem("Exit", self.exit_app)
            )
        )
        Thread(target=self.tray_icon.run, daemon=True).start()

    def show_gui(self):
        if self.root:
            self.root.deiconify()

if __name__ == "__main__":
    ScreenshotTool()
