import cv2
import numpy as np
import math
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options

def lips_detection_module():
    """
    Module 1: Lips Detection
    Contains all logic for Smile Detection, MAR Tracking, and Lip-Sync Counting.
    Includes internal menu for selecting input source.
    """
    
    # --- Global Constants ---
    MODEL_ASSET_PATH = "face_landmarker.task"

    # Setup shortcuts 
    BaseOptions = base_options.BaseOptions
    FaceLandmarker = vision.FaceLandmarker
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions
    VisionRunningMode = vision.RunningMode

    def calculate_distance(p1, p2):
        """Calculates the Euclidean distance between two 2D points."""
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def get_mouth_metrics(face_landmarks_list, w, h):
        """
        Extracts landmarks and calculates MAR and Smile status.
        """
        def get_coords(index):
            pt = face_landmarks_list[index]
            return (int(pt.x * w), int(pt.y * h))

        p_upper, p_lower = get_coords(13), get_coords(14)
        p_left, p_right = get_coords(78), get_coords(308)

        vert_dist = calculate_distance(p_upper, p_lower)
        horiz_dist = calculate_distance(p_left, p_right)
        mar = vert_dist / horiz_dist if horiz_dist > 0 else 0.0

        mouth_center_y = (p_upper[1] + p_lower[1]) / 2
        corners_y = (p_left[1] + p_right[1]) / 2
        is_smiling = (mouth_center_y - corners_y) > 2.0
        
        return mar, is_smiling, [p_upper, p_lower, p_left, p_right]

    def module1_lips_detection_image(image_path):
        if not os.path.exists(image_path):
            print(f"Error: Path '{image_path}' not found.")
            return

        frame = cv2.imread(image_path)
        if frame is None:
            print("Error: Could not read image.")
            return

        h, w, _ = frame.shape
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
            running_mode=VisionRunningMode.IMAGE
        )

        with FaceLandmarker.create_from_options(options) as landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            results = landmarker.detect(mp_image)

            smile_label = "Neutral"
            mar_display = 0.0
            draw_red_border = False

            if results.face_landmarks:
                mar, is_smiling, pts = get_mouth_metrics(results.face_landmarks[0], w, h)
                mar_display = mar
                if mar > 0.55: draw_red_border = True
                if is_smiling: smile_label = "Smiling"
                for pt in pts: cv2.circle(frame, pt, 2, (0, 255, 0), -1)

            if draw_red_border:
                cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 10)

            cv2.putText(frame, f"Expression: {smile_label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"MAR: {mar_display:.2f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow("Module 1: Lips Detection - Image", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def module1_lips_detection(input_source=0):
        cap = cv2.VideoCapture(input_source)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return
        
        # FIX: Get FPS to calculate monotonically increasing timestamps
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30.0
        frame_counter = 0

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
            running_mode=VisionRunningMode.VIDEO
        )

        is_mouth_open = False
        cycle_count = 0
        paused = False

        with FaceLandmarker.create_from_options(options) as landmarker:
            while cap.isOpened():
                if not paused:
                    success, frame = cap.read()
                    if not success:
                        if isinstance(input_source, str): 
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        break

                    h, w, _ = frame.shape
                    
                    # FIX: Generate a strictly increasing timestamp
                    # This prevents the "monotonically increasing" ValueError
                    timestamp_ms = int((1000 / fps) * frame_counter)
                    frame_counter += 1

                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    results = landmarker.detect_for_video(mp_image, timestamp_ms)

                    draw_red_border = False
                    mar_display = 0.0
                    smile_label = "Neutral"

                    if results.face_landmarks:
                        mar, is_smiling, _ = get_mouth_metrics(results.face_landmarks[0], w, h)
                        mar_display = mar
                        if mar > 0.55:
                            draw_red_border = True
                            is_mouth_open = True
                        elif mar < 0.35 and is_mouth_open:
                            cycle_count += 1
                            is_mouth_open = False
                        if is_smiling: smile_label = "Smiling"

                    if draw_red_border:
                        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 10)

                    cv2.putText(frame, f"Expression: {smile_label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    cv2.putText(frame, f"MAR: {mar_display:.2f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"Cycles: {cycle_count}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow("Module 1: Lips Detection", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == 27: # ESC
                    break
                elif key == ord("p"):
                    paused = not paused
                elif key == ord("r"):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    cycle_count = 0

        cap.release()
        cv2.destroyAllWindows()

    # --- Internal Menu for Module 1 ---
    if not os.path.exists(MODEL_ASSET_PATH):
        print(f"Error: Face Landmarker model '{MODEL_ASSET_PATH}' not found.")
        return

    while True:
        print("\n--- Lips Detection Module Menu ---")
        print("1. Live Webcam Feed")
        print("2. Video File Upload")
        print("3. Image Upload")
        print("0. Back to Main Menu")
        
        choice = input("Select Source: ")
        
        if choice == "0":
            break
        elif choice == "1":
            module1_lips_detection(0)
        elif choice == "2":
            path = input("Enter Video Path: ").strip()
            module1_lips_detection(path)
        elif choice == "3":
            path = input("Enter Image Path: ").strip()
            module1_lips_detection_image(path)
        else:
            print("Invalid Choice.")

# Example of how to call the function:
# lips_detection_module()
    

def eyes_detection_module():
    import cv2
    import numpy as np
    import mediapipe as mp
    import time
    import os

    # Import the new MediaPipe Tasks API components
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options

    # --- Global Constants ---
    EAR_THRESHOLD_CLOSED = 0.25
    FRAMES_PER_SECOND = 30
    DROWSY_FRAMES_THRESHOLD = 20
    CLEAR_DROWSY_FRAMES_THRESHOLD = 5

    # --- MediaPipe Tasks Face Landmarker Setup ---
    MODEL_ASSET_PATH = "face_landmarker.task"

    # Ensure the model file exists
    if not os.path.exists(MODEL_ASSET_PATH):
        print(f"Error: Face Landmarker model '{MODEL_ASSET_PATH}' not found.")
        print("Please download it and place it in the same directory.")
        return

    # Configuration for FaceLandmarker
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions
    BaseOptions = base_options.BaseOptions

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1
    )

    # --- Eye landmark indices ---
    LEFT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
    
    DEBUG_LEFT_EYE_POINTS = [362, 385, 387, 263, 373, 380, 382, 381, 374, 390, 249, 398, 397, 396, 403, 404, 405]
    DEBUG_RIGHT_EYE_POINTS = [33, 160, 158, 133, 153, 144, 161, 159, 145, 7, 163, 154, 155, 157, 246]
    VISUALIZE_ALL_DEBUG_POINTS = False

    # --- Helper Functions ---
    def euclidean_distance(point1, point2):
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def calculate_ear(eye_landmarks, face_landmarks_list, img_w, img_h):
        if not all(idx < len(face_landmarks_list) for idx in eye_landmarks):
            return 0.0
        p = []
        for i in eye_landmarks:
            landmark = face_landmarks_list[i]
            x, y = int(landmark.x * img_w), int(landmark.y * img_h)
            p.append((x, y))
        A = euclidean_distance(p[1], p[5])
        B = euclidean_distance(p[2], p[4])
        C = euclidean_distance(p[0], p[3])
        return (A + B) / (2.0 * C) if C != 0 else 0.0

    def process_frame_eyes_detection(frame, face_landmarker_detector, blink_counter_state, drowsy_state):
        img_h, img_w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        results = face_landmarker_detector.detect(mp_image)

        left_ear, right_ear = 0.0, 0.0

        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]
            landmarks_list = face_landmarks

            left_ear = calculate_ear(LEFT_EYE_LANDMARKS, landmarks_list, img_w, img_h)
            right_ear = calculate_ear(RIGHT_EYE_LANDMARKS, landmarks_list, img_w, img_h)

            if left_ear < EAR_THRESHOLD_CLOSED and right_ear < EAR_THRESHOLD_CLOSED:
                blink_counter_state['is_eye_closed'] = True
            elif blink_counter_state['is_eye_closed'] and left_ear > EAR_THRESHOLD_CLOSED and right_ear > EAR_THRESHOLD_CLOSED:
                blink_counter_state['blink_count'] += 1
                blink_counter_state['is_eye_closed'] = False

            if left_ear < EAR_THRESHOLD_CLOSED and right_ear < EAR_THRESHOLD_CLOSED:
                drowsy_state['consecutive_closed_frames'] += 1
                drowsy_state['consecutive_open_frames'] = 0
            else:
                drowsy_state['consecutive_open_frames'] += 1
                if drowsy_state['consecutive_open_frames'] >= CLEAR_DROWSY_FRAMES_THRESHOLD:
                    drowsy_state['is_drowsy_alert_active'] = False
                    drowsy_state['consecutive_closed_frames'] = 0

            if drowsy_state['consecutive_closed_frames'] >= DROWSY_FRAMES_THRESHOLD:
                drowsy_state['is_drowsy_alert_active'] = True

            for eye_indices in [LEFT_EYE_LANDMARKS, RIGHT_EYE_LANDMARKS]:
                for idx in eye_indices:
                    landmark = landmarks_list[idx]
                    cv2.circle(frame, (int(landmark.x * img_w), int(landmark.y * img_h)), 2, (0, 255, 255), -1)

            cv2.putText(frame, f"L-EAR: {left_ear:.3f}", (10, img_h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"R-EAR: {right_ear:.3f}", (10, img_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"Blinks: {blink_counter_state['blink_count']}", (img_w - 180, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        if drowsy_state['is_drowsy_alert_active']:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, img_h // 2 - 50), (img_w, img_h // 2 + 50), (0, 0, 255), -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
            cv2.putText(frame, 'DROWSY! Wake Up!', (img_w // 2 - 200, img_h // 2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        return frame, left_ear, right_ear

    # --- Runners ---
    def run_webcam(detector):
        cap = cv2.VideoCapture(0)
        blink_state = {'blink_count': 0, 'is_eye_closed': False}
        drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            annotated, _, _ = process_frame_eyes_detection(frame, detector, blink_state, drowsy_state)
            cv2.imshow('Eyes Detection', annotated)
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()
        cv2.destroyAllWindows()

    def run_video(path, detector):
        cap = cv2.VideoCapture(path)
        paused, current_pos = False, 0
        blink_state = {'blink_count': 0, 'is_eye_closed': False}
        drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}
        while True:
            if not paused:
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos)
                ret, frame = cap.read()
                if not ret: paused = True; continue
                current_pos += 1
                annotated, _, _ = process_frame_eyes_detection(frame, detector, blink_state, drowsy_state)
                cv2.imshow('Eyes Detection (Video)', annotated)
            key = cv2.waitKey(25) & 0xFF
            if key == ord('p'): paused = not paused
            elif key == ord('r'): current_pos = 0; paused = False
            elif key == 27: break
        cap.release()
        cv2.destroyAllWindows()

    def run_image(path, detector):
        frame = cv2.imread(path)
        if frame is None: return
        blink_state = {'blink_count': 0, 'is_eye_closed': False}
        drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}
        annotated, _, _ = process_frame_eyes_detection(frame, detector, blink_state, drowsy_state)
        cv2.putText(annotated, "Static Image - Blinks & Drowsiness N/A", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('Eyes Detection (Image)', annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # --- Module Execution Logic ---
    try:
        landmarker_detector = vision.FaceLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    while True:
        print("\n--- Eyes Detection Module ---")
        print("1. Live Webcam Feed\n2. Video File Upload\n3. Image Upload\nb. Back")
        choice = input("Choice: ").lower()
        if choice == '1': run_webcam(landmarker_detector)
        elif choice == '2': run_video(input("Video Path: "), landmarker_detector)
        elif choice == '3': run_image(input("Image Path: "), landmarker_detector)
        elif choice == 'b': break

def face_detection_module():
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
                    xs = [lm.x for lm in landmarks]; ys = [lm.y for lm in landmarks]
                    x1, y1 = int(max(min(xs)*w-20, 0)), int(max(min(ys)*h-20, 0))
                    x2, y2 = int(min(max(xs)*w+20, w)), int(min(max(ys)*h+20, h))
                    analysis = DeepFace.analyze(frame[y1:y2, x1:x2], actions=['emotion'], enforce_detection=False, silent=True)
                    
                    bs = results.face_blendshapes[0] if results.face_blendshapes else None
                    curr_emo, curr_conf = pick_emotion(analysis[0]['emotion'], bs, last_state)
                    emotion_history.append((time.time(), curr_emo))
                except: pass

            for pt in landmarks:
                cv2.circle(frame, (int(pt.x*w), int(pt.y*h)), 1, (0, 255, 0), -1)

        now = time.time()
        while emotion_history and now - emotion_history[0][0] > EMOTION_HISTORY_DURATION:
            emotion_history.popleft()

        mood = compute_weighted_mood(list(emotion_history))

        cv2.putText(frame, f"Emotion: {curr_emo} ({curr_conf:.1f}%)", (10, 30), 1, 1.5, (0, 255, 255), 2)
        cv2.putText(frame, f"Head Pose: {pose}", (10, 70), 1, 1.5, (0, 255, 0), 2)
        cv2.putText(frame, f"Recent Mood: {mood}", (10, 110), 1, 1.5, (255, 255, 0), 2)

        return frame, emotion_history, {"emotion": curr_emo, "confidence": curr_conf}

    # ---------------- MAIN EXECUTION LOGIC ----------------
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

    while True:
        print("\n--- Face Detection & Emotion Module ---")
        print("1. Live Webcam Feed")
        print("2. Video File Upload")
        print("3. Image Upload")
        print("0. Exit Module")
        choice = input("Enter your choice: ")

        if choice == '0':
            break
        elif choice == '1':
            cap = cv2.VideoCapture(0)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                frame, history, state = _process_frame(cv2.flip(frame, 1), detector, count, history, state)
                cv2.imshow("Face Detection - Webcam", frame)
                count += 1
                if cv2.waitKey(1) & 0xFF == 27: break
            cap.release()
            cv2.destroyAllWindows()
        elif choice == '2':
            source = input("Enter path to video file: ")
            cap = cv2.VideoCapture(source)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                frame, history, state = _process_frame(frame, detector, count, history, state)
                cv2.imshow("Face Detection - Video", frame)
                count += 1
                if cv2.waitKey(1) & 0xFF == 27: break
            cap.release()
            cv2.destroyAllWindows()
        elif choice == '3':
            source = input("Enter path to image file: ")
            frame = cv2.imread(source)
            if frame is not None:
                frame, _, _ = _process_frame(frame, detector, 0, history, state, force_deepface=True)
                cv2.imshow("Face Detection - Image", frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("Invalid Image Path.")
        else:
            print("Invalid choice.")

    detector.close()

def hand_detection_module():
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

    # ── Manual Hand Connections ──────────────────
    HAND_CONNECTIONS = frozenset([
        (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
        (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)
    ])

    TIP_IDS = [4, 8, 12, 16, 20]
    PIP_IDS = [3, 6, 10, 14, 18]

    GESTURE_MAP = {
        0: ("Fist", "[FIST]"), 1: ("One", "[1]"), 2: ("Peace", "[V]"),
        3: ("Three", "[3]"), 4: ("Four", "[4]"),
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

    # ── Logic ──────────────────────────────────────────────────────────────────
    def count_fingers(lms: list, side: str) -> tuple:
        ext = []
        d_thumb_tip = math.hypot(lms[4].x - lms[17].x, lms[4].y - lms[17].y)
        d_thumb_pip = math.hypot(lms[3].x - lms[17].x, lms[3].y - lms[17].y)
        ext.append(d_thumb_tip > d_thumb_pip)
        for i in range(1, 5):
            d_tip = math.hypot(lms[TIP_IDS[i]].x - lms[0].x, lms[TIP_IDS[i]].y - lms[0].y)
            d_pip = math.hypot(lms[PIP_IDS[i]].x - lms[0].x, lms[PIP_IDS[i]].y - lms[0].y)
            ext.append(d_tip > d_pip)
        return sum(ext), ext

    def is_fingers_spread(lms) -> bool:
        tip_dist = math.hypot(lms[8].x - lms[20].x, lms[8].y - lms[20].y)
        knuckle_dist = math.hypot(lms[5].x - lms[17].x, lms[5].y - lms[17].y)
        return (tip_dist / knuckle_dist) > 1.6 if knuckle_dist != 0 else False

    def classify_gesture(count: int, ext: list, lms: list) -> tuple:
        thumb, index, middle, ring, pinky = ext
        if thumb and not any([index, middle, ring, pinky]): return "Thumbs Up", "[TU]"
        if count == 5:
            return ("High Five", "[HI-5]") if is_fingers_spread(lms) else ("Open Hand", "[Hand-Closed]")
        return GESTURE_MAP.get(count, ("Unknown", "[?]"))

    # ── Runners ───────────────────────────────────────────────────────────────
    def run_finger_counter(source, is_image=False) -> None:
        _ensure_model()
        mode = RunningMode.IMAGE if is_image else RunningMode.VIDEO
        opts = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mode, num_hands=2,
            min_hand_detection_confidence=0.6, min_tracking_confidence=0.5
        )
        with HandLandmarker.create_from_options(opts) as det:
            if is_image:
                frame = cv2.imread(source)
                if frame is None: return
                h, w = frame.shape[:2]
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                res = det.detect(mp_img)
                if res.hand_landmarks:
                    for i, lms in enumerate(res.hand_landmarks):
                        side = res.handedness[i][0].category_name if res.handedness else "Right"
                        draw_skeleton(frame, lms, h, w)
                        cnt, ext = count_fingers(lms, side)
                        name, tag = classify_gesture(cnt, ext, lms)
                        frame = put_text(frame, f"{name} {tag}", (int(lms[0].x*w)-50, int(lms[0].y*h)-60))
                cv2.imshow("Image Detection", frame)
                cv2.waitKey(0)
            else:
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
                            frame = put_text(frame, f"{name} {tag}", (int(lms[0].x*w)-50, int(lms[0].y*h)-60))
                    cv2.imshow("Hand Detection", frame)
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
                        score += 1; target = random.choice(GAME_TARGETS); hold_start = None
                else: hold_start, progress = None, 0.0
                frame = put_text(frame, f"Target: {target}", (20, 20), size=30, color=(0, 255, 255))
                draw_bar(frame, progress, (20, 60))
                cv2.putText(frame, f"Score: {score}", (w-150, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Gesture Game", frame)
                if cv2.waitKey(1) & 0xFF == 27: break
            cap.release()
        cv2.destroyAllWindows()

    # ── Entry Menu ────────────────────────────────────────────────────────────
    while True:
        print("\n--- Hand Detection Module ---")
        print("1. Webcam (Detection)\n2. Video (Detection)\n3. Image (Detection)\n4. Gesture Game (Webcam)\n0. Exit")
        choice = input("Select: ")
        if choice == "1": run_finger_counter(0)
        elif choice == "2": run_finger_counter(input("Video Path: "))
        elif choice == "3": run_finger_counter(input("Image Path: "), is_image=True)
        elif choice == "4": run_gesture_game(0)
        elif choice == "0": break

def main_menu():
    
    while True:
        print("\n------------------------------------------")
        print("SELECT DETECTION MODULE:")
        print("1. Lips Detection (Smile/MAR/Sync)")
        print("2. Eyes Detection (Blink/EAR/Drowsiness)")
        print("3. Face Detection (Emotion/Pose/History)")
        print("4. Hand Detection (Fingers/Gestures/Game)")
        print("b. Back to Input Selection")
        print("------------------------------------------")
            
        mode = input("Select Mode: ").lower()

        if mode == 'b':
            break
        elif mode == '1':
            lips_detection_module()
        elif mode == '2':
            eyes_detection_module()
        elif mode == '3':
            face_detection_module()
        elif mode == '4':
            hand_detection_module()
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    # Ensure the model file exists in the directory
    if not os.path.exists("face_landmarker.task"):
        print("Warning: face_landmarker.task not found in current directory!")
    
    main_menu()