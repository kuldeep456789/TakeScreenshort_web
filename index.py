import pyautogui
from datetime import datetime
import os

# Directory to save screenshots
output_dir = "Screenshots"
os.makedirs(output_dir, exist_ok=True)

def take_screenshot():
    # Capture the screen
    screenshot = pyautogui.screenshot()

    # Generate a filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(output_dir, f"screenshot_{timestamp}.png")  # Use .png for image files

    # Save the screenshot
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

if __name__ == "__main__":
    print("Press 's' to take a screenshot or 'q' to quit.")
    while True:
        user_input = input("Enter your choice: ").strip().lower()
        if user_input == 's':
            take_screenshot()
        elif user_input == 'q':
            print("Exiting the program.")
            break
        else:
            print("Invalid input. Please press 's' to take a screenshot or 'q' to quit.")
