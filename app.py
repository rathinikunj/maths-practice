import streamlit as st
import streamlit.components.v1 as components
import os
import re
import fractions_module
import measurement_module
import perimeter_area_module
import time_module
import db
import utils
import pandas as pd
from progress import load_progress, save_progress, reset_progress, calculate_badges

db.init_db()
# Fall back to 1234 when env var is missing or blank.
PARENT_DASHBOARD_PIN = os.getenv("PARENT_DASHBOARD_PIN") or "1234"

st.markdown(
    """
    <style>
    /* Keep control focus/active styles neutral (no red highlight). */
    .stTextInput input,
    .stTextInput input:focus,
    .stTextInput input:focus-visible,
    .stTextInput input[aria-invalid="true"],
    .stTextInput [data-baseweb="input"] input,
    .stTextInput [data-baseweb="input"] input:focus,
    .stTextInput [data-baseweb="input"] input:focus-visible,
    .stTextInput [data-baseweb="input"] input[aria-invalid="true"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div:focus-within,
    .stSelectbox [data-baseweb="select"] > div[data-focused="true"],
    .stSelectbox [data-baseweb="select"] > div[aria-invalid="true"],
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="input"] input[aria-invalid="true"],
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div[aria-invalid="true"],
    div[data-baseweb="base-input"] input:focus,
    textarea:focus,
    textarea:focus-visible {
        border-color: #94a3b8 !important;
        box-shadow: 0 0 0 1px #94a3b8 !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

UNIT_ALIASES = {
    "kilogram": "kg",
    "kilograms": "kg",
    "kg": "kg",
    "gram": "g",
    "grams": "g",
    "g": "g",
    "litre": "l",
    "litres": "l",
    "liter": "l",
    "liters": "l",
    "l": "l",
    "millilitre": "ml",
    "millilitres": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "ml": "ml",
    "metre": "m",
    "metres": "m",
    "meter": "m",
    "meters": "m",
    "m": "m",
    "centimetre": "cm",
    "centimetres": "cm",
    "centimeter": "cm",
    "centimeters": "cm",
    "cm": "cm",
    "kilometre": "km",
    "kilometres": "km",
    "kilometer": "km",
    "kilometers": "km",
    "km": "km",
    "hour": "hr",
    "hours": "hr",
    "hr": "hr",
    "minute": "min",
    "minutes": "min",
    "min": "min",
    "day": "day",
    "days": "day",
}


def normalize_text(value):
    return " ".join(str(value).strip().lower().split())


def normalize_number(value):
    if re.fullmatch(r"-?\d+", value):
        return str(int(value))
    if re.fullmatch(r"-?\d+\.\d+", value):
        return str(float(value)).rstrip("0").rstrip(".")
    return value


def canonicalize_unit(unit):
    cleaned = unit.strip().lower().replace(".", "")
    return UNIT_ALIASES.get(cleaned, cleaned)


def parse_number_with_optional_unit(text):
    match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s*", text)
    if not match:
        return None
    number = normalize_number(match.group(1))
    unit = match.group(2)
    return number, canonicalize_unit(unit) if unit else None


def parse_quantity_pairs(text):
    pairs = re.findall(r"(-?\d+(?:\.\d+)?)\s*([a-zA-Z]+)", text.lower())
    if not pairs:
        return None
    return [(normalize_number(n), canonicalize_unit(u)) for n, u in pairs]


def answers_match(user_answer, correct_answer, question_type):
    if user_answer is None:
        return False

    user_norm = normalize_text(user_answer)
    correct_norm = normalize_text(correct_answer)

    if question_type in ("mcq", "true_false"):
        return user_norm == correct_norm

    if user_norm == correct_norm:
        return True

    if user_norm.replace(" ", "") == correct_norm.replace(" ", ""):
        return True

    if re.fullmatch(r"-?\d+(?:\.\d+)?", correct_norm):
        user_number = parse_number_with_optional_unit(user_answer)
        if user_number and user_number[0] == normalize_number(correct_norm):
            return True

    correct_pairs = parse_quantity_pairs(correct_answer)
    user_pairs = parse_quantity_pairs(user_answer)
    if correct_pairs and user_pairs and correct_pairs == user_pairs:
        return True

    return False


def sanitize_question(question):
    if question.get("type") != "mcq":
        return question

    answer = str(question.get("answer", "")).strip()
    options = [str(option).strip() for option in question.get("options", []) if str(option).strip()]

    # Keep options unique while preserving order.
    seen = set()
    deduped_options = []
    for option in options:
        key = option.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped_options.append(option)

    if answer and answer.lower() not in {option.lower() for option in deduped_options}:
        if len(deduped_options) >= 4:
            deduped_options[0] = answer
        else:
            deduped_options.append(answer)

    question["options"] = deduped_options
    return question


def sanitize_questions(questions):
    return [sanitize_question(question) for question in questions]


def show_live_timer(start_time):
    start_ms = int(start_time * 1000)
    components.html(
        f"""
        <div style="display:flex; justify-content:flex-end; align-items:center;">
            <div style="
                min-width: 50px;
                text-align: center;
                padding: 10px 14px;
                border-radius: 12px;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border: 1px solid #334155;
                color: #f8fafc;
                box-shadow: 0 6px 14px rgba(15, 23, 42, 0.35);
            ">
                <div style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: #93c5fd;">Timer</div>
                <div id="live-timer" style="font-size: 1.25rem; font-weight: 700; margin-top: 2px;">00:00</div>
            </div>
        </div>
        <script>
        const start = {start_ms};
        function pad(n) {{ return String(n).padStart(2, '0'); }}
        function tick() {{
            const seconds = Math.max(0, Math.floor((Date.now() - start) / 1000));
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            const timer = document.getElementById("live-timer");
            if (timer) timer.textContent = `${{pad(mins)}}:${{pad(secs)}}`;
        }}
        tick();
        setInterval(tick, 1000);
        </script>
        """,
        height=84,
    )

st.title("🏆 Maths Champions - Class 4")
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Student Practice", "Parent Dashboard"]
)
previous_mode = st.session_state.get("last_mode")
if previous_mode == "Parent Dashboard" and mode == "Student Practice":
    st.session_state.parent_dashboard_unlocked = False
st.session_state.last_mode = mode

if mode == "Student Practice":
    module = st.selectbox(
        "Select Module",
        ["Fractions", "Measurement", "Perimeter & Area", "Time"]
    )

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.score = 0
        st.session_state.current = 0
        st.session_state.start_time = None
    if "confirm_exit_worksheet" not in st.session_state:
        st.session_state.confirm_exit_worksheet = False


    def start_worksheet():

        if module == "Fractions":
            st.session_state.questions = fractions_module.generate_balanced_worksheet()
        elif module == "Measurement":
            st.session_state.questions = measurement_module.generate_balanced_worksheet()
        elif module == "Perimeter & Area":
            st.session_state.questions = perimeter_area_module.generate_balanced_worksheet()
        else:
            st.session_state.questions = time_module.generate_balanced_worksheet()
        st.session_state.questions = sanitize_questions(st.session_state.questions)

        st.session_state.score = 0
        st.session_state.current = 0
        st.session_state.start_time = utils.start_timer()
        st.session_state.user_answers = []
        st.session_state.confirm_exit_worksheet = False

    if st.button("Start New Worksheet"):
        start_worksheet()

    if st.session_state.questions:
        q = sanitize_question(st.session_state.questions[st.session_state.current])

        header_col, timer_col = st.columns([3, 2])
        with header_col:
            st.write(f"### Question {st.session_state.current + 1}")
        with timer_col:
            if st.session_state.start_time:
                show_live_timer(st.session_state.start_time)

        # Allow exiting only before first attempted question.
        if st.session_state.current == 0 and not st.session_state.user_answers:
            if not st.session_state.confirm_exit_worksheet:
                if st.button("Exit Worksheet"):
                    st.session_state.confirm_exit_worksheet = True
                    st.rerun()
            else:
                st.warning("Exit worksheet without saving progress?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Yes, Exit"):
                        st.session_state.questions = []
                        st.session_state.current = 0
                        st.session_state.score = 0
                        st.session_state.start_time = None
                        st.session_state.user_answers = []
                        st.session_state.confirm_exit_worksheet = False
                        st.rerun()
                with cancel_col:
                    if st.button("Cancel Exit"):
                        st.session_state.confirm_exit_worksheet = False
                        st.rerun()

        widget_key_base = f"q_{module}_{st.session_state.current}"
        st.write(q["question"])

        user_answer = None

        if q["type"] == "mcq":
            user_answer = st.radio("Choose answer:", q["options"], key=f"{widget_key_base}_mcq")
        elif q["type"] == "true_false":
            user_answer = st.radio("Select:", ["True", "False"], key=f"{widget_key_base}_tf")
        else:
            user_answer = st.text_input("Your answer:", key=f"{widget_key_base}_fill")

        if st.button("Submit Answer", key=f"{widget_key_base}_submit"):

            correct = answers_match(user_answer, q["answer"], q["type"])

            # Save attempt
            st.session_state.user_answers.append({
                "question": q["question"],
                "your_answer": user_answer,
                "correct_answer": q["answer"],
                "is_correct": correct
            })

            if correct:
                st.success("Correct! ⚽ Goal!")
                st.session_state.score += 1
            else:
                st.error(f"Wrong! Correct answer: {q['answer']}")

            st.session_state.current += 1

            if st.session_state.current >= len(st.session_state.questions):

                time_taken = utils.stop_timer(st.session_state.start_time)
                total_questions = len(st.session_state.questions)
                db.save_score(module, st.session_state.score, total_questions, time_taken)
                save_progress(
                    module=module,
                    score=st.session_state.score,
                    total=total_questions,
                    time_taken=round(time_taken),
                    attempts=list(st.session_state.user_answers)
                )

                st.write("## 🎉 Worksheet Completed!")
                st.write(f"Score: {st.session_state.score}/{total_questions}")
                st.write(f"Time Taken: {time_taken} seconds")

                # Show detailed review
                st.write("## 📝 Worksheet Review")

                for idx, result in enumerate(st.session_state.user_answers):
                    icon = "✅" if result["is_correct"] else "❌"
                    st.write(f"### Question {idx+1} {icon}")
                    st.write(f"**Q:** {result['question']}")
                    st.write(f"Your Answer: {result['your_answer']}")
                    st.write(f"Correct Answer: {result['correct_answer']}")
                    st.markdown("---")

                st.session_state.questions = []
            else:
                st.rerun()


    # 📊 Score History

    st.write("## 📈 Past Performance")

    scores = db.get_scores()

    if scores:
        df = pd.DataFrame(scores, columns=["ID", "Module", "Score", "Total", "Time", "Date"])
        st.dataframe(df.drop(columns=["ID"]))

elif mode == "Parent Dashboard":

    st.title("📊 Parent Dashboard")
    if "parent_dashboard_unlocked" not in st.session_state:
        st.session_state.parent_dashboard_unlocked = False

    if not st.session_state.parent_dashboard_unlocked:
        entered_pin = st.text_input("Enter Parent PIN", type="password")
        if st.button("Unlock Dashboard"):
            if entered_pin == PARENT_DASHBOARD_PIN:
                st.session_state.parent_dashboard_unlocked = True
                st.success("Dashboard unlocked.")
                st.rerun()
            else:
                st.error("Incorrect PIN.")
        st.stop()

    if st.button("Lock Dashboard"):
        st.session_state.parent_dashboard_unlocked = False
        st.rerun()

    if st.button("🧹 Clear Past Performance"):
        db.clear_scores()
        reset_progress()
        st.success("Past performance cleared.")
        st.rerun()

    data = load_progress()

    if not data:
        st.info("No worksheets completed yet.")
    else:
        total_attempts = len(data)
        total_correct = sum(d["score"] for d in data)
        total_questions = sum(d["total"] for d in data)

        avg_score = total_correct / total_questions * 100
        avg_time = sum(d["time_taken"] for d in data) / total_attempts

        st.metric("Total Worksheets", total_attempts)
        st.metric("Average Accuracy (%)", f"{avg_score:.2f}")
        st.metric("Average Time (sec)", f"{avg_time:.0f}")

        st.subheader("📜 History")

        for idx, d in enumerate(data[::-1], start=1):
            timestamp = d.get("timestamp", "No timestamp")
            with st.expander(
                f"Worksheet {idx}: {d['module']} | "
                f"Score {d['score']}/{d['total']} | "
                f"Time {d['time_taken']} sec | {timestamp}"
            ):
                attempts = d.get("attempts", [])
                if not attempts:
                    st.info("Detailed question review not available for this older worksheet.")
                else:
                    for q_idx, result in enumerate(attempts, start=1):
                        icon = "✅" if result.get("is_correct") else "❌"
                        st.write(f"**Q{q_idx} {icon}** {result.get('question', '')}")
                        st.write(f"Your Answer: {result.get('your_answer', '')}")
                        st.write(f"Correct Answer: {result.get('correct_answer', '')}")
                        st.markdown("---")

        st.subheader("🏅 Football Badges")

        badges = calculate_badges(data)

        if badges:
            for badge in badges:
                st.success(badge)
        else:
            st.info("No badges yet. Keep practicing!")

        if st.button("🔴 Reset All Progress"):
            db.clear_scores()
            reset_progress()
            st.success("Progress reset successfully.")
            st.rerun()
