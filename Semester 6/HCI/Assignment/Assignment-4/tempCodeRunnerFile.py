
# --- Global Constants ---
MODEL_ASSET_PATH = "face_landmarker.task"

# Setup shortcuts using the same structure as your working code
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
    Matches the coordinate logic of your working eye code.
    """
    def get_coords(index):
        pt = face_landmarks_list[index]
        return (int(pt.x * w), int(pt.y * h))

    # Landmark indices for mouth (MediaPipe standard)
    p_upper, p_lower = get_coords(13), get_coords(14)
    p_left, p_right = get_coords(78), get_coords(308)

    vert_dist = calculate_distance(p_upper, p_lower)
    horiz_dist = calculate_distance(p_left, p_right)
    mar = vert_dist / horiz_dist if horiz_dist > 0 else 0.0

    # Smile detection logic from your team member's original code
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
    
    # Configure for Static Image
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_ASSET_PATH),
        running_mode=VisionRunningMode.IMAGE
    )

    with FaceLandmarker.create_from_options(options) as landmarker:
        # Prepare MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = landmarker.detect(mp_image)

        smile_label = "Neutral"
        mar_display = 0.0
        draw_red_border = False

        if results.face_landmarks:
            # results.face_landmarks is a list of faces; take the first one
            mar, is_smiling, pts = get_mouth_metrics(results.face_landmarks[0], w, h)
            
            mar_display = mar
            if mar > 0.55:
                draw_red_border = True
            if is_smiling:
                smile_label = "Smiling"

            # Draw mouth points
            for pt in pts:
                cv2.circle(frame, pt, 2, (0, 255, 0), -1)

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
    
    # Configure for Video (requires timestamp)
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
                    if isinstance(input_source, str): # Loop video if it's a file
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    break

                h, w, _ = frame.shape
                
                # Get current timestamp in milliseconds
                timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                # For live webcam, if pos_msec is 0, use current system time
                if timestamp_ms == 0:
                    timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

                # Process Frame
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                results = landmarker.detect_for_video(mp_image, timestamp_ms)

                draw_red_border = False
                mar_display = 0.0
                smile_label = "Neutral"

                if results.face_landmarks:
                    mar, is_smiling, _ = get_mouth_metrics(results.face_landmarks[0], w, h)
                    
                    mar_display = mar
                    # Logic for mouth cycles
                    if mar > 0.55:
                        draw_red_border = True
                        is_mouth_open = True
                    elif mar < 0.35 and is_mouth_open:
                        cycle_count += 1
                        is_mouth_open = False

                    if is_smiling:
                        smile_label = "Smiling"

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
