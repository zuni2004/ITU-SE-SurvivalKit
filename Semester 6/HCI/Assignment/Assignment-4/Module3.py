import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision
from deepface import DeepFace
import time
import collections
import os

# ---------------- CONFIG ----------------
DEEPFACE_INFERENCE_INTERVAL = 10
EMOTION_HISTORY_DURATION = 5
MODEL_PATH = "face_landmarker.task"

NOSE_TIP_INDEX = 1
LEFT_EYE_LANDMARKS_CENTRAL = [33, 133]
RIGHT_EYE_LANDMARKS_CENTRAL = [362, 359]

# Thresholds tuned for the provided sample images
EMOTION_MIN_THRESHOLD = {
    "angry":    10,
    "fear":     10,
    "surprise": 12,
    "sad":      12,
    "happy":    20,
    "neutral":  50,
}

EMOTION_BOOST = {
    "angry":    2.8, 
    "fear":     2.8,
    "surprise": 3.0,
    "sad":      2.5,
    "happy":    1.2,
    "neutral":  0.15,
}

EMOTION_STABILITY_REQUIRED = {
    "angry":    2, "fear": 2, "surprise": 1, "sad": 2, "happy": 1, "neutral": 3
}

EMOTION_HISTORY_WEIGHT = {
    "angry": 4.0, "fear": 4.0, "surprise": 3.5, "sad": 3.0, "happy": 2.0, "neutral": 0.2
}

BLENDSHAPE_CONFIRM_BONUS = 2.0

# MediaPipe Blendshape Indices
BS_BROW_INNER_UP   = 1
BS_BROW_DOWN_L     = 4
BS_BROW_DOWN_R     = 5
BS_EYE_WIDE_L      = 11
BS_EYE_WIDE_R      = 12
BS_JAW_OPEN        = 25
BS_MOUTH_SMILE_L   = 44
BS_MOUTH_SMILE_R   = 45
BS_MOUTH_FROWN_L   = 40
BS_MOUTH_FROWN_R   = 41
BS_MOUTH_UPPER_UP_L= 48
BS_MOUTH_UPPER_UP_R= 49
BS_NOSE_SNEER_L    = 27
BS_NOSE_SNEER_R    = 28

# ---------------- HELPERS ----------------

def get_bs(blendshapes, index):
    if blendshapes and index < len(blendshapes):
        return blendshapes[index].score
    return 0.0

def get_eye_midpoint(landmarks, eye_indices, img_w, img_h):
    xs = [landmarks[i].x * img_w for i in eye_indices if i < len(landmarks)]
    ys = [landmarks[i].y * img_h for i in eye_indices if i < len(landmarks)]
    return (int(np.mean(xs)), int(np.mean(ys))) if xs else None

def estimate_head_pose(landmarks_list, img_w, img_h):
    if not landmarks_list: return "Forward"
    nose = landmarks_list[NOSE_TIP_INDEX]
    nose_x, nose_y = int(nose.x * img_w), int(nose.y * img_h)
    
    left_mp = get_eye_midpoint(landmarks_list, LEFT_EYE_LANDMARKS_CENTRAL, img_w, img_h)
    right_mp = get_eye_midpoint(landmarks_list, RIGHT_EYE_LANDMARKS_CENTRAL, img_w, img_h)
    
    if not left_mp or not right_mp: return "Forward"
    
    avg_eye_x, avg_eye_y = (left_mp[0] + right_mp[0]) // 2, (left_mp[1] + right_mp[1]) // 2
    h_thresh, v_thresh = img_w * 0.03, img_h * 0.05
    
    res_h = "Right" if nose_x < avg_eye_x - h_thresh else "Left" if nose_x > avg_eye_x + h_thresh else ""
    res_v = "Up" if nose_y < avg_eye_y - v_thresh else "Down" if nose_y > avg_eye_y + v_thresh else ""
    
    combined = f"{res_h}-{res_v}".strip("-")
    return combined if combined else "Forward"

def get_blendshape_bonuses(blendshapes):
    bonuses = {}
    jaw = get_bs(blendshapes, BS_JAW_OPEN)
    brow_in = get_bs(blendshapes, BS_BROW_INNER_UP)
    smile = (get_bs(blendshapes, BS_MOUTH_SMILE_L) + get_bs(blendshapes, BS_MOUTH_SMILE_R)) / 2
    frown = (get_bs(blendshapes, BS_MOUTH_FROWN_L) + get_bs(blendshapes, BS_MOUTH_FROWN_R)) / 2
    wide = (get_bs(blendshapes, BS_EYE_WIDE_L) + get_bs(blendshapes, BS_EYE_WIDE_R)) / 2
    upper_lip = (get_bs(blendshapes, BS_MOUTH_UPPER_UP_L) + get_bs(blendshapes, BS_MOUTH_UPPER_UP_R)) / 2
    sneer = (get_bs(blendshapes, BS_NOSE_SNEER_L) + get_bs(blendshapes, BS_NOSE_SNEER_R)) / 2

    if brow_in > 0.25 or frown > 0.2: bonuses["sad"] = BLENDSHAPE_CONFIRM_BONUS
    if smile > 0.4: bonuses["happy"] = BLENDSHAPE_CONFIRM_BONUS
    if jaw > 0.4 and wide > 0.3: bonuses["surprise"] = BLENDSHAPE_CONFIRM_BONUS
    if wide > 0.3 and jaw < 0.4 and brow_in > 0.2: bonuses["fear"] = BLENDSHAPE_CONFIRM_BONUS
    if upper_lip > 0.2 and sneer > 0.1: bonuses["angry"] = BLENDSHAPE_CONFIRM_BONUS
    return bonuses

def pick_emotion(raw_scores, blendshapes, last_state):
    boosted = {e: s * EMOTION_BOOST.get(e, 1.0) for e, s in raw_scores.items() if s >= EMOTION_MIN_THRESHOLD.get(e, 0)}
    if not boosted: boosted = raw_scores
    
    geo_bonuses = get_blendshape_bonuses(blendshapes)
    for e, b in geo_bonuses.items():
        if e in boosted: boosted[e] *= b

    winner = max(boosted, key=boosted.get)
    return winner.capitalize(), raw_scores.get(winner.lower(), 0.0)

def compute_weighted_mood(history):
    if not history: return "N/A"
    scores = collections.defaultdict(float)
    for _, emotion in history:
        scores[emotion] += EMOTION_HISTORY_WEIGHT.get(emotion.lower(), 1.0)
    return max(scores, key=scores.get)

# ---------------- FRAME PROCESSING ----------------

def _process_frame(frame, detector, frame_count, emotion_history, last_state, force_deepface=False):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = detector.detect(mp_img)

    curr_emo = last_state["emotion"]
    curr_conf = last_state["confidence"]
    pose = "Forward"

    if results.face_landmarks:
        landmarks = results.face_landmarks[0]
        pose = estimate_head_pose(landmarks, w, h)
        
        if force_deepface or (frame_count % DEEPFACE_INFERENCE_INTERVAL == 0):
            try:
                # Facial crop for better DeepFace accuracy
                xs = [lm.x for lm in landmarks]; ys = [lm.y for lm in landmarks]
                x1, y1 = int(max(min(xs)*w-20, 0)), int(max(min(ys)*h-20, 0))
                x2, y2 = int(min(max(xs)*w+20, w)), int(min(max(ys)*h+20, h))
                analysis = DeepFace.analyze(frame[y1:y2, x1:x2], actions=['emotion'], enforce_detection=False, silent=True)
                
                bs = results.face_blendshapes[0] if results.face_blendshapes else None
                curr_emo, curr_conf = pick_emotion(analysis[0]['emotion'], bs, last_state)
                emotion_history.append((time.time(), curr_emo))
            except: pass

        # Draw Landmarks
        for pt in landmarks:
            cv2.circle(frame, (int(pt.x*w), int(pt.y*h)), 1, (0, 255, 0), -1)

    # Prune history
    now = time.time()
    while emotion_history and now - emotion_history[0][0] > EMOTION_HISTORY_DURATION:
        emotion_history.popleft()

    mood = compute_weighted_mood(list(emotion_history))

    # Display Overlay
    cv2.putText(frame, f"Emotion: {curr_emo} ({curr_conf:.1f}%)", (10, 30), 1, 1.5, (0, 255, 255), 2)
    cv2.putText(frame, f"Head Pose: {pose}", (10, 70), 1, 1.5, (0, 255, 0), 2)
    cv2.putText(frame, f"Recent Mood: {mood}", (10, 110), 1, 1.5, (255, 255, 0), 2)

    return frame, emotion_history, {"emotion": curr_emo, "confidence": curr_conf}

# ---------------- MAIN MODULES ----------------

def face_detection_module(input_type, source=None):
    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found."); return

    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        output_face_blendshapes=True, num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)
    history = collections.deque()
    state = {"emotion": "Neutral", "confidence": 0.0}
    count = 0

    if input_type == 'webcam':
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame, history, state = _process_frame(cv2.flip(frame, 1), detector, count, history, state)
            cv2.imshow("HCI Detection - Webcam", frame)
            count += 1
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()

    elif input_type == 'image':
        frame = cv2.imread(source)
        if frame is not None:
            # Force DeepFace on the single frame
            frame, _, _ = _process_frame(frame, detector, 0, history, state, force_deepface=True)
            cv2.imshow("HCI Detection - Image", frame)
            cv2.waitKey(0)
        else: print("Invalid Image Path.")

    elif input_type == 'video':
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame, history, state = _process_frame(frame, detector, count, history, state)
            cv2.imshow("HCI Detection - Video", frame)
            count += 1
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()

    cv2.destroyAllWindows()
    detector.close()

def main_menu():
    while True:
        print("\n--- HCI Detection System ---")
        print("1. Webcam")
        print("2. Video File")
        print("3. Image File")
        print("0. Exit")
        choice = input("Select Source: ")
        if choice == '0': break
        
        source = None
        if choice == '1': face_detection_module('webcam')
        elif choice == '2':
            source = input("Path to video: ")
            face_detection_module('video', source)
        elif choice == '3':
            source = input("Path to image: ")
            face_detection_module('image', source)
        else: print("Invalid Choice.")

if __name__ == "__main__":
    main_menu()