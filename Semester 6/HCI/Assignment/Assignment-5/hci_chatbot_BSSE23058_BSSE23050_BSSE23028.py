import sys
import string
import warnings
import time
import threading
import speech_recognition as sr
import pyttsx3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

warnings.filterwarnings('ignore')

# ============================================================
# ESC KEY LISTENER (Cross-platform)
# ============================================================
try:
    import keyboard
    KEYBOARD_LIB = True
except ImportError:
    KEYBOARD_LIB = False

esc_pressed = False

def esc_listener():
    global esc_pressed
    if KEYBOARD_LIB:
        keyboard.wait('esc')
        esc_pressed = True

def start_esc_listener():
    global esc_pressed
    esc_pressed = False
    if KEYBOARD_LIB:
        t = threading.Thread(target=esc_listener, daemon=True)
        t.start()

def reset_esc():
    global esc_pressed
    esc_pressed = False

# ============================================================
# MODULE 1 & 2: BRAIN (EXPANDED CLASSIFICATION)
# ============================================================
class ChatbotBrain:
    def __init__(self):

        # ---- EXPANDED SPAM KEYWORDS ----
        self.spam_keywords = [
            # Financial Scams
            'bitcoin', 'crypto', 'cryptocurrency', 'ethereum', 'nft', 'token',
            'free money', 'earn cash', 'make money fast', 'get rich', 'investment opportunity',
            'double your money', 'passive income', 'financial freedom', 'forex', 'trading signal',
            # Promotional / Clickbait
            'discount', 'click link', 'click here', '100%', 'guaranteed', 'limited offer',
            'act now', 'exclusive deal', 'special offer', 'buy now', 'order now', 'sale',
            'best price', 'cheapest', 'lowest price', 'free trial', 'no cost', 'risk free',
            # Prizes / Lottery
            'prize', 'winner', 'you won', 'congratulations', 'lottery', 'jackpot',
            'claim your reward', 'free gift', 'selected winner', 'lucky draw',
            # Suspicious Actions
            'subscribe', 'follow me', 'share this', 'viral', 'watch this video',
            'open this link', 'verify your account', 'confirm your details',
            'update your password', 'bank account', 'credit card', 'ssn', 'social security',
            # Degree / Credential Fraud
            'buy cheap degrees', 'fake certificate', 'instant degree', 'online diploma fast',
            'accredited fake', 'cheap certification'
        ]

        # ---- EXPANDED INTENT KEYWORDS ----
        self.intent_keywords = {
            'Admission': [
                'apply', 'admission', 'admissions', 'deadline', 'pucit', 'punjab university',
                'entry test', 'merit list', 'registration', 'enroll', 'enrollment', 'application form',
                'apply online', 'last date', 'form submission', 'eligibility', 'criteria',
                'intermediate', 'fsc', 'a level', 'hec', 'nts', 'ecat', 'pucat', 'pu-cat',
                'open merit', 'self finance', 'morning program', 'evening program', 'prospectus',
                'how to get admission', 'when does admission start', 'seat availability',
                'aggregate', 'marks required', 'minimum marks'
            ],
            'Fee': [
                'fee', 'fees', 'cost', 'charges', 'tuition', 'challan', 'scholarship',
                'payment', 'fee structure', 'semester fee', 'annual fee', 'monthly fee',
                'how much', 'total cost', 'expense', 'financial aid', 'need based',
                'merit scholarship', 'hec scholarship', 'ehsas', 'ihsan trust',
                'fee payment deadline', 'late fee', 'fine', 'dues', 'outstanding dues',
                'bank payment', 'online payment', 'fee challan form', 'hostel fee',
                'library charges', 'examination fee', 'registration fee'
            ],
            'Courses': [
                'bs cs', 'bs it', 'bs ai', 'bs se', 'bscs', 'bsit', 'bsai', 'bsse',
                'subjects', 'syllabus', 'degree', 'program', 'course', 'courses',
                'computer science', 'software engineering', 'information technology',
                'artificial intelligence', 'data science', 'cyber security',
                'curriculum', 'credit hours', 'elective', 'major', 'minor',
                'ms', 'phd', 'postgraduate', 'undergraduate', 'mcs',
                'what programs', 'available degrees', 'offered programs',
                'specialization', 'concentration', 'semesters', 'how many subjects'
            ],
            'Schedule': [
                'timetable', 'time table', 'timing', 'calendar', 'classes start',
                'exam date', 'schedule', 'class schedule', 'lecture time',
                'when does semester start', 'semester start', 'semester end',
                'midterm', 'final exam', 'paper date', 'date sheet',
                'holiday', 'break', 'winter break', 'summer break', 'eid holiday',
                'academic calendar', 'session', 'morning shift', 'evening shift',
                'lab timing', 'office hours', 'department timings', 'working hours'
            ]
        }

        # ---- EXPANDED TRAINING DATA ----
        self.spam_data = [
            # SPAM samples (label=1)
            ("click here for 100% discount on products", 1),
            ("earn bitcoin by clicking this link now", 1),
            ("get crypto for free guaranteed returns", 1),
            ("win prize money now act fast", 1),
            ("subscribe to my channel for free money", 1),
            ("buy cheap degrees online no exam required", 1),
            ("limited offer exclusive deal buy now", 1),
            ("you are selected winner claim your reward", 1),
            ("double your investment in forex trading", 1),
            ("get rich quick with crypto signals", 1),
            ("open this link to verify your bank account", 1),
            ("free trial no credit card required click now", 1),
            ("guaranteed passive income financial freedom", 1),
            ("nft token sale exclusive limited offer", 1),
            ("earn cash fast work from home opportunity", 1),
            ("congratulations you won the lucky draw prize", 1),
            ("special offer cheapest degree online", 1),
            ("share this viral video to win money", 1),
            ("update your password confirm your details now", 1),
            ("best price lowest cost act now buy", 1),
            # NON-SPAM samples (label=0)
            ("admission process at pucit lahore", 0),
            ("what are the semester fees at pu", 0),
            ("show me the class timetable", 0),
            ("how to apply for bs computer science", 0),
            ("hi hello good morning", 0),
            ("what programs are offered at pucit", 0),
            ("when does the next semester start", 0),
            ("tell me about faculty at pu", 0),
            ("where is the campus located", 0),
            ("what is the merit list criteria", 0),
            ("can you help me with admission form", 0),
            ("what is the fee structure for bs it", 0),
            ("tell me about bs ai program", 0),
            ("is hec scholarship available", 0),
            ("what are the exam dates", 0)
        ]

        self.intent_data = [
            ("admission apply deadline pucit entry test merit list register enrollment pucat aggregate eligibility", "Admission"),
            ("admission form submission last date criteria open merit self finance enroll how to apply morning evening", "Admission"),
            ("fee cost tuition payment scholarship charges fee structure semester annual challan hec ehsas", "Fee"),
            ("how much fees financial aid merit scholarship need based bank payment online payment registration fee", "Fee"),
            ("course degree subjects bs cs bs it bs ai bs se syllabus curriculum credit hours program", "Courses"),
            ("computer science software engineering artificial intelligence data science cyber security ms phd postgraduate", "Courses"),
            ("schedule timetable timing exam date calendar date sheet midterm final paper academic session", "Schedule"),
            ("when semester starts morning shift evening shift lab timing holiday break winter summer", "Schedule"),
            ("hi hello how are you what is your name thank you thanks okay bye goodbye", "Unknown"),
        ]

        self.train_models()

    def train_models(self):
        s_texts, s_labels = zip(*self.spam_data)
        self.spam_clf = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', MultinomialNB())
        ]).fit(s_texts, s_labels)

        i_texts, i_labels = zip(*self.intent_data)
        self.intent_clf = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', MultinomialNB())
        ]).fit(i_texts, i_labels)

    def keyword_match_spam(self, q_low):
        matched = [k for k in self.spam_keywords if k in q_low]
        return matched

    def keyword_match_intent(self, q_low):
        for intent, keys in self.intent_keywords.items():
            matched = [k for k in keys if k in q_low]
            if matched:
                return intent, matched
        return None, []

    def analyze(self, query):
        q_low = query.lower()

        # Safety valve: university terms are never spam
        uni_terms = [
            'admission', 'pucit', 'pu', 'fee', 'course', 'it', 'cs', 'apply',
            'punjab university', 'schedule'
        ]
        is_uni_query = any(term in q_low for term in uni_terms)

        # ---- KEYWORD-BASED SPAM CHECK ----
        spam_keywords_found = self.keyword_match_spam(q_low)
        s_prob = self.spam_clf.predict_proba([query])[0][1]
        is_spam = (
            (s_prob > 0.5 or len(spam_keywords_found) >= 2)  # Enhanced logic here.
            and not is_uni_query
        )

        # ---- KEYWORD-BASED INTENT CHECK ----
        keyword_intent, intent_keys_found = self.keyword_match_intent(q_low)
        if keyword_intent:
            detected_intent = keyword_intent
        else:
            detected_intent = self.intent_clf.predict([query])[0]

        i_probs = self.intent_clf.predict_proba([query])[0]
        i_conf = max(i_probs)

        # ---- CONFIDENCE SCORING ----
        if is_spam:
            s_score = min(s_prob + 0.2, 1.0)
            i_score = 0.05
            u_score = 0.0
        elif keyword_intent:
            s_score = s_prob
            i_score = max(i_conf, 0.75)
            u_score = 0.0
        elif detected_intent == "Unknown" or i_conf < 0.4:
            s_score = s_prob
            i_score = i_conf
            u_score = 1.0 - i_conf
        else:
            s_score = s_prob
            i_score = i_conf
            u_score = max(0.0, 1.0 - i_conf - s_prob)

        return (
            is_spam,
            detected_intent,
            round(s_score, 4),
            round(i_score, 4),
            round(u_score, 4),
            spam_keywords_found,
            intent_keys_found
        )


# ============================================================
# MODULE 3 & 4: VOICE, TTS & NAVIGATION
# ============================================================
class PU_System:
    def __init__(self):
        self.brain = ChatbotBrain()
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 2.0
        self.tts_engine = None

        self.responses = {
            'Admission': (
                "PUCIT / PU Admissions 2026: Applications are submitted online via pu.edu.pk. "
                "PU-CAT entry test is mandatory. Merit list is based on your FSc or A-level aggregate. "
                "Both Morning and Evening programs are available. Deadline is usually in August."
            ),
            'Fee': (
                "Fee Structure 2026: BS Morning programs cost approximately 45,000 PKR per semester. "
                "Evening programs cost approximately 85,000 PKR. HEC and Ehsaas scholarships are available "
                "for deserving students. Fee challan can be generated through the student portal."
            ),
            'Courses': (
                "Programs Offered at PUCIT: BS Computer Science, BS Software Engineering, BS Information Technology, "
                "BS Artificial Intelligence, BS Data Science, and BS Cyber Security. "
                "Postgraduate programs include MS and PhD in CS. Each program is 4 years with 8 semesters."
            ),
            'Schedule': (
                "Academic Schedule: Morning classes start at 8 AM and end at 2 PM. "
                "Evening classes run from 2 PM to 8 PM. Midterm exams are held in October and March. "
                "Final exams are in January and June. The full academic calendar is available on pu.edu.pk."
            ),
            'Unknown': (
                "I am sorry, I do not have specific information on that topic. "
                "I can help you with PU Admissions, Fee Structure, Available Courses, "
                "Class Schedule, Faculty Info, Campus Location, and Contact Details. "
                "Please ask me about any of these topics."
            ),
            'Spam': (
                "SECURITY ALERT: Your message has been flagged as SPAM or promotional content. "
                "This session will now be terminated for security reasons. "
                "Please restart the system if you have a genuine query about Punjab University."
            )
        }

    # ---- TTS ENGINE ----
    def speak(self, text):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 165)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS Error]: {e}")

    # ---- VOICE INPUT ----
    def listen(self):
        with sr.Microphone() as source:
            print("\n[LISTENING] Speak now... (Pause when done)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio)
                print(f"[VOICE CAPTURED]: {text}")
                return text
            except sr.WaitTimeoutError:
                print("[TIMEOUT] No speech detected.")
                return ""
            except sr.UnknownValueError:
                print("[ERROR] Could not understand audio.")
                return ""
            except Exception as e:
                print(f"[MIC ERROR]: {e}")
                return ""

    # ---- PROCESS INPUT ----
    def process(self, query, mode):
        if not query.strip():
            return "continue"

        print(f"\n[YOU]: {query}")

        result = self.brain.analyze(query)
        is_spam, intent, s_c, i_c, u_c, spam_kws, intent_kws = result

        # ---- PRINT ANALYSIS REPORT ----
        print("\n" + "=" * 55)
        print("  ANALYSIS REPORT")
        print("=" * 55)
        print(f"  Spam Confidence    : {s_c:.2%}")
        print(f"  Intent Confidence  : {i_c:.2%}  -> [{intent}]")
        print(f"  Unknown Confidence : {u_c:.2%}")
        if spam_kws:
            print(f"  Spam Keywords Found  : {', '.join(spam_kws)}")
        if intent_kws:
            print(f"  Intent Keywords Found: {', '.join(intent_kws)}")
        print("=" * 55)

        # ---- DECISION LOGIC ----
        if is_spam:
            final_intent = "Spam"
            reply = self.responses['Spam']
            self._print_bot_reply(final_intent, reply)
            if mode in ['2', '3']:
                self.speak(reply)
            print("\n[!] SPAM DETECTED - Session terminated. Returning to main menu...")
            time.sleep(2)
            return "spam_exit"

        elif u_c >= 0.65 or intent == "Unknown":
            final_intent = "Unknown"
            reply = self.responses['Unknown']

        else:
            final_intent = intent
            reply = self.responses.get(intent, self.responses['Unknown'])

        self._print_bot_reply(final_intent, reply)
        if mode in ['2', '3']:
            self.speak(reply)

        return "continue"

    def _print_bot_reply(self, intent_label, reply):
        print(f"\n[BOT - {intent_label}]:")
        print("-" * 55)
        print(f"  {reply}")
        print("-" * 55)

    # ---- SHOW MENU ----
    def show_menu(self, speak_mode=False):
        reset_esc()
        print("\n" + "#" * 55)
        print("  PU LAHORE INTELLIGENT CHATBOT SYSTEM V8.0")
        print("#" * 55)
        print("  1. Text Mode    - Type your queries")
        print("  2. Voice Mode   - Speak your queries (TTS enabled)")
        print("  3. Hybrid Mode  - Choose per query")
        print("  4. Exit System  - End the session completely")
        print("#" * 55)
        if speak_mode:
            self.speak("Main menu. Please select mode 1 for text, 2 for voice, 3 for hybrid, or 4 to exit.")

    # ---- MAIN ENTRY ----
    def start(self):
        print("\n[INFO] Press ESC at any time during a chat session to return to the main menu.")
        if not KEYBOARD_LIB:
            print("[WARNING] 'keyboard' library not found. ESC key detection disabled.")
            print("          Install with: pip install keyboard")
            print("          You can type 'menu' or 'exit' instead.\n")

        while True:
            self.show_menu()
            mode = input("\nSelect Mode (1/2/3/4): ").strip()

            if mode == '4':
                print("\n[SYSTEM] Thank you for using PU Lahore Chatbot. Goodbye!")
                if KEYBOARD_LIB:
                    pass
                sys.exit(0)

            if mode not in ['1', '2', '3']:
                print("[!] Invalid option. Please enter 1, 2, 3, or 4.")
                continue

            mode_names = {'1': 'Text Mode', '2': 'Voice Mode', '3': 'Hybrid Mode'}
            print(f"\n[ENTERING] {mode_names[mode]}")
            print("  Type 'menu' to return to main menu, 'exit' to quit the system.")
            if KEYBOARD_LIB:
                print("  Press ESC at any time to return to main menu.\n")
            start_esc_listener()

            # ---- CHAT LOOP ----
            while True:
                # Check ESC
                if KEYBOARD_LIB and esc_pressed:
                    print("\n[ESC PRESSED] Returning to main menu...")
                    time.sleep(0.5)
                    break

                user_input = ""

                try:
                    if mode == '1':
                        user_input = input("\nYou: ")

                    elif mode == '2':
                        print("\n[Press ENTER to speak, or type 'menu'/'exit']")
                        cmd = input(">> ").strip().lower()
                        if cmd in ['menu', 'm', 'back']:
                            break
                        if cmd in ['exit', 'quit']:
                            print("\n[SYSTEM] Goodbye!")
                            sys.exit(0)
                        user_input = self.listen()

                    elif mode == '3':
                        print("\n[T] Type  |  [V] Voice  |  [menu] Main Menu  |  [exit] Quit")
                        cmd = input("Choose: ").strip().lower()
                        if cmd in ['v', 'voice']:
                            user_input = self.listen()
                        elif cmd in ['t', 'text']:
                            user_input = input("You: ")
                        elif cmd in ['menu', 'm', 'back']:
                            break
                        elif cmd in ['exit', 'quit']:
                            print("\n[SYSTEM] Goodbye!")
                            sys.exit(0)
                        else:
                            print("[!] Invalid input. Type T, V, menu, or exit.")
                            continue

                except KeyboardInterrupt:
                    print("\n[CTRL+C] Returning to main menu...")
                    break

                # Check text commands
                if isinstance(user_input, str):
                    if user_input.strip().lower() in ['exit', 'quit']:
                        print("\n[SYSTEM] Goodbye!")
                        sys.exit(0)
                    if user_input.strip().lower() in ['menu', 'back', 'm']:
                        break
                    if not user_input.strip():
                        continue

                # Process the query
                result = self.process(user_input, mode)

                if result == "spam_exit":
                    # Spam detected: force back to menu
                    reset_esc()
                    break

                # Re-check ESC after processing
                if KEYBOARD_LIB and esc_pressed:
                    print("\n[ESC PRESSED] Returning to main menu...")
                    time.sleep(0.5)
                    break


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    PU_System().start()
