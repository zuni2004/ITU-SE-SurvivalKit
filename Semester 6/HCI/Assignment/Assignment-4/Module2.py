import cv2
import numpy as np
import mediapipe as mp
import time
import os

# Import the new MediaPipe Tasks API components
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options

# --- Global Constants (for easier modification and consistency) ---
EAR_THRESHOLD_CLOSED = 0.25 # Threshold for closed eyes
FRAMES_PER_SECOND = 30      # Assumed webcam FPS for drowsiness logic
DROWSY_FRAMES_THRESHOLD = 20 # Number of consecutive closed frames to trigger drowsiness
CLEAR_DROWSY_FRAMES_THRESHOLD = 5 # Number of consecutive open frames to clear drowsiness

# --- MediaPipe Tasks Face Landmarker Setup ---
MODEL_ASSET_PATH = "face_landmarker.task"

# Ensure the model file exists
if not os.path.exists(MODEL_ASSET_PATH):
    print(f"Error: Face Landmarker model '{MODEL_ASSET_PATH}' not found.")
    print("Please download it from MediaPipe's official documentation and place it in the same directory as this script.")
    print("Download link example: https://developers.google.com/mediapipe/solutions/vision/face_landmarker/index#model_options (look for 'Model Asset Bundles')")
    exit()

# Configuration for FaceLandmarker
FaceLandmarkerOptions = vision.FaceLandmarkerOptions
BaseOptions = base_options.BaseOptions

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1 # We are interested in detecting only one face
)

# --- Refined Eye landmark indices for EAR calculation ---
# These indices are commonly used from MediaPipe's face_landmarks for EAR.
# They represent P1-P6 from the standard EAR formula.
# P1 (inner horizontal), P2 (upper-inner vertical), P3 (upper-outer vertical),
# P4 (outer horizontal), P5 (lower-outer vertical), P6 (lower-inner vertical)

# For the *left eye* (subject's right eye, viewer's left)
LEFT_EYE_LANDMARKS = [
    362,  # P1 - inner horizontal point
    385,  # P2 - upper vertical point
    387,  # P3 - upper vertical point
    263,  # P4 - outer horizontal point
    373,  # P5 - lower vertical point
    380   # P6 - lower vertical point
]

# For the *right eye* (subject's left eye, viewer's right)
RIGHT_EYE_LANDMARKS = [
    33,   # P1 - inner horizontal point
    160,  # P2 - upper vertical point
    158,  # P3 - upper vertical point
    133,  # P4 - outer horizontal point
    153,  # P5 - lower vertical point
    144   # P6 - lower vertical point
]

# --- Debugging Landmark Visualization (Optional) ---
# A broader set of eye points to draw for visual debugging (in magenta)
# These are for inspection, not directly for EAR calculation
DEBUG_LEFT_EYE_POINTS = [
    362, 385, 387, 263, 373, 380, # Your current EAR points
    382, 381, 374, 390, 249, 398, 397, 396, 403, 404, 405 # Other nearby eye contour points
]
DEBUG_RIGHT_EYE_POINTS = [
    33, 160, 158, 133, 153, 144, # Your current EAR points
    161, 159, 145, 7, 163, 154, 155, 157, 246
]
# Set to True to draw all these magenta points for debugging landmark mapping
VISUALIZE_ALL_DEBUG_POINTS = False


def euclidean_distance(point1, point2):
    """Calculates the Euclidean distance between two 2D points."""
    return np.linalg.norm(np.array(point1) - np.array(point2))

def calculate_ear(eye_landmarks, face_landmarks_list, img_w, img_h):
    """
    Calculates the Eye Aspect Ratio (EAR) for a given eye.
    Assumes eye_landmarks is a list of 6 indices corresponding to:
    P1, P2, P3, P4, P5, P6 (from the standard EAR formula)
    face_landmarks_list is a list of NormalizedLandmark objects from MediaPipe Tasks.
    """
    # Ensure all required landmarks are present
    if not all(idx < len(face_landmarks_list) for idx in eye_landmarks):
        return 0.0 # Not enough landmarks detected

    # Get the 2D pixel coordinates of the 6 eye landmarks
    p = []
    for i in eye_landmarks:
        landmark = face_landmarks_list[i]
        x = int(landmark.x * img_w)
        y = int(landmark.y * img_h)
        p.append((x, y))

    # Calculate distances:
    # Vertical distances (between upper and lower eyelids)
    A = euclidean_distance(p[1], p[5]) # P2-P6
    B = euclidean_distance(p[2], p[4]) # P3-P5
    # Horizontal distance (between eye corners)
    C = euclidean_distance(p[0], p[3]) # P1-P4

    # Calculate EAR
    if C == 0: return 0.0 # Avoid division by zero if eye is extremely squashed horizontally
    ear = (A + B) / (2.0 * C)
    return ear

def process_frame_eyes_detection(frame, face_landmarker_detector,
                                blink_counter_state,
                                drowsy_state):
    """
    Processes a single frame for eyes detection tasks (blink counting, EAR, drowsiness)
    using the new MediaPipe Tasks API.

    Args:
        frame (np.array): The input video frame (BGR format).
        face_landmarker_detector (mediapipe.tasks.python.vision.FaceLandmarker): Initialized FaceLandmarker object.
        blink_counter_state (dict): Dictionary to maintain blink count state.
        drowsy_state (dict): Dictionary to maintain drowsiness state.

    Returns:
        np.array: The annotated frame.
        float: Left eye EAR.
        float: Right eye EAR.
    """
    img_h, img_w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR frame to RGB for MediaPipe
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb) # Create MediaPipe Image

    results = face_landmarker_detector.detect(mp_image) # Perform landmark detection

    left_ear = 0.0
    right_ear = 0.0

    if results.face_landmarks: # Check if any face landmarks were detected
        # Assuming num_faces=1 in options, we take the first detected face
        face_landmarks = results.face_landmarks[0]
        landmarks_list = face_landmarks # This is already a list of NormalizedLandmark objects

        # Calculate EAR for both eyes
        left_ear = calculate_ear(LEFT_EYE_LANDMARKS, landmarks_list, img_w, img_h)
        right_ear = calculate_ear(RIGHT_EYE_LANDMARKS, landmarks_list, img_w, img_h)

        # --- T1 Blink Counter ---
        if left_ear < EAR_THRESHOLD_CLOSED and right_ear < EAR_THRESHOLD_CLOSED:
            blink_counter_state['is_eye_closed'] = True
        elif blink_counter_state['is_eye_closed'] and \
             left_ear > EAR_THRESHOLD_CLOSED and right_ear > EAR_THRESHOLD_CLOSED:
            blink_counter_state['blink_count'] += 1
            blink_counter_state['is_eye_closed'] = False

        # --- T3 Drowsiness Alert ---
        if left_ear < EAR_THRESHOLD_CLOSED and right_ear < EAR_THRESHOLD_CLOSED:
            drowsy_state['consecutive_closed_frames'] += 1
            drowsy_state['consecutive_open_frames'] = 0 # Reset open counter
        else:
            drowsy_state['consecutive_open_frames'] += 1
            if drowsy_state['consecutive_open_frames'] >= CLEAR_DROWSY_FRAMES_THRESHOLD:
                drowsy_state['is_drowsy_alert_active'] = False
                drowsy_state['consecutive_closed_frames'] = 0 # Reset closed counter

        if drowsy_state['consecutive_closed_frames'] >= DROWSY_FRAMES_THRESHOLD:
            drowsy_state['is_drowsy_alert_active'] = True

        # --- Visualizations ---
        # Draw yellow circles for the specific EAR calculation landmarks
        for eye_indices in [LEFT_EYE_LANDMARKS, RIGHT_EYE_LANDMARKS]:
            for idx in eye_indices:
                if idx < len(landmarks_list):
                    landmark = landmarks_list[idx]
                    x = int(landmark.x * img_w)
                    y = int(landmark.y * img_h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 255), -1) # Yellow circles

        # Draw magenta circles for ALL debug points (if enabled)
        if VISUALIZE_ALL_DEBUG_POINTS:
            for idx in DEBUG_LEFT_EYE_POINTS:
                if idx < len(landmarks_list):
                    landmark = landmarks_list[idx]
                    x = int(landmark.x * img_w)
                    y = int(landmark.y * img_h)
                    cv2.circle(frame, (x, y), 3, (255, 0, 255), -1) # Magenta for debug points
            for idx in DEBUG_RIGHT_EYE_POINTS:
                if idx < len(landmarks_list):
                    landmark = landmarks_list[idx]
                    x = int(landmark.x * img_w)
                    y = int(landmark.y * img_h)
                    cv2.circle(frame, (x, y), 3, (255, 0, 255), -1) # Magenta for debug points


        # Annotate EAR values on the frame (T2)
        cv2.putText(frame, f"L-EAR: {left_ear:.3f}", (10, img_h - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f"R-EAR: {right_ear:.3f}", (10, img_h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    # Display Blink Count (T1)
    cv2.putText(frame, f"Blinks: {blink_counter_state['blink_count']}", (img_w - 180, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Drowsiness Alert (T3)
    if drowsy_state['is_drowsy_alert_active']:
        overlay = frame.copy()
        alpha = 0.6  # Transparency factor.
        x1, y1, x2, y2 = 0, img_h // 2 - 50, img_w, img_h // 2 + 50
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1) # Red background
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        cv2.putText(frame, 'DROWSY! Wake Up!', (img_w // 2 - 200, img_h // 2 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)

    return frame, left_ear, right_ear

# --- Wrapper functions for running detection on different input types ---

def run_eyes_detection_webcam(face_landmarker_detector):
    """
    Runs the Eyes Detection module using the live webcam feed.
    Implements T1, T2, T3.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    blink_counter_state = {'blink_count': 0, 'is_eye_closed': False}
    drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}

    print("\n--- Eyes Detection (Live Webcam) ---")
    print("Press 'ESC' to return to the main menu.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        annotated_frame, _, _ = process_frame_eyes_detection(
            frame, face_landmarker_detector, blink_counter_state, drowsy_state)

        cv2.imshow('Eyes Detection', annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def run_eyes_detection_video_file(video_path, face_landmarker_detector):
    """
    Runs the Eyes Detection module using an uploaded video file.
    Implements T1, T2, T3, with play/pause/replay controls.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return

    paused = False
    current_frame_pos = 0

    blink_counter_state = {'blink_count': 0, 'is_eye_closed': False}
    drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}

    print(f"\n--- Eyes Detection (Video File: {os.path.basename(video_path)}) ---")
    print("Controls: 'P' to Play/Pause, 'R' to Replay, 'ESC' to Main Menu.")

    while True:
        if not paused:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos)
            ret, frame = cap.read()
            if not ret:
                print("End of video. Press 'R' to replay or 'ESC' to exit.")
                paused = True
                continue
            current_frame_pos += 1

            annotated_frame, _, _ = process_frame_eyes_detection(
                frame, face_landmarker_detector, blink_counter_state, drowsy_state)

            cv2.imshow('Eyes Detection (Video)', annotated_frame)

        key = cv2.waitKey(25) & 0xFF

        if key == ord('p') or key == ord('P'):
            paused = not paused
            print(f"Video {'Paused' if paused else 'Playing'}.")
        elif key == ord('r') or key == ord('R'):
            current_frame_pos = 0
            blink_counter_state = {'blink_count': 0, 'is_eye_closed': False}
            drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}
            paused = False
            print("Video Replaying...")
        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def run_eyes_detection_image_upload(image_path, face_landmarker_detector):
    """
    Performs Eyes Detection on a static image.
    Displays annotated results for T1, T2, T3 (though dynamic counters are less relevant for static).
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not load image: {image_path}. Check if file is corrupted or path is incorrect.")
        return

    # Initialize state variables (will only reflect initial state for static image)
    # These won't change for a static image, but are needed by process_frame_eyes_detection
    blink_counter_state = {'blink_count': 0, 'is_eye_closed': False}
    drowsy_state = {'consecutive_closed_frames': 0, 'consecutive_open_frames': 0, 'is_drowsy_alert_active': False}

    print(f"\n--- Eyes Detection (Image: {os.path.basename(image_path)}) ---")
    print("Press 'ESC' to return to the main menu.")

    # Process the image once
    annotated_frame, _, _ = process_frame_eyes_detection(
        frame, face_landmarker_detector, blink_counter_state, drowsy_state)

    # For static images, drowsiness and blink count are effectively "0" or "not active"
    # as there's no temporal context. We display the current EAR.
    cv2.putText(annotated_frame, "Static Image - Blinks & Drowsiness N/A", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('Eyes Detection (Image)', annotated_frame)
    cv2.waitKey(0) # Wait indefinitely for a key press
    cv2.destroyAllWindows()


def eyes_detection_module():
    """
    Main function for the Eyes Detection module, presenting input source options.
    Initializes the FaceLandmarker detector for the entire module session.
    """
    try:
        landmarker_detector = vision.FaceLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Failed to initialize Face Landmarker: {e}")
        print("Please ensure 'face_landmarker.task' is downloaded and in the correct directory.")
        return # Exit the module if initialization fails

    while True:
        print("\n--- Eyes Detection Module ---")
        print("1. Live Webcam Feed")
        print("2. Video File Upload")
        print("3. Image Upload")
        print("Press 'ESC' from any detection mode to return here.")
        print("Enter your choice (1-3, or 'b' to go back to main menu): ")

        choice = input().lower()

        if choice == '1':
            run_eyes_detection_webcam(landmarker_detector)
        elif choice == '2':
            video_path = input("Enter path to video file: ")
            run_eyes_detection_video_file(video_path, landmarker_detector)
        elif choice == '3':
            image_path = input("Enter path to image file: ")
            run_eyes_detection_image_upload(image_path, landmarker_detector)
        elif choice == 'b':
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 'b'.")

# --- Main Menu (simplified for this example, would be part of your full assignment) ---
def main_menu():
    """
    Simulated main menu to select different detection modules or exit.
    """
    while True:
        print("\n========== HCI Detection System ==========")
        print("Select a Detection Module:")
        print("1. Lips Detection (Placeholder)")
        print("2. Eyes Detection")
        print("3. Face Detection (Placeholder)")
        print("4. Hand Detection (Placeholder)")
        print("0. Exit")
        print("==========================================")

        main_choice = input("Enter your choice (0-4): ").lower()

        if main_choice == '1':
            print("Lips Detection module not implemented yet with the new API.")
        elif main_choice == '2':
            eyes_detection_module()
        elif main_choice == '3':
            print("Face Detection module not implemented yet.")
        elif main_choice == '4':
            print("Hand Detection module not implemented yet.")
        elif main_choice == '0':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 0 and 4.")

if __name__ == "__main__":
    main_menu()
