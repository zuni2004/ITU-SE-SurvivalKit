import os
import threading
import time
import warnings
import nltk
import numpy as np
import speech_recognition as sr
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Mute technical system output
warnings.filterwarnings("ignore")

try:
    nltk.data.find("vader_lexicon")
except (LookupError, AttributeError):
    nltk.download("vader_lexicon", quiet=True)

# ==============================================================================
# PIPELINE CONFIGURATION & DICTIONARIES
# ==============================================================================
PURPOSE_KEYWORDS = {
    "GRIEVANCE": [
        "problem",
        "issues",
        "broken",
        "error",
        "fail",
        "wrong",
        "terrible",
        "awful",
    ],
    "QUESTION": [
        "what",
        "how",
        "when",
        "where",
        "explain",
        "tell me",
        "does",
        "can you",
    ],
    "ASSISTANCE": ["help", "stuck", "assist", "cannot", "unable", "don't know"],
    "SUGGESTION": [
        "suggest",
        "improve",
        "recommend",
        "wish",
        "would be better",
        "should",
    ],
    "FINANCIAL": [
        "charge",
        "payment",
        "invoice",
        "refund",
        "price",
        "cost",
        "money",
    ],
    "EXIT": ["bye", "goodbye", "thanks", "thank you", "done", "that's all"],
}

MOOD_LABELS = {
    "JOYFUL": "JOYFUL",
    "POSITIVE": "POSITIVE",
    "BALANCED": "BALANCED",
    "NEGATIVE": "NEGATIVE",
    "AGITATED": "AGITATED",
}

MOOD_SCALES = {
    "AGITATED": 0,
    "NEGATIVE": 1,
    "BALANCED": 2,
    "POSITIVE": 3,
    "JOYFUL": 4,
}

# Core audio receiver instance
audio_receiver = sr.Recognizer()

# ==============================================================================
# PHASE 1: AUDIO CAPTURE AND SPEECH-TO-TEXT
# ==============================================================================


def capture_audio_stream(max_wait=6, sample_frequency=16000):
    print(f"\n>>> [IO_STREAM] Recording active (Timeout: {max_wait}s)... Please speak.")
    try:
        with sr.Microphone() as hardware_source:
            audio_receiver.adjust_for_ambient_noise(hardware_source, duration=0.5)
            raw_data = audio_receiver.listen(
                hardware_source, timeout=max_wait, phrase_time_limit=max_wait
            )
            print(">>> [IO_STREAM] Acoustic buffer captured successfully.")
            return raw_data
    except Exception as hardware_fault:
        print(f"Hardware Error Detected: {hardware_fault}")
        return None


def convert_audio_to_string(audio_data, sample_frequency=16000):
    if audio_data is None:
        return ""

    try:
        parsed_string = audio_receiver.recognize_google(audio_data)
        return parsed_string.strip()
    except sr.UnknownValueError:
        print("!!! [PARSING_ERR] Audio input could not be decoded.")
        return ""
    except sr.RequestError as network_fault:
        print(f"!!! [NET_ERR] Remote recognition server offline: {network_fault}")
        return "I have a problem with my account login failing."


def fetch_client_input():
    prompt_str = "\n💬 DIALOGUE > Provide text input or press [ENTER] to use voice: "
    raw_input_string = input(prompt_str).strip()

    if raw_input_string == "":
        voice_buffer = capture_audio_stream()
        processed_text = convert_audio_to_string(voice_buffer)
        print(f'Decoded: "{processed_text}"')
        return processed_text, "audio_mic"

    return raw_input_string, "keyboard_text"


# ==============================================================================
# PHASE 2: SENTIMENT AND MOOD METRICS
# ==============================================================================


def analyze_sentiment(input_text):
    vader_engine = SentimentIntensityAnalyzer()
    polarity_metrics = vader_engine.polarity_scores(input_text)
    metric_score = polarity_metrics["compound"]

    if metric_score >= 0.5:
        category = "JOYFUL"
    elif metric_score >= 0.05:
        category = "POSITIVE"
    elif metric_score > -0.05:
        category = "BALANCED"
    elif metric_score > -0.5:
        category = "NEGATIVE"
    else:
        category = "AGITATED"

    return {
        "tag": category,
        "score_value": metric_score,
        "sentiment_profile": MOOD_LABELS[category],
    }


def track_mood_variance(previous_tag, current_tag):
    if previous_tag is None:
        return "unaltered"

    rank_old = MOOD_SCALES.get(previous_tag, 2)
    rank_new = MOOD_SCALES.get(current_tag, 2)

    if rank_new < rank_old:
        return "worsening"
    if rank_new > rank_old:
        return "recovering"
    return "unaltered"


def compile_session_metrics(sentiment_history):
    if not sentiment_history:
        return {"modal_mood": "BALANCED", "mean_score": 0.0, "degradations": 0}

    numerical_scores = [entry["score_value"] for entry in sentiment_history]
    categorical_tags = [entry["tag"] for entry in sentiment_history]

    frequency_tracker = {}
    for tag in categorical_tags:
        frequency_tracker[tag] = frequency_tracker.get(tag, 0) + 1
    modal_mood = max(frequency_tracker, key=frequency_tracker.get)

    negative_transitions = 0
    for idx in range(len(categorical_tags) - 1):
        if MOOD_SCALES[categorical_tags[idx + 1]] < MOOD_SCALES[categorical_tags[idx]]:
            negative_transitions += 1

    return {
        "modal_mood": modal_mood,
        "mean_score": round(float(np.mean(numerical_scores)), 4),
        "degradations": negative_transitions,
    }


# ==============================================================================
# PHASE 3: INTENT STRATIFICATION & RESPONSE GENERATION
# ==============================================================================


def analyze_intent(input_text):
    normalized_text = input_text.lower()
    match_counters = {}

    for intention, keywords in PURPOSE_KEYWORDS.items():
        occurrences = sum(1 for word in keywords if word in normalized_text)
        if occurrences > 0:
            match_counters[intention] = occurrences

    if not match_counters:
        return "UNCATEGORIZED"

    return max(match_counters, key=match_counters.get)


def log_intent_transition(intent_history, current_intent, sequence_id):
    transition_event = None
    if intent_history:
        previous_intent = intent_history[-1]["active_state"]
        if previous_intent != current_intent:
            transition_event = {
                "origin": previous_intent,
                "destination": current_intent,
                "step": sequence_id,
            }

    intent_history.append(
        {"active_state": current_intent, "transition": transition_event}
    )
    return intent_history


def map_agent_reply(input_text, identified_intent, mood_tag):
    if identified_intent == "GRIEVANCE":
        if mood_tag == "AGITATED":
            return "Please accept my sincere apologies. I am transferring your session to our senior management team immediately."
        return "I recognize that you are facing a problem. Could you supply some more context?"

    if identified_intent == "FINANCIAL" and mood_tag in [
        "NEGATIVE",
        "AGITATED",
    ]:
        return "I understand your frustration regarding this financial issue. I am opening your ledger details right now."

    if identified_intent == "EXIT":
        return "Thank you for reaching out to our channel. Goodbye!"

    if identified_intent == "QUESTION":
        return "That is an important question. According to our current records, our processing staff is reviewing your case details."

    return "Thank you for providing that context. What else can I handle for you?"


# ==============================================================================
# PHASE 5: DIAGNOSTICS & SYSTEM REPORTING
# ==============================================================================


def generate_system_diagnostic(interaction_log, mood_log, intent_log):
    print("\n" + "=" * 55)
    print("             NEXUS SYSTEM COMPLIANCE REVIEW")
    print("=" * 55)

    interaction_count = len(interaction_log)
    voice_inputs = len(
        [entry for entry in interaction_log if entry["medium"] == "audio_mic"]
    )
    text_inputs = interaction_count - voice_inputs

    unique_intents = []
    total_transitions = 0
    for entry in intent_log:
        if entry["active_state"] not in unique_intents:
            unique_intents.append(entry["active_state"])
        if entry["transition"]:
            total_transitions += 1

    summary_data = compile_session_metrics(mood_log)
    average_polarity = summary_data["mean_score"]
    negative_shifts = summary_data["degradations"]

    # Session health algorithm
    appraisal_index = (
        50 + (average_polarity * 30) - (total_transitions * 5) - (negative_shifts * 8)
    )
    appraisal_index = int(np.clip(appraisal_index, 0, 100))

    if appraisal_index >= 70:
        resolution_strategy = "SUCCESS_CLOSE"
    elif appraisal_index >= 40:
        resolution_strategy = "OBSERVE_CASE"
    else:
        resolution_strategy = "CRITICAL_ROUTE"

    print(
        f"Total Transactions : {interaction_count} (Voice: {voice_inputs} | Text: {text_inputs})"
    )
    print(f"Identified Intents : {', '.join(unique_intents)}")
    print(f"Intent Deviations  : {total_transitions}")
    print(f"Prevailing Mood    : {summary_data['modal_mood']} ({average_polarity:.3f})")
    print(f"Mood Regressions   : {negative_shifts}")
    print("-" * 55)
    print(f"DIAGNOSTIC INDEX   : {appraisal_index}/100")
    print(f"DISPOSITION STATUS : {resolution_strategy}")
    print("=" * 55)


# ==============================================================================
# PHASE 4: REPLAY AUDITING SUITE
# ==============================================================================


def trigger_evaluation_audit():
    DUMMY_CONVERSATION = [
        "Hi, I need some help with my account.",
        "I have been trying to log in for two days but it keeps failing.",
        "This is really frustrating, I cannot believe this is still broken.",
        "Can you at least tell me when it will be fixed?",
        "Also I was charged twice last month — I want a refund.",
        "Actually you know what, forget it. I am going to cancel.",
        "Wait — actually I found the issue, it was my browser. Never mind!",
        "Thanks for your patience. Bye.",
    ]

    session_history, mood_history, intent_history = [], [], []
    prior_mood = None

    print("\n--- DEPLOYING CONVERSATION REPLAY PIPELINE ---")

    for index, string_payload in enumerate(DUMMY_CONVERSATION):
        mood_analysis = analyze_sentiment(string_payload)
        intent_analysis = analyze_intent(string_payload)

        variance = track_mood_variance(prior_mood, mood_analysis["tag"])
        prior_mood = mood_analysis["tag"]

        agent_output = map_agent_reply(
            string_payload, intent_analysis, mood_analysis["tag"]
        )

        mood_history.append(mood_analysis)
        intent_history = log_intent_transition(
            intent_history, intent_analysis, index + 1
        )
        session_history.append({"medium": "keyboard_text"})

        visual_mood = mood_analysis["sentiment_profile"]
        print(
            f"Step {index+1}: [{visual_mood}] | Class: {intent_analysis} | Flow: {variance}"
        )
        print(f"NEXUS-Agent: {agent_output}\n")

    generate_system_diagnostic(session_history, mood_history, intent_history)


# ==============================================================================
# SYSTEM MANAGEMENT ROUTER
# ==============================================================================


def main():
    while True:
        print("\n[ CENTRAL NEXUS CONSOLE ]")
        print("1. Initialize Communications Node (Live Feed)")
        print("2. Run Pipeline Replay Audit (Preset Batch)")
        print("3. Terminate Operation")

        selection = input("Action Code: ")

        if selection == "1":
            live_session, live_mood, live_intent = [], [], []
            tracking_mood = None
            iteration_step = 1

            while True:
                client_payload, medium_type = fetch_client_input()
                if client_payload.lower() in ["exit", "quit", "back"]:
                    break

                sentiment_out = analyze_sentiment(client_payload)
                intent_out = analyze_intent(client_payload)

                variance_state = track_mood_variance(
                    tracking_mood, sentiment_out["tag"]
                )
                tracking_mood = sentiment_out["tag"]

                bot_response = map_agent_reply(
                    client_payload, intent_out, sentiment_out["tag"]
                )

                live_mood.append(sentiment_out)
                live_intent = log_intent_transition(
                    live_intent, intent_out, iteration_step
                )
                live_session.append({"medium": medium_type})

                visual_tag = sentiment_out["sentiment_profile"]
                print(
                    f"\nMetrics: [{visual_tag}] | Scope: {intent_out} | Delta: {variance_state}"
                )
                print(f"NEXUS-Agent: {bot_response}")
                iteration_step += 1

            if live_session:
                generate_system_diagnostic(live_session, live_mood, live_intent)

        elif selection == "2":
            trigger_evaluation_audit()
        elif selection == "3":
            print("Process terminated. Connection closed.")
            break


if __name__ == "__main__":
    main()
