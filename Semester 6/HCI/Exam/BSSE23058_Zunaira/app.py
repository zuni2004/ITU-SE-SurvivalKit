# ────────────────────────────────────────────────────────────
# CampusConnect  —  Starter Template  |  HCI-401 Final Exam
# Fill every  pass # TODO  stub. Do NOT rename functions.
# ────────────────────────────────────────────────────────────
import gradio as gr
import cv2
import whisper
import speech_recognition as sr
import numpy as np
from PIL import Image
from openai import OpenAI
import base64, io, uuid, logging, requests
from pydub import AudioSegment
from openai import OpenAI
import re
import time
import functools
from typing import Tuple, List, Dict, Optional, Generator
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# ── Ollama client (no internet required) ──────────────────────
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60.0)
# ── Whisper  (loaded once — do NOT move inside a function) ─────
print("Loading Whisper...")
whisper_model = whisper.load_model("base")
print("Whisper ready.")
# ── System prompt ──────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are CampusConnect, an AI support assistant for FAST University. "
    "Only answer questions about: Fee & Finance, Examination & Grades, "
    "Course Registration, Hostel & Transport, Scholarship & Financial Aid. "
    "Politely decline anything outside scope and name the correct office. "
    "Always state which input modality (image/voice/text) you used to understand the query."
)


# ── Startup health check ───────────────────────────────────────
def startup_check():
    """TODO Task 3.B.iii — extend this with all required checks"""
    checks_passed = True

    # Check 1: Ollama running
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        assert r.status_code == 200
        print("\033[92m[PASS]\033[0m Ollama server running at localhost:11434")
    except Exception as e:
        print(f"\033[91m[FAIL]\033[0m Ollama: {e}")
        print("Run: ollama serve")
        checks_passed = False

    # Check 2: llama3 model available
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = r.json().get("models", [])
        model_names = [m.get("name", "") for m in models]

        if any("llama3" in name or "llama2" in name for name in model_names):
            print("\033[92m[PASS]\033[0m LLM model available")
        else:
            print(
                f"\033[91m[FAIL]\033[0m No llama3/llama2 found. Available: {model_names}"
            )
            print("Run: ollama pull llama3")
            checks_passed = False
    except Exception as e:
        print(f"\033[91m[FAIL]\033[0m Could not check models: {e}")
        checks_passed = False

    # Check 3: Whisper model cached
    try:
        if whisper_model is not None:
            print("\033[92m[PASS]\033[0m Whisper base model loaded")
        else:
            print("\033[91m[FAIL]\033[0m Whisper model not loaded")
            checks_passed = False
    except Exception as e:
        print(f"\033[91m[FAIL]\033[0m Whisper: {e}")
        checks_passed = False

    # Check 4: Camera access
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            print("\033[92m[PASS]\033[0m Camera (index 0) accessible")
        else:
            print("\033[91m[FAIL]\033[0m Camera not accessible")
    except Exception as e:
        print(f"\033[91m[FAIL]\033[0m Camera: {e}")

    if not checks_passed:
        raise RuntimeError("Critical checks failed. See above for instructions.")

    print("\nAll systems ready! Starting CampusConnect...\n")


startup_check()

# Topic keywords for local classification
TOPIC_KEYWORDS = {
    "Fee & Finance": [
        "fee",
        "challan",
        "tuition",
        "payment",
        "dues",
        "overdue",
        "fine",
        "refund",
        "discount",
        "scholarship",
        "waiver",
        "installment",
        "billing",
    ],
    "Examination & Grades": [
        "result",
        "grade",
        "marks",
        "gpa",
        "exam",
        "test",
        "score",
        "transcript",
        "degree",
        "transcript",
        "retake",
        "dispute",
        "appeal",
        "fail",
        "pass",
    ],
    "Course Registration": [
        "course",
        "register",
        "add",
        "drop",
        "enrollment",
        "section",
        "prerequisite",
        "corequisite",
        "conflict",
        "closed",
        "waitlist",
        "schedule",
        "semester",
    ],
    "Hostel & Transport": [
        "hostel",
        "room",
        "accommodation",
        "transport",
        "bus",
        "shuttle",
        "complaint",
        "maintenance",
        "wifi",
        "facility",
        "move",
        "transfer",
        "resident",
    ],
    "Scholarship & Financial Aid": [
        "scholarship",
        "financial aid",
        "grant",
        "loan",
        "bursary",
        "merit",
        "need-based",
        "sponsorship",
        "application",
        "eligible",
        "award",
        "funding",
    ],
}


# ══════════════════════════════════════════════════════════
#  STUDENT CODE — implement every function below
# ══════════════════════════════════════════════════════════
def process_frame(image_np) -> Optional[str]:
    """Task 1.A — receive NumPy frame, return base64 JPEG string or None"""

    try:
        if image_np is None:
            logger.warning("process_frame: image_np is None")
            return None

        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        height, width = image_bgr.shape[:2]
        max_width, max_height = 640, 480

        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_bgr = cv2.resize(image_bgr, (new_width, new_height))

        success, jpeg_bytes = cv2.imencode(
            ".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85]
        )
        if not success:
            logger.error("Failed to encode JPEG")
            return None

        base64_str = base64.b64encode(jpeg_bytes).decode("utf-8")
        logger.info(f"Frame processed: {len(base64_str)} bytes base64")
        return base64_str

    except cv2.error as e:
        logger.error(f"OpenCV error in process_frame: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in process_frame: {e}")
        return None


def transcribe_audio(audio_path: str) -> str:
    """Task 1.B — transcribe WAV/MP3 using Whisper, return transcript string"""

    try:
        if audio_path is None:
            return ""

        audio_file = Path(audio_path)
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return "Error: Audio file not found"

        if whisper_model is None:
            return "Error: Whisper not loaded. Cannot transcribe."

        logger.info(f"Transcribing: {audio_path}")
        result = whisper_model.transcribe(audio_path)
        transcript = result.get("text", "").strip()

        logger.info(f"Transcript: {transcript[:100]}...")
        return transcript

    except RuntimeError as e:
        if "ffmpeg" in str(e).lower():
            msg = "Error: MP3 requires ffmpeg. Please upload a WAV file instead or install ffmpeg."
            logger.error(msg)
            return msg
        else:
            logger.error(f"Whisper RuntimeError: {e}")
            return f"Error: {str(e)[:100]}"
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        return f"Error: Could not transcribe audio ({type(e).__name__})"


def validate_text_input(text: str) -> Tuple[bool, str]:
    """Task 1.C — returns (is_valid: bool, error_message: str)"""

    if not text or text.isspace():
        return False, "Error: Text cannot be empty."

    if len(text) < 5:
        return False, "Error: Text must be at least 5 characters."

    if text.isdigit():
        return False, "Error: Text must contain letters, not only numbers."

    if len(text) > 500:
        return False, "Error: Text exceeds 500 character limit."

    return True, ""


def topic_classifier(text: str, transcript: str) -> Tuple[bool, str]:
    """Task 2.A — returns (in_scope: bool, topic_or_refusal_msg: str)"""

    combined = f"{text} {transcript}".lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined:
                logger.info(f"Topic matched: {topic}")
                return True, topic

    refusal = (
        "Your query is outside my scope. I can help with: "
        "Fee & Finance, Examination & Grades, Course Registration, "
        "Hostel & Transport, or Scholarship & Financial Aid. "
        "Please contact the relevant office for other inquiries."
    )
    logger.warning("Query out of scope")
    return False, refusal


def build_message_payload(
    text: str, transcript: str, image_b64: Optional[str]
) -> List[Dict]:
    """Task 2.A — returns OpenAI-compatible content list for one user turn"""

    content = []

    if image_b64 is not None:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            }
        )

    if transcript and transcript.strip():
        content.append({"type": "text", "text": f"[VOICE TRANSCRIPT]: {transcript}"})

    content.append({"type": "text", "text": text})

    return [{"role": "user", "content": content}]


def trim_history(history: List[Dict], max_turns: int = 10) -> List[Dict]:
    """Task 2.A — keeps system prompt + last max_turns messages only"""

    if len(history) <= max_turns + 1:
        return history

    logger.warning(f"Trimming history from {len(history)} to {max_turns + 1} messages")
    return history[:1] + history[-(max_turns):]


def parse_modality_used(response_text: str) -> str:
    response_lower = response_text.lower()

    if any(
        phrase in response_lower
        for phrase in [
            "based on the image",
            "from the document",
            "from your screenshot",
        ]
    ):
        return "image"
    elif any(
        phrase in response_lower
        for phrase in ["from your spoken", "your voice", "audio you"]
    ):
        return "voice"
    elif any(
        phrase in response_lower
        for phrase in ["from your typed", "from your message", "question you asked"]
    ):
        return "text"
    else:
        return "combined"


def handle_error(error: Exception, context: str = "") -> str:
    """Task 3.B — unified error handler, returns user-friendly string"""

    logger.exception(f"Error in {context}: {error}")

    error_type = type(error).__name__
    error_msg = str(error).lower()

    if isinstance(error, requests.exceptions.ConnectionError):
        return "Ollama server is not running. Please start Ollama and try again."
    elif error_type == "APITimeoutError":
        return "The model is taking too long. Try a lighter model like mistral."
    elif error_type == "APIConnectionError":
        return "Cannot reach local AI server at localhost:11434."
    elif "UnknownValueError" in error_type:
        return "Could not understand audio. Please try again."
    elif isinstance(error, FileNotFoundError):
        return "Audio or image file not found or corrupted."
    elif isinstance(error, cv2.error):
        return "Camera error: check your device connection."
    else:
        return f"Error: {str(error)[:80]}"


def retry_with_backoff(max_retries: int = 3, base_delay: float = 2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_type = type(e).__name__
                    if error_type not in ["APIConnectionError", "APITimeoutError"]:
                        raise

                    if attempt == max_retries - 1:
                        raise

                    delay = base_delay**attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed. Retrying in {delay}s..."
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def chat(
    text: str,
    audio_path: Optional[str],
    image_np: Optional[np.ndarray],
    history: List[Dict],
    state: Dict,
) -> Tuple[List, List[Dict], str, str]:
    """Task 2.B — main callback. Returns (chatbot, history, transcript, error_msg)"""

    if state.get("is_processing", False):
        return (
            history,
            state,
            "",
            gr.Warning("Please wait for current response to complete."),
        )

    state["is_processing"] = True
    error_msg = ""
    transcript = ""

    try:
        is_valid, validation_error = validate_text_input(text)
        if not is_valid:
            state["is_processing"] = False
            return history, state, "", validation_error

        image_b64 = process_frame(image_np) if image_np is not None else None
        transcript = transcribe_audio(audio_path) if audio_path else ""

        in_scope, topic_or_msg = topic_classifier(text, transcript)

        if not in_scope:
            user_msg = f"Text: {text}"
            if transcript:
                user_msg += f"\n[Voice: {transcript}]"

            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": topic_or_msg})

            state["is_processing"] = False
            return history, state, transcript, ""

        user_messages = build_message_payload(text, transcript, image_b64)

        system_msg = {"role": "system", "content": SYSTEM_PROMPT}
        full_history = [system_msg] + history + user_messages

        full_history = trim_history(full_history, max_turns=10)

        logger.info(f"Calling Ollama with {len(full_history)} messages")

        response_text = ""
        try:
            stream = client.chat.completions.create(
                model="llama3",
                messages=full_history,
                stream=True,
                temperature=0.7,
                top_p=0.9,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content

        except Exception as e:
            response_text = handle_error(e, "Ollama API call")
            error_msg = response_text

        if not response_text.startswith("X") and not response_text.startswith(
            "Warning"
        ):
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": response_text})

        state["conversation_history"] = history
        state["last_error"] = error_msg if error_msg else None

    except Exception as e:
        error_msg = handle_error(e, "chat()")
        logger.exception("Critical error in chat()")

    finally:
        state["is_processing"] = False

    return history, state, transcript, error_msg


def init_state():
    return {
        "session_id": str(uuid.uuid4()),
        "conversation_history": [],
        "is_processing": False,
        "last_error": None,
        "camera_mode": "webcam",
        "voice_mode": "mic",
        "char_count": 0,
    }


def update_char_counter(text: str) -> Tuple[str, str]:
    count = len(text)
    counter = f"{count} / 500"

    if count > 480:
        counter = f"{counter} (almost full!)"

    if count > 500:
        text = text[:500]

    return text, counter


def clear_all(state: Dict) -> Tuple[List, List, str, str, str, None, None, Dict]:
    state["conversation_history"] = []
    state["session_id"] = str(uuid.uuid4())

    return (
        [],  # chatbot
        [],  # history state
        "",  # text input
        "0 / 500",  # char counter
        "",  # transcript
        None,  # image
        None,  # audio
        state,  # state
    )


def update_status_panel(state: Dict) -> str:
    is_processing = state.get("is_processing", False)
    status = "Processing..." if is_processing else "Ready"

    return f"Status: {status}"


# ── Gradio UI layout (provided — do NOT remove components) ────
with gr.Blocks(title="CampusConnect — FAST University SIS") as app:

    state = gr.State(value=init_state())
    history_state = gr.State(value=[])

    gr.Markdown("# 🎓 CampusConnect — FAST University Support")
    gr.Markdown("**AI-powered multimodal student support chatbot**")

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                placeholder="Type your query here (5-500 chars)...",
                label="Text Input",
                lines=3,
                max_lines=5,
            )
            char_counter = gr.Textbox(
                label="Character Count", value="0 / 500", interactive=False
            )

            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="Voice — Live Microphone or Audio Upload (WAV/MP3)",
            )

            transcript_box = gr.Textbox(
                label="Voice Transcript (auto-filled)", interactive=False, lines=2
            )

        with gr.Column(scale=2):
            camera_input = gr.Image(
                sources=["webcam", "upload"],
                type="numpy",
                label="Camera — Live Webcam or Upload Image",
            )

            status_panel = gr.Textbox(label="Status", value="Ready", interactive=False)

    chatbot = gr.Chatbot(label="CampusConnect Chat", show_label=True, height=400)

    error_label = gr.Textbox(
        label="Status / Error Messages", interactive=False, lines=2
    )

    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary", size="lg")
        clear_btn = gr.Button("Clear Conversation", variant="secondary")

    text_input.change(
        fn=update_char_counter, inputs=text_input, outputs=[text_input, char_counter]
    )

    # submit button — inputs/outputs fixed, implement chat() above
    submit_btn.click(
        fn=chat,
        inputs=[text_input, audio_input, camera_input, history_state, state],
        outputs=[chatbot, history_state, transcript_box, error_label],
    )

    clear_btn.click(
        fn=clear_all,
        inputs=state,
        outputs=[
            chatbot,
            history_state,
            text_input,
            char_counter,
            transcript_box,
            camera_input,
            audio_input,
            state,
        ],
    )

    state.change(fn=update_status_panel, inputs=state, outputs=status_panel)

if __name__ == "__main__":
    print("\nLaunching CampusConnect...\n")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft(),
    )
