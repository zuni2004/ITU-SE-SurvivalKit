import cv2
import numpy as np
import time
import random
import os
import urllib.request
import math

# ── PIL for Unicode text rendering ──────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── MediaPipe Tasks API ─────────────────────────────────────────────────────
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

BaseOptions = mp_python.BaseOptions
HandLandmarker = mp_vision.HandLandmarker
HandLandmarkerOptions = mp_vision.HandLandmarkerOptions
RunningMode = mp_vision.RunningMode

# ── Model auto-download ──────────────────────────────────────────────────────
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

def _ensure_model() -> None:
    if not os.path.exists(MODEL_PATH):
        print("[INFO] Downloading hand_landmarker.task...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        except Exception as exc:
            raise RuntimeError(f"Download failed: {exc}")

# ── Manual Hand Connections (Bypassing mp.solutions error) ──────────────────
HAND_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)
])

TIP_IDS = [4, 8, 12, 16, 20]
PIP_IDS = [3, 6, 10, 14, 18]

# ── Gesture tables ────────────────────────────────────────────────────────────
GESTURE_MAP = {
    0: ("Fist", "[FIST]"),
    1: ("One", "[1]"),
    2: ("Peace", "[V]"),
    3: ("Three", "[3]"),
    4: ("Four", "[4]"),
}
GESTURE_TAGS = {
    "Fist": "[FIST]", "One": "[1]", "Peace": "[V]", "Three": "[3]",
    "Four": "[4]", "Open Hand": "[Hand-Closed]", "High Five": "[HI-5]",
    "Thumbs Up": "[TU]", "Unknown": "[?]",
}
GAME_TARGETS = ["Fist", "One", "Peace", "Three", "Four", "Open Hand", "High Five", "Thumbs Up"]

# ── UI Helpers ────────────────────────────────────────────────────────────────
def put_text(frame, text, pos, size=24, color=(255, 255, 0)):
    if PIL_AVAILABLE:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(img).text(pos, text, fill=color)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, size/38.0, (color[2], color[1], color[0]), 2)
    return frame

def draw_skeleton(frame, lms, h, w):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in lms]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (60, 200, 60), 2)
    for i, pt in enumerate(pts):
        cv2.circle(frame, pt, 4, (0, 100, 255) if i in TIP_IDS else (240, 240, 240), -1)
    return frame

def draw_bar(frame, progress, pos, size=(240, 24), color=(0, 210, 60)):
    x, y = pos
    bw, bh = size
    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (45, 45, 45), -1)
    cv2.rectangle(frame, (x, y), (x + int(bw * progress), y + bh), color, -1)
    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (170, 170, 170), 1)
    return frame

# ── IMPROVED LOGIC FOR PALM & BACK DETECTION ──────────────────────────────────

def count_fingers(lms: list, side: str) -> tuple:
    """
    Counts fingers using distances from the wrist.
    Works for both Palm and Back of the hand.
    """
    ext = []

    # 1. Thumb Detection (Distance from Thumb Tip to Pinky Knuckle)
    # This distance increases when the thumb is stretched out.
    d_thumb_tip = math.hypot(lms[4].x - lms[17].x, lms[4].y - lms[17].y)
    d_thumb_pip = math.hypot(lms[3].x - lms[17].x, lms[3].y - lms[17].y)
    ext.append(d_thumb_tip > d_thumb_pip)

    # 2. Fingers 2-5 Detection (Distance from Tip to Wrist vs PIP to Wrist)
    # If Tip is further from Wrist than the PIP joint, the finger is extended.
    for i in range(1, 5):
        d_tip = math.hypot(lms[TIP_IDS[i]].x - lms[0].x, lms[TIP_IDS[i]].y - lms[0].y)
        d_pip = math.hypot(lms[PIP_IDS[i]].x - lms[0].x, lms[PIP_IDS[i]].y - lms[0].y)
        ext.append(d_tip > d_pip)

    return sum(ext), ext

def is_fingers_spread(lms) -> bool:
    """Checks if fingers are spread apart (High Five) vs together (Open Hand)."""
    tip_dist = math.hypot(lms[8].x - lms[20].x, lms[8].y - lms[20].y)
    knuckle_dist = math.hypot(lms[5].x - lms[17].x, lms[5].y - lms[17].y)
    if knuckle_dist == 0: return False
    return (tip_dist / knuckle_dist) > 1.6

def classify_gesture(count: int, ext: list, lms: list) -> tuple:
    thumb, index, middle, ring, pinky = ext
    # Thumbs up logic
    if thumb and not any([index, middle, ring, pinky]):
        return "Thumbs Up", "[TU]"
    # Special logic for 5 fingers
    if count == 5:
        if is_fingers_spread(lms):
            return "High Five", "[HI-5]"
        else:
            return "Open Hand", "[Hand-Closed]"
    return GESTURE_MAP.get(count, ("Unknown", "[?]"))

# ── Main Run Functions (Preserving your structure) ───────────────────────────

def run_finger_counter(source) -> None:
    _ensure_model()
    opts = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO, num_hands=2,
        min_hand_detection_confidence=0.6, min_tracking_confidence=0.5
    )
    with HandLandmarker.create_from_options(opts) as det:
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = det.detect_for_video(mp_img, int(cap.get(cv2.CAP_PROP_POS_MSEC)))

            if res.hand_landmarks:
                for i, lms in enumerate(res.hand_landmarks):
                    side = res.handedness[i][0].category_name if res.handedness else "Right"
                    draw_skeleton(frame, lms, h, w)
                    cnt, ext = count_fingers(lms, side)
                    name, tag = classify_gesture(cnt, ext, lms)
                    wx, wy = int(lms[0].x * w), int(lms[0].y * h)
                    frame = put_text(frame, f"{name} {tag}", (wx-50, wy-60))

            cv2.imshow("Module 4 - Palm & Back Detection", frame)
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()
        cv2.destroyAllWindows()

def run_gesture_game(source) -> None:
    _ensure_model()
    score, target, hold_start = 0, random.choice(GAME_TARGETS), None
    opts = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO, num_hands=1
    )
    with HandLandmarker.create_from_options(opts) as det:
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = det.detect_for_video(mp_img, int(cap.get(cv2.CAP_PROP_POS_MSEC)))

            cur = None
            if res.hand_landmarks:
                lms = res.hand_landmarks[0]
                side = res.handedness[0][0].category_name if res.handedness else "Right"
                draw_skeleton(frame, lms, h, w)
                cnt, ext = count_fingers(lms, side)
                cur, _ = classify_gesture(cnt, ext, lms)

            now = time.time()
            if cur == target:
                if hold_start is None: hold_start = now
                progress = min((now - hold_start) / 1.0, 1.0)
                if progress >= 1.0:
                    score += 1
                    target = random.choice(GAME_TARGETS)
                    hold_start = None
            else: hold_start, progress = None, 0.0

            frame = put_text(frame, f"Target: {target}", (20, 20), size=30, color=(0, 255, 255))
            draw_bar(frame, progress, (20, 60))
            cv2.putText(frame, f"Score: {score}", (w-150, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Gesture Game", frame)
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()
        cv2.destroyAllWindows()

def main():
    while True:
        print("\n1. Finger Counter (T1+T2) | 2. Gesture Game (T3) | 0. Exit")
        c = input("Select: ")
        if c == "1": run_finger_counter(0)
        elif c == "2": run_gesture_game(0)
        elif c == "0": break

if __name__ == "__main__":
    main()