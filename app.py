import streamlit as st
import streamlit.components.v1 as components
import os
import re
from curriculum import CURRICULA
from uuid import uuid4
from answer_validation import formatted_answers_match
from quantity_answers import quantity_answers_match
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

def normalize_text(value):
    return " ".join(str(value).strip().lower().split())


def normalize_number(value):
    if re.fullmatch(r"-?\d+", value):
        return str(int(value))
    if re.fullmatch(r"-?\d+\.\d+", value):
        return str(float(value)).rstrip("0").rstrip(".")
    return value


def answers_match(user_answer, correct_answer, question_type, answer_format=None, expected_unit=None):
    if user_answer is None:
        return False

    user_norm = normalize_text(user_answer)
    correct_norm = normalize_text(correct_answer)

    if question_type in ("mcq", "true_false"):
        return user_norm == correct_norm

    if expected_unit is not None:
        return quantity_answers_match(user_answer, correct_answer, expected_unit)

    if answer_format:
        return formatted_answers_match(user_answer, correct_answer, answer_format)

    if user_norm == correct_norm:
        return True

    if user_norm.replace(" ", "") == correct_norm.replace(" ", ""):
        return True

    if re.fullmatch(r"-?\d+(?:\.\d+)?", correct_norm) and re.fullmatch(r"-?\d+(?:\.\d+)?", user_norm):
        return normalize_number(user_norm) == normalize_number(correct_norm)

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


def show_solution(result):
    if result.get("solution_diagram"):
        components.html(result["solution_diagram"], height=220, scrolling=True)
    if result.get("solution_chart"):
        st.table(pd.DataFrame(result["solution_chart"]).astype(str))


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

st.title("🏆 Maths Champions")
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Student Practice", "Parent Dashboard"]
)
previous_mode = st.session_state.get("last_mode")
if previous_mode == "Parent Dashboard" and mode == "Student Practice":
    st.session_state.parent_dashboard_unlocked = False
st.session_state.last_mode = mode

if mode == "Student Practice":
    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.score = 0
        st.session_state.current = 0
        st.session_state.start_time = None
    if "confirm_exit_worksheet" not in st.session_state:
        st.session_state.confirm_exit_worksheet = False

    st.session_state.setdefault("confirm_restart_worksheet", False)

    worksheet_active = bool(st.session_state.questions)
    if worksheet_active:
        # Restore selectors when returning from the parent dashboard, where
        # Streamlit may have cleaned up widgets that were not displayed.
        active_class = st.session_state.worksheet_class
        st.session_state.selected_class = active_class
        st.session_state[f"chapter_class_{active_class}"] = st.session_state.worksheet_module
    class_level = st.selectbox(
        "Select Class", list(CURRICULA),
        format_func=lambda value: f"Class {value}",
        key="selected_class", disabled=worksheet_active,
    )
    chapters = CURRICULA[class_level]
    module = st.selectbox(
        "Select Chapter", list(chapters), key=f"chapter_class_{class_level}",
        disabled=worksheet_active or not chapters,
    )
    if not chapters:
        st.info(f"Class {class_level} chapters are coming soon. Please choose Class 4 to practise meanwhile.")
    if worksheet_active:
        st.caption("Class and chapter stay fixed until this worksheet ends.")

    def start_worksheet():

        st.session_state.questions = chapters[module]()
        st.session_state.questions = sanitize_questions(st.session_state.questions)
        st.session_state.worksheet_class = class_level
        st.session_state.worksheet_module = module
        st.session_state.worksheet_id = uuid4().hex

        st.session_state.score = 0
        st.session_state.current = 0
        st.session_state.start_time = utils.start_timer()
        st.session_state.user_answers = []
        st.session_state.confirm_exit_worksheet = False
        st.session_state.confirm_restart_worksheet = False

    def request_new_worksheet():
        if st.session_state.questions:
            st.session_state.confirm_restart_worksheet = True
            st.session_state.confirm_exit_worksheet = False
        else:
            start_worksheet()

    def request_exit():
        st.session_state.confirm_exit_worksheet = True
        st.session_state.confirm_restart_worksheet = False

    def cancel_discard():
        st.session_state.confirm_exit_worksheet = False
        st.session_state.confirm_restart_worksheet = False

    def exit_worksheet():
        st.session_state.questions = []
        st.session_state.current = 0
        st.session_state.score = 0
        st.session_state.start_time = None
        st.session_state.user_answers = []
        cancel_discard()

    st.button("Start New Worksheet", disabled=not chapters, on_click=request_new_worksheet)

    if st.session_state.questions:
        q = sanitize_question(st.session_state.questions[st.session_state.current])
        unit_label = {"cm2": "cm²", "square": "squares"}.get(q.get("expected_unit"), q.get("expected_unit"))
        correct_answer_label = f"{q['answer']} {unit_label}" if unit_label else q["answer"]

        header_col, timer_col = st.columns([3, 2])
        with header_col:
            st.write(f"### Question {st.session_state.current + 1}")
        with timer_col:
            if st.session_state.start_time:
                show_live_timer(st.session_state.start_time)

        st.button("Exit Worksheet", on_click=request_exit)
        if st.session_state.confirm_restart_worksheet:
            st.warning("Start a new worksheet? Your unfinished worksheet and answers will be discarded without saving.")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                st.button("Discard and Start New", on_click=start_worksheet)
            with cancel_col:
                st.button("Keep Working", on_click=cancel_discard)
        elif st.session_state.confirm_exit_worksheet:
            st.warning("Exit worksheet? Your unfinished worksheet and answers will be discarded without saving.")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                st.button("Yes, Exit", on_click=exit_worksheet)
            with cancel_col:
                st.button("Cancel Exit", on_click=cancel_discard)

        widget_key_base = f"q_{st.session_state.worksheet_id}_{st.session_state.current}"
        st.write(q["question"])
        if unit_label:
            st.caption(f"Answer in {unit_label}. You may enter the number alone or include the unit.")
        if "chart" in q:
            st.table(pd.DataFrame(q["chart"]))
        if "diagram" in q:
            components.html(q["diagram"], height=220, scrolling=True)
        if "hint" in q:
            st.caption(q["hint"])

        submitted = len(st.session_state.user_answers) > st.session_state.current
        pending_discard = st.session_state.confirm_restart_worksheet or st.session_state.confirm_exit_worksheet
        input_suffix = "mcq" if q["type"] == "mcq" else "tf" if q["type"] == "true_false" else "fill"
        input_key = f"{widget_key_base}_{input_suffix}"

        def submit_answer():
            # The saved attempt is also the submission guard across reruns.
            if len(st.session_state.user_answers) > st.session_state.current:
                return
            answer = st.session_state[input_key]
            correct = answers_match(answer, q["answer"], q["type"], q.get("answer_format"), q.get("expected_unit"))
            st.session_state.user_answers.append({
                "question": q["question"],
                "your_answer": answer,
                "correct_answer": correct_answer_label,
                "is_correct": correct,
                **{key: q[key] for key in ("solution_diagram", "solution_chart") if key in q},
            })
            if correct:
                st.session_state.score += 1

        def next_question():
            if len(st.session_state.user_answers) == st.session_state.current + 1:
                st.session_state.current += 1

        if q["type"] == "mcq":
            st.radio("Choose answer:", q["options"], key=input_key, disabled=submitted)
        elif q["type"] == "true_false":
            st.radio("Select:", ["True", "False"], key=input_key, disabled=submitted)
        else:
            st.text_input("Your answer:", key=input_key, disabled=submitted)

        st.button("Submit Answer", key=f"{widget_key_base}_submit",
                  disabled=submitted or pending_discard, on_click=submit_answer)

        if submitted:
            result = st.session_state.user_answers[st.session_state.current]
            if result["is_correct"]:
                st.success("Correct! ⚽ Goal!")
            else:
                st.error(f"Wrong! Correct answer: {result['correct_answer']}")
            show_solution(result)

            if len(st.session_state.user_answers) >= len(st.session_state.questions):

                time_taken = utils.stop_timer(st.session_state.start_time)
                total_questions = len(st.session_state.questions)
                db.save_score(
                    st.session_state.worksheet_module, st.session_state.score,
                    total_questions, time_taken,
                    class_level=st.session_state.worksheet_class,
                )
                save_progress(
                    module=st.session_state.worksheet_module,
                    score=st.session_state.score,
                    total=total_questions,
                    time_taken=round(time_taken),
                    attempts=list(st.session_state.user_answers),
                    class_level=st.session_state.worksheet_class,
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
                    show_solution(result)
                    st.markdown("---")

                st.session_state.questions = []
                st.button("Choose Another Chapter")
            else:
                st.button("Next Question", key=f"{widget_key_base}_next",
                          disabled=pending_discard, on_click=next_question)


    # 📊 Score History

    st.write("## 📈 Past Performance")

    scores = db.get_scores()

    if scores:
        df = pd.DataFrame(scores, columns=["ID", "Chapter", "Score", "Total", "Time", "Date", "Class"])
        st.dataframe(df[["Class", "Chapter", "Score", "Total", "Time", "Date"]])

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
                f"Worksheet {idx}: Class {d['class_level']} | {d['module']} | "
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
                        show_solution(result)
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
