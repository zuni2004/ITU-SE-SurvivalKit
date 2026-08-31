import cv2
import numpy as np
from deepface import DeepFace

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
smile_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

MOUTH_OPEN_THRESHOLD = 0.55
ANALYZE_EVERY_N_FRAMES = 5
COLOR_GREEN = (0, 210, 0)
COLOR_RED = (0, 0, 220)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (0, 210, 210)
COLOR_CYAN = (210, 210, 0)
COLOR_ORANGE = (0, 140, 255)
COLOR_BLACK = (0, 0, 0)


def estimate_mouth_openness(grayscale_face):
    face_height, face_width = grayscale_face.shape

    mouth_region = grayscale_face[
        int(face_height * 0.62) : int(face_height * 0.92),
        int(face_width * 0.20) : int(face_width * 0.80),
    ]

    if mouth_region.size == 0:
        return 0.0

    edge_map = cv2.Canny(mouth_region, 50, 150)
    region_height, region_width = edge_map.shape

    middle_strip = edge_map[region_height // 4 : 3 * region_height // 4, :]
    edge_density = np.count_nonzero(middle_strip) / max(middle_strip.size, 1)

    openness_score = float(np.clip(edge_density * 6.0, 0.0, 1.0))
    return openness_score


def draw_text_label(
    frame,
    text,
    position,
    color=COLOR_WHITE,
    font_scale=0.65,
    thickness=2,
    draw_background=True,
):

    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    x, y = position

    if draw_background:
        cv2.rectangle(
            frame,
            (x - 4, y - text_height - 6),
            (x + text_width + 4, y + baseline),
            COLOR_BLACK,
            -1,
        )

    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)


def draw_frame_border(frame, color, thickness=8):

    frame_height, frame_width = frame.shape[:2]
    inset = thickness // 2
    cv2.rectangle(
        frame,
        (inset, inset),
        (frame_width - inset, frame_height - inset),
        color,
        thickness,
    )


def run(source=0):

    is_static_image = isinstance(source, str) and source.lower().endswith(
        (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")
    )

    if is_static_image:
        original_image = cv2.imread(source)
        if original_image is None:
            print(f"[ERROR] Cannot read image: {source}")
            return
        video_capture = None
    else:
        video_capture = cv2.VideoCapture(source)
        if not video_capture.isOpened():
            print(f"[ERROR] Cannot open: {source}")
            return

    current_frame_index = 0

    last_emotion_result = {"dominant": "N/A", "confidence": 0.0}

    print("[INFO] Running... Press ESC to exit.")

    while True:
        if is_static_image:
            frame = original_image.copy()
        else:
            success, frame = video_capture.read()
            if not success:
                print("[INFO] End of stream.")
                break

        frame_height, frame_width = frame.shape[:2]
        current_frame_index += 1
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        active_border_color = COLOR_GREEN

        detected_faces = face_detector.detectMultiScale(
            grayscale_frame, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        if len(detected_faces) == 0:
            draw_text_label(
                frame, "No face detected", (20, 45), color=COLOR_YELLOW, font_scale=0.75
            )

        else:
            face_x, face_y, face_w, face_h = sorted(
                detected_faces, key=lambda f: f[2] * f[3], reverse=True
            )[0]

            cv2.rectangle(
                frame,
                (face_x, face_y),
                (face_x + face_w, face_y + face_h),
                COLOR_ORANGE,
                2,
            )

            grayscale_face_crop = grayscale_frame[
                face_y : face_y + face_h, face_x : face_x + face_w
            ]

            print("── FEATURE 1: Smile Detection + MAR ─────────────────")

            mouth_openness = estimate_mouth_openness(grayscale_face_crop)

            if mouth_openness > MOUTH_OPEN_THRESHOLD:
                active_border_color = COLOR_RED

            smile_search_top = face_y + face_h // 2
            smile_search_region = grayscale_frame[
                smile_search_top : face_y + face_h, face_x : face_x + face_w
            ]

            detected_smiles = smile_detector.detectMultiScale(
                smile_search_region, scaleFactor=1.7, minNeighbors=20, minSize=(25, 15)
            )

            person_is_smiling = len(detected_smiles) > 0

            for smile_x, smile_y, smile_w, smile_h in detected_smiles:
                cv2.rectangle(
                    frame,
                    (face_x + smile_x, smile_search_top + smile_y),
                    (face_x + smile_x + smile_w, smile_search_top + smile_y + smile_h),
                    COLOR_CYAN,
                    2,
                )

            smile_text = "Smiling :)" if person_is_smiling else "Neutral :)"
            smile_color = COLOR_GREEN if person_is_smiling else COLOR_YELLOW
            draw_text_label(
                frame, smile_text, (20, 45), color=smile_color, font_scale=0.85
            )
            draw_text_label(
                frame,
                f"MAR: {mouth_openness:.3f}",
                (20, 85),
                color=COLOR_WHITE,
                font_scale=0.62,
            )

            print(" ── FEATURE 2: Emotion Recognition ───────────────────")

            if current_frame_index % ANALYZE_EVERY_N_FRAMES == 0:
                face_image_crop = frame[
                    face_y : face_y + face_h, face_x : face_x + face_w
                ]

                if face_image_crop.size > 0:
                    try:
                        analysis_output = DeepFace.analyze(
                            img_path=face_image_crop,
                            actions=["emotion"],
                            enforce_detection=False,
                            silent=True,
                        )

                        if isinstance(analysis_output, list):
                            analysis_output = analysis_output[0]

                        emotion_scores = analysis_output.get("emotion", {})
                        top_emotion = analysis_output.get("dominant_emotion", "N/A")
                        top_confidence = emotion_scores.get(top_emotion, 0.0)

                        last_emotion_result = {
                            "dominant": top_emotion.capitalize(),
                            "confidence": top_confidence,
                        }

                    except Exception:
                        pass

            emotion_display_text = (
                f"Emotion: {last_emotion_result['dominant']} "
                f"({last_emotion_result['confidence']:.1f}%)"
            )
            draw_text_label(
                frame,
                emotion_display_text,
                (20, 120),
                color=COLOR_CYAN,
                font_scale=0.65,
            )

        draw_frame_border(frame, active_border_color)
        draw_text_label(
            frame,
            "ESC to exit",
            (frame_width - 130, frame_height - 12),
            color=COLOR_WHITE,
            font_scale=0.50,
        )

        cv2.imshow("Smile + Emotion Detection - HCI Assessment-4", frame)
        key_pressed = cv2.waitKey(1 if not is_static_image else 0) & 0xFF

        if key_pressed == 27:
            print("[INFO] ESC - exiting.")
            break
        if is_static_image:
            break

    if video_capture is not None:
        video_capture.release()

    cv2.destroyAllWindows()
    print("[INFO] Done.")


if __name__ == "__main__":
    import sys

    input_source = sys.argv[1] if len(sys.argv) > 1 else 0

    if isinstance(input_source, str) and input_source.isdigit():
        input_source = int(input_source)

    run(source=input_source)
