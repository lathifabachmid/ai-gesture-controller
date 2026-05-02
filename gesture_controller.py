import cv2
import subprocess
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time

# =============================================
# AI GESTURE CONTROLLER
# by Lathifa Magfirah Bachmid
# =============================================
# GESTURE MAP:
# 0 jari (kepalan)  = Mute / Unmute
# 1 jari (telunjuk) = Next track
# 2 jari (victory)  = Previous track
# 3 jari            = Volume Up
# 4 jari            = Volume Down
# 5 jari (semua)    = Play / Pause
# =============================================

# Helper: kirim media key lewat PowerShell (lebih reliable di Windows)
def media_key(char_code):
    subprocess.Popen([
        'powershell', '-c',
        f'(New-Object -comObject WScript.Shell).SendKeys([char]{char_code})'
    ])

# Setup
detector = HandDetector(maxHands=1, detectionCon=0.7)
cap = cv2.VideoCapture(0)

# Cooldown biar gesture ga kedeteksi berkali-kali
COOLDOWN = 1.2  # detik
last_action_time = 0
last_gesture = -1

# Warna UI
COLOR_GREEN  = (80, 200, 120)
COLOR_BLUE   = (255, 180, 50)
COLOR_RED    = (80, 80, 255)
COLOR_WHITE  = (255, 255, 255)
COLOR_DARK   = (30, 30, 30)
COLOR_PURPLE = (220, 130, 255)


def draw_ui(frame, gesture_name, jumlah_jari, action_text, cooldown_remaining):
    h, w = frame.shape[:2]

    # Background bar atas
    cv2.rectangle(frame, (0, 0), (w, 110), (20, 20, 20), -1)
    cv2.rectangle(frame, (0, 110), (w, 112), COLOR_PURPLE, -1)

    # Judul
    cv2.putText(frame, 'AI Gesture Controller', (14, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLOR_WHITE, 2)
    cv2.putText(frame, 'by Lathifa Magfirah Bachmid', (14, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180, 130, 220), 1)

    # Status jari
    cv2.putText(frame, f'Jari terdeteksi: {jumlah_jari}', (14, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_BLUE, 2)

    # Box gesture name
    if gesture_name:
        cv2.rectangle(frame, (0, h - 110), (w, h), (20, 20, 20), -1)
        cv2.rectangle(frame, (0, h - 112), (w, h - 110), COLOR_PURPLE, -1)

        # Nama gesture
        cv2.putText(frame, f'Gesture: {gesture_name}', (14, h - 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_GREEN, 2)

        # Aksi yang dilakukan
        cv2.putText(frame, f'Action : {action_text}', (14, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_PURPLE, 2)

        # Cooldown bar
        if cooldown_remaining > 0:
            bar_w = int((cooldown_remaining / COOLDOWN) * (w - 28))
            cv2.rectangle(frame, (14, h - 20), (14 + bar_w, h - 10),
                          COLOR_PURPLE, -1)

    # Hint keluar
    cv2.putText(frame, 'Tekan Q untuk keluar', (w - 220, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 120, 120), 1)

    return frame


def get_gesture_info(jumlah_jari, fingers):
    """Return (gesture_name, action_text, action_fn)"""

    if jumlah_jari == 0:
        return "Kepalan Tangan", "Mute / Unmute", \
               lambda: pyautogui.press('volumemute')

    elif jumlah_jari == 1:
        return "1 Jari - Telunjuk", "Next Track", \
               lambda: media_key(176)

    elif jumlah_jari == 2:
        return "2 Jari - Victory", "Previous Track", \
               lambda: media_key(177)

    elif jumlah_jari == 3:
        return "3 Jari", "Volume Up", \
               lambda: pyautogui.press('volumeup')

    elif jumlah_jari == 4:
        return "4 Jari", "Volume Down", \
               lambda: pyautogui.press('volumedown')

    elif jumlah_jari == 5:
        return "5 Jari - Semua", "Play / Pause", \
               lambda: media_key(179)

    return None, None, None


# =============================================
# MAIN LOOP
# =============================================
print("=" * 45)
print("  AI Gesture Controller - Lathifa M. Bachmid")
print("=" * 45)
print("  Gesture yang tersedia:")
print("  0 jari  = Mute / Unmute")
print("  1 jari  = Next Track")
print("  2 jari  = Previous Track")
print("  3 jari  = Volume Up")
print("  4 jari  = Volume Down")
print("  5 jari  = Play / Pause")
print("=" * 45)
print("  Kamera nyala! Arahkan tangan ke kamera.")
print("  Tekan Q untuk keluar.")
print("=" * 45)

current_gesture_name = ""
current_action_text  = ""

cv2.namedWindow('AI Gesture Controller', cv2.WINDOW_NORMAL)
cv2.resizeWindow('AI Gesture Controller', 960, 720)

while True:
    success, frame = cap.read()
    if not success:
        print("Kamera tidak terbaca, coba cek koneksi kamera.")
        break

    frame = cv2.flip(frame, 1)
    hands, frame = detector.findHands(frame)

    now = time.time()
    cooldown_remaining = max(0, COOLDOWN - (now - last_action_time))
    jumlah_jari = 0

    if hands:
        hand    = hands[0]
        fingers = detector.fingersUp(hand)
        jumlah_jari = fingers.count(1)

        gesture_name, action_text, action_fn = get_gesture_info(jumlah_jari, fingers)

        if gesture_name:
            current_gesture_name = gesture_name
            current_action_text  = action_text

            gesture_changed = (jumlah_jari != last_gesture)
            cooldown_done   = (now - last_action_time) > COOLDOWN

            if gesture_changed and cooldown_done:
                action_fn()
                last_action_time = now
                last_gesture     = jumlah_jari
                print(f"  >> Gesture: {gesture_name} | Action: {action_text}")
    else:
        current_gesture_name = ""
        current_action_text  = ""
        last_gesture         = -1

        cv2.putText(frame, 'Arahkan tangan ke kamera...', (14, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)

    frame = draw_ui(frame, current_gesture_name, jumlah_jari,
                    current_action_text, cooldown_remaining)

    cv2.imshow('AI Gesture Controller', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nProgram selesai. Sampai jumpa!")
