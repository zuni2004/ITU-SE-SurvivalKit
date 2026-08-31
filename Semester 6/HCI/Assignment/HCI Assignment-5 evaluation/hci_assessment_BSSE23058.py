import os
import warnings
import time
import threading
import numpy as np
import speech_recognition as sr

# Suppress technical logs
warnings.filterwarnings("ignore")

# NLP Resources
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    nltk.data.find("vader_lexicon")
except (LookupError, AttributeError):
    nltk.download("vader_lexicon", quiet=True)

# ==============================================================================
# ENGINE GLOBALS
# ==============================================================================
INTENT_MAP = {
    "COMPLAINT": [
        "problem",
        "issues",
        "broken",
        "error",
        "fail",
        "wrong",
        "terrible",
        "awful",
    ],
    "INQUIRY": [
        "what",
        "how",
        "when",
        "where",
        "explain",
        "tell me",
        "does",
        "can you",
    ],
    "SUPPORT": ["help", "stuck", "assist", "cannot", "unable", "don't know"],
    "FEEDBACK": [
        "suggest",
        "improve",
        "recommend",
        "wish",
        "would be better",
        "should",
    ],
    "BILLING": ["charge", "payment", "invoice", "refund", "price", "cost", "money"],
    "FAREWELL": ["bye", "goodbye", "thanks", "thank you", "done", "that's all"],
}

SENTIMENT_EMOTIONS = {
    "ELATED": "ELATED",
    "POSITIVE": "POSITIVE",
    "NEUTRAL": "NEUTRAL",
    "NEGATIVE": "NEGATIVE",
    "FRUSTRATED": "FRUSTRATED",
}
SENTIMENT_WEIGHTS = {
    "FRUSTRATED": 0,
    "NEGATIVE": 1,
    "NEUTRAL": 2,
    "POSITIVE": 3,
    "ELATED": 4,
}

# Initialize the global recognizer engine
speech_engine = sr.Recognizer()

# ==============================================================================
# STAGE 1: VOICE + TEXT INPUT (SPEECH_RECOGNITION LOGIC)
# ==============================================================================


def record_voice(duration=6, sr_rate=16000):
    print(f"\n>>> [SYSTEM] Listening (Max {duration}s)... Speak clearly.")
    try:
        with sr.Microphone() as mic:
            # Adjust for background noise levels
            speech_engine.adjust_for_ambient_noise(mic, duration=0.5)
            # Capture the stream
            raw_audio = speech_engine.listen(
                mic, timeout=duration, phrase_time_limit=duration
            )
            print(">>> [SYSTEM] Audio captured successfully.")
            return raw_audio
    except Exception as hardware_err:
        print(f"Mic Error: {hardware_err}")
        return None


def transcribe(audio, sr_rate=16000):
    if audio is None:
        return ""

    try:
        # Use Google's recognition engine (as used in Assignment 5)
        text_output = speech_engine.recognize_google(audio)
        return text_output.strip()
    except sr.UnknownValueError:
        print("!!! [ERROR] Speech was unintelligible.")
        return ""
    except sr.RequestError as req_err:
        print(f"!!! [API ERROR] Service unavailable: {req_err}")
        # Return fallback for evaluation if API fails
        return "I have a problem with my account login failing."


def get_user_input():
    entry_prompt = "\n💬 INPUT > Type message or hit [ENTER] to talk: "
    user_string = input(entry_prompt).strip()

    if user_string == "":
        captured_audio = record_voice()
        transcribed_text = transcribe(captured_audio)
        print(f'Captured: "{transcribed_text}"')
        return transcribed_text, "voice"

    return user_string, "text"


# ==============================================================================
# STAGE 2: EMOTION ANALYSER
# ==============================================================================


def classify_emotion(text):
    analyzer = SentimentIntensityAnalyzer()
    metrics = analyzer.polarity_scores(text)
    val = metrics["compound"]

    if val >= 0.5:
        tag = "ELATED"
    elif val >= 0.05:
        tag = "POSITIVE"
    elif val > -0.05:
        tag = "NEUTRAL"
    elif val > -0.5:
        tag = "NEGATIVE"
    else:
        tag = "FRUSTRATED"

    return {"label": tag, "score": val, "emotion": SENTIMENT_EMOTIONS[tag]}


def detect_mood_shift(prev_label, curr_label):
    if prev_label is None:
        return "stable"

    v1 = SENTIMENT_WEIGHTS.get(prev_label, 2)
    v2 = SENTIMENT_WEIGHTS.get(curr_label, 2)

    if v2 < v1:
        return "escalating"
    if v2 > v1:
        return "improving"
    return "stable"


def session_emotion_summary(emotion_log):
    if not emotion_log:
        return {"dominant": "NEUTRAL", "avg": 0.0, "escalations": 0}

    scores = [x["score"] for x in emotion_log]
    labels = [x["label"] for x in emotion_log]

    # Calculate mode
    count_map = {}
    for L in labels:
        count_map[L] = count_map.get(L, 0) + 1
    dom = max(count_map, key=count_map.get)

    # Count negative shifts
    worsening = 0
    for i in range(len(labels) - 1):
        if SENTIMENT_WEIGHTS[labels[i + 1]] < SENTIMENT_WEIGHTS[labels[i]]:
            worsening += 1

    return {
        "dominant_emotion": dom,
        "average_score": round(float(np.mean(scores)), 4),
        "escalation_count": worsening,
    }


# ==============================================================================
# STAGE 3: INTENT TRACKER
# ==============================================================================


def classify_intent(text):
    msg = text.lower()
    hits = {}

    for intent_key, words in INTENT_MAP.items():
        score = sum(1 for w in words if w in msg)
        if score > 0:
            hits[intent_key] = score

    if not hits:
        return "GENERAL"

    return max(hits, key=hits.get)


def update_intent_log(intent_log, new_intent, turn_number):
    shift = None
    if intent_log:
        last_intent = intent_log[-1]["current"]
        if last_intent != new_intent:
            shift = {"from": last_intent, "to": new_intent, "turn": turn_number}

    intent_log.append({"current": new_intent, "shift_event": shift})
    return intent_log


def generate_response(text, intent, emotion):
    if intent == "COMPLAINT":
        if emotion == "FRUSTRATED":
            return "I sincerely apologise. Let me escalate this to our senior team right now."
        return "I understand there is an issue. Can you share more details?"

    if intent == "BILLING" and emotion in ["NEGATIVE", "FRUSTRATED"]:
        return "I am sorry about the billing concern. I will review your account immediately."

    if intent == "FAREWELL":
        return "Thank you for contacting us. Have a great day!"

    if intent == "INQUIRY":
        return "Great question. Here is what I know: Our staff is currently looking into your specific request."

    return "Thank you for the information. How can I help you further?"


# ==============================================================================
# STAGE 5: REPORTING
# ==============================================================================


def print_health_report(history, emotion_log, intent_log):
    print("\n" + "#" * 50)
    print("           ARIA SESSION HEALTH AUDIT")
    print("#" * 50)

    total = len(history)
    voice_t = len([x for x in history if x["source"] == "voice"])
    text_t = total - voice_t

    # Process Intents
    all_intents = []
    shifts = 0
    for item in intent_log:
        if item["current"] not in all_intents:
            all_intents.append(item["current"])
        if item["shift_event"]:
            shifts += 1

    # Process Sentiment
    stats = session_emotion_summary(emotion_log)
    avg_s = stats["average_score"]
    esc_c = stats["escalation_count"]

    # Health Calculation
    h_score = 50 + (avg_s * 30) - (shifts * 5) - (esc_c * 8)
    h_score = int(np.clip(h_score, 0, 100))

    if h_score >= 70:
        recommendation = "RESOLVED"
    elif h_score >= 40:
        recommendation = "MONITOR"
    else:
        recommendation = "ESCALATE"

    print(f"Turns Taken    : {total} (Mic: {voice_t}, Text: {text_t})")
    print(f"Goal History   : {', '.join(all_intents)}")
    print(f"Goal Shifts    : {shifts}")
    print(f"Average Mood   : {stats['dominant_emotion']} ({avg_s:.2f})")
    print(f"Mood Declines  : {esc_c}")
    print("-" * 50)
    print(f"SESSION SCORE  : {h_score}/100")
    print(f"ACTION STATUS  : {recommendation}")
    print("#" * 50)


# ==============================================================================
# STAGE 4: AUDIT REPLAY
# ==============================================================================


def run_evaluation_audit():
    CONVO_LOG = [
        "Hi, I need some help with my account.",
        "I have been trying to log in for two days but it keeps failing.",
        "This is really frustrating, I cannot believe this is still broken.",
        "Can you at least tell me when it will be fixed?",
        "Also I was charged twice last month — I want a refund.",
        "Actually you know what, forget it. I am going to cancel.",
        "Wait — actually I found the issue, it was my browser. Never mind!",
        "Thanks for your patience. Bye.",
    ]

    hist, e_log, i_log = [], [], []
    prev_emo = None

    print("\n--- INITIATING LOG REPLAY AUDIT ---")

    for i, msg in enumerate(CONVO_LOG):
        emo = classify_emotion(msg)
        inte = classify_intent(msg)

        move = detect_mood_shift(prev_emo, emo["label"])
        prev_emo = emo["label"]

        reply = generate_response(msg, inte, emo["label"])

        # Internal Recording
        e_log.append(emo)
        i_log = update_intent_log(i_log, inte, i + 1)
        hist.append({"source": "text"})

        emotion_display = emo["emotion"]
        print(f"Turn {i+1}: [{emotion_display}] | {inte} | Shift: {move}")
        print(f"ARIA: {reply}\n")

    print_health_report(hist, e_log, i_log)


# ==============================================================================
# MAIN NAVIGATION
# ==============================================================================


def main():
    while True:
        print("\n[ ARIA CUSTOMER CARE PORTAL ]")
        print("1. Start Interactive Session (Voice/Text)")
        print("2. Run Evaluation Replay (Stage 4)")
        print("3. Shutdown")

        opt = input("Select Option: ")

        if opt == "1":
            h_data, e_data, i_data = [], [], []
            p_e = None
            turn = 1

            while True:
                user_msg, source = get_user_input()
                if user_msg.lower() in ["exit", "quit", "back"]:
                    break

                res_e = classify_emotion(user_msg)
                res_i = classify_intent(user_msg)

                s_status = detect_mood_shift(p_e, res_e["label"])
                p_e = res_e["label"]

                bot_ans = generate_response(user_msg, res_i, res_e["label"])

                # Update records
                e_data.append(res_e)
                i_data = update_intent_log(i_data, res_i, turn)
                h_data.append({"source": source})

                emotion_display = res_e["emotion"]
                print(
                    f"\nAnalysis: [{emotion_display}] | Intent: {res_i} | Shift: {s_status}"
                )
                print(f"ARIA Agent: {bot_ans}")
                turn += 1

            if h_data:
                print_health_report(h_data, e_data, i_data)

        elif opt == "2":
            run_evaluation_audit()
        elif opt == "3":
            print("System offline.")
            break1


if __name__ == "__main__":
    main()

# Hi, I need help with my account
# I have a problem with payment
# What's the status of my refund?
# Goodbye, thanks!
