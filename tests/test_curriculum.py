import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from curriculum import CURRICULA
import db
import progress


APP = Path(__file__).resolve().parents[1] / "app.py"


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = str(Path(self.temp.name) / "scores.db")
        self.progress_file = str(Path(self.temp.name) / "progress.json")
        for name, value in [("db.DB_NAME", self.database),
                            ("progress.DATA_FILE", self.progress_file)]:
            patcher = patch(name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_class_4_generators(self):
        self.assertEqual(len(CURRICULA[4]), 4)
        for generator in CURRICULA[4].values():
            questions = generator()
            self.assertEqual(len(questions), 15)
            for question in questions:
                self.assertTrue({"question", "answer", "type", "topic",
                                 "worksheet_type"} <= question.keys())
                if question["type"] == "mcq":
                    self.assertIn(question["answer"], question["options"])

    def test_feedback_persists_until_next_question(self):
        def worksheet():
            return [{"question": "Test question", "answer": "7", "type": "fill"} for _ in range(3)]

        with patch.dict(CURRICULA[4], {"Fractions": worksheet}):
            app = AppTest.from_file(str(APP)).run()
            def click(label):
                next(b for b in app.button if b.label == label).click().run()
                self.assertFalse(app.exception)
            click("Start New Worksheet")
            app.text_input[0].input("6")
            click("Submit Answer")
            self.assertEqual(app.session_state.current, 0)
            self.assertIn("Correct answer: 7", app.error[0].value)
            self.assertTrue(app.text_input[0].disabled)
            self.assertTrue(next(b for b in app.button if b.label == "Submit Answer").disabled)
            app.run()
            self.assertIn("Correct answer: 7", app.error[0].value)
            self.assertEqual(len(app.session_state.user_answers), 1)
            click("Start New Worksheet")
            click("Keep Working")
            self.assertIn("Correct answer: 7", app.error[0].value)
            click("Next Question")
            self.assertEqual(app.session_state.current, 1)
            self.assertFalse(app.text_input[0].disabled)
            self.assertEqual(len(app.error), 0)
            app.text_input[0].input("7")
            click("Submit Answer")
            app.run()
            self.assertTrue(any("Correct!" in item.value for item in app.success))
            self.assertEqual(app.session_state.score, 1)
            self.assertEqual(len(app.session_state.user_answers), 2)
            click("Next Question")
            app.text_input[0].input("7")
            click("Submit Answer")
            self.assertEqual(len(db.get_scores()), 1)
            self.assertEqual(progress.load_progress()[0]["score"], 2)
            app.run()
            self.assertEqual(len(db.get_scores()), 1)

    def test_restart_and_exit_require_confirmation_preserve_drafts(self):
        def worksheet():
            return [{"question": "Test question", "answer": "7", "type": "fill"} for _ in range(3)]

        with patch.dict(CURRICULA[4], {"Fractions": worksheet}):
            app = AppTest.from_file(str(APP)).run()
            def click(label):
                next(b for b in app.button if b.label == label).click().run()
                self.assertFalse(app.exception)

            click("Start New Worksheet")
            original_id = app.session_state.worksheet_id
            original_start = app.session_state.start_time
            app.text_input[0].input("draft").run()
            click("Start New Worksheet")
            self.assertEqual(app.session_state.worksheet_id, original_id)
            self.assertEqual(app.text_input[0].value, "draft")
            self.assertTrue(next(b for b in app.button if b.label == "Submit Answer").disabled)
            click("Keep Working")
            self.assertEqual(app.text_input[0].value, "draft")
            app.text_input[0].input("7")
            click("Submit Answer")
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertEqual(app.session_state.score, 1)
            app.text_input[0].input("next draft").run()
            click("Start New Worksheet")
            click("Keep Working")
            self.assertEqual(app.session_state.current, 1)
            self.assertEqual(app.session_state.score, 1)
            self.assertEqual(app.session_state.start_time, original_start)
            self.assertEqual(app.text_input[0].value, "next draft")
            click("Exit Worksheet")
            click("Cancel Exit")
            self.assertEqual(app.text_input[0].value, "next draft")
            self.assertEqual(len(app.session_state.user_answers), 1)
            click("Start New Worksheet")
            click("Discard and Start New")
            self.assertNotEqual(app.session_state.worksheet_id, original_id)
            self.assertEqual(app.session_state.current, 0)
            self.assertEqual(app.session_state.score, 0)
            self.assertEqual(app.text_input[0].value, "")
            self.assertEqual(db.get_scores(), [])
            self.assertEqual(progress.load_progress(), [])
            app.text_input[0].input("7")
            click("Submit Answer")
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            click("Exit Worksheet")
            click("Yes, Exit")
            self.assertEqual(app.session_state.questions, [])
            self.assertFalse(app.selectbox(key="selected_class").disabled)
            self.assertEqual(db.get_scores(), [])
            self.assertEqual(progress.load_progress(), [])

    def test_legacy_sqlite_migration_preserves_scores(self):
        with sqlite3.connect(self.database) as conn:
            conn.execute("CREATE TABLE scores (id INTEGER PRIMARY KEY, module TEXT, "
                         "score INTEGER, total INTEGER, time_taken REAL, timestamp TEXT)")
            conn.execute("INSERT INTO scores VALUES (1, 'Fractions', 12, 15, 90, 'old')")
        db.init_db()
        db.init_db()  # Migration must be safe on subsequent Streamlit reruns.
        self.assertEqual(db.get_scores(), [(1, "Fractions", 12, 15, 90.0, "old", 4)])
        db.save_score("New chapter", 14, 15, 80, class_level=5)
        self.assertEqual([row[-1] for row in db.get_scores()], [5, 4])

    def test_legacy_json_and_new_class_round_trip(self):
        old = {"module": "Time", "score": 10, "total": 15, "time_taken": 100,
               "attempts": [{"question": "Old question"}]}
        Path(self.progress_file).write_text(json.dumps([old]))
        self.assertEqual(progress.load_progress()[0]["class_level"], 4)
        progress.save_progress("New chapter", 15, 15, 80, class_level=5)
        records = progress.load_progress()
        self.assertEqual([record["class_level"] for record in records], [4, 5])
        self.assertEqual(records[0]["attempts"], old["attempts"])

    def test_empty_class_and_class_4_exit(self):
        with patch.dict(CURRICULA, {5: {}}):
            self.check_empty_class_and_class_4_exit()

    def check_empty_class_and_class_4_exit(self):
        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("coming soon" in item.value for item in app.info))
        start = next(button for button in app.button if button.label == "Start New Worksheet")
        self.assertTrue(start.disabled)
        app.selectbox(key="selected_class").select(4).run()
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        self.assertTrue(app.selectbox(key="selected_class").disabled)
        self.assertTrue(app.selectbox(key="chapter_class_4").disabled)
        self.assertEqual(len(app.session_state.questions), 15)
        next(button for button in app.button if button.label == "Exit Worksheet").click().run()
        next(button for button in app.button if button.label == "Yes, Exit").click().run()
        self.assertFalse(app.selectbox(key="selected_class").disabled)
        self.assertEqual(db.get_scores(), [])
        self.assertFalse(app.exception)

    def test_new_class_routing_completion_and_parent_history(self):
        # A test-only chapter proves registration works without inventing curriculum.
        def worksheet(total_questions=15):
            return [{"question": "Test question", "answer": "7", "type": "fill",
                     "topic": "Test", "worksheet_type": "Test"}
                    for _ in range(total_questions)]

        with patch.dict(CURRICULA, {5: {"Test chapter": worksheet}}), \
                patch.dict("os.environ", {"PARENT_DASHBOARD_PIN": "test-pin"}):
            app = AppTest.from_file(str(APP)).run()
            app.selectbox(key="selected_class").select(5).run()
            next(button for button in app.button if button.label == "Start New Worksheet").click().run()
            app.sidebar.selectbox[0].select("Parent Dashboard").run()
            app.sidebar.selectbox[0].select("Student Practice").run()
            self.assertEqual(app.selectbox(key="selected_class").value, 5)
            self.assertEqual(app.selectbox(key="chapter_class_5").value, "Test chapter")
            for _ in range(15):
                app.text_input[0].input("7")
                next(button for button in app.button if button.label == "Submit Answer").click().run()
                if any(button.label == "Next Question" for button in app.button):
                    next(button for button in app.button if button.label == "Next Question").click().run()
                self.assertFalse(app.exception)
            score = db.get_scores()[0]
            self.assertEqual((score[1], score[2], score[3], score[-1]),
                             ("Test chapter", 15, 15, 5))
            self.assertEqual(len(progress.load_progress()[0]["attempts"]), 15)
            self.assertEqual(progress.load_progress()[0]["class_level"], 5)
            next(button for button in app.button if button.label == "Choose Another Chapter").click().run()
            self.assertFalse(app.selectbox(key="selected_class").disabled)
            app.sidebar.selectbox[0].select("Parent Dashboard").run()
            app.text_input[0].input("test-pin")
            next(button for button in app.button if button.label == "Unlock Dashboard").click().run()
            self.assertFalse(app.exception)
            self.assertIn("Class 5 | Test chapter", app.expander[0].label)

    def test_large_numbers_full_worksheet(self):
        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        self.assertEqual(app.selectbox(key="chapter_class_5").value, "Large Numbers")
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        for index in range(15):
            q = app.session_state.questions[index]
            if "chart" in q:
                self.assertEqual(len(app.table), 1)
            if q["type"] == "fill":
                answer = q["answer"]
                if q["answer_format"] in ("integer", "integer_list"):
                    answer = answer.replace(",", "")
                elif q["answer_format"] == "number_words":
                    answer = answer.upper().replace(" ", "-")
                elif q["answer_format"] == "roman":
                    answer = answer.lower()
                app.text_input[0].input(answer)
            else:
                app.radio[0].set_value(q["answer"])
            next(button for button in app.button if button.label == "Submit Answer").click().run()
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual((record["class_level"], record["module"], record["score"]),
                         (5, "Large Numbers", 15))
        self.assertEqual(len(record["attempts"]), 15)

    def test_addition_subtraction_full_worksheet(self):
        from curriculum.class_5.addition_subtraction import CHAPTER_NAME

        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        app.selectbox(key="chapter_class_5").select(CHAPTER_NAME).run()
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        for index in range(15):
            q = app.session_state.questions[index]
            if q["type"] == "fill":
                app.text_input[0].input(q["answer"].replace(",", ""))
            else:
                app.radio[0].set_value(q["answer"])
            next(button for button in app.button if button.label == "Submit Answer").click().run()
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual((record["class_level"], record["module"], record["score"]),
                         (5, CHAPTER_NAME, 15))
        self.assertEqual(db.get_scores()[0][1], CHAPTER_NAME)
        self.assertEqual(len(record["attempts"]), 15)

    def test_unit_validation_in_worksheet(self):
        from curriculum.class_4 import measurement_module as measurement

        with patch.object(measurement.random, "choice", return_value=True), patch.object(measurement.random, "randint", return_value=1):
            q = measurement.convert_length()
        with patch.dict(CURRICULA[4], {"Measurement": lambda: [dict(q) for _ in range(4)]}):
            app = AppTest.from_file(str(APP)).run()
            app.selectbox(key="chapter_class_4").select("Measurement").run()
            next(button for button in app.button if button.label == "Start New Worksheet").click().run()
            for answer in ["1000 kg", "1000 metres", "1000", "1000 m junk"]:
                app.text_input[0].input(answer)
                next(button for button in app.button if button.label == "Submit Answer").click().run()
                if any(button.label == "Next Question" for button in app.button):
                    next(button for button in app.button if button.label == "Next Question").click().run()
                self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual(record["score"], 2)
        self.assertEqual([a["is_correct"] for a in record["attempts"]], [False, True, True, False])
        self.assertEqual(record["attempts"][0]["correct_answer"], "1000 m")

    def test_class4_equivalent_fraction_answers_saved(self):
        from curriculum.class_4 import fractions_module as fractions
        from unittest.mock import patch

        with patch.object(fractions.random, "randint", side_effect=[4, 1, 1]):
            half = fractions.addition_like()
        with patch.object(fractions.random, "randint", side_effect=[3, 2, 2]):
            zero = fractions.subtraction_like()
        with patch.dict(CURRICULA[4], {"Fractions": lambda: [half, zero]}):
            app = AppTest.from_file(str(APP)).run()
            next(button for button in app.button if button.label == "Start New Worksheet").click().run()
            for answer in ["2/4", "0"]:
                app.text_input[0].input(answer)
                next(button for button in app.button if button.label == "Submit Answer").click().run()
                if any(button.label == "Next Question" for button in app.button):
                    next(button for button in app.button if button.label == "Next Question").click().run()
                self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual(record["score"], 2)
        self.assertEqual(record["class_level"], 4)
        self.assertEqual([a["your_answer"] for a in record["attempts"]], ["2/4", "0"])
        self.assertTrue(all(a["is_correct"] for a in record["attempts"]))

    def test_class5_fractions_full_worksheet(self):
        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        app.selectbox(key="chapter_class_5").select("Fractions").run()
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        for index in range(15):
            q = app.session_state.questions[index]
            if q["type"] == "fill":
                app.text_input[0].input(q["answer"])
            else:
                app.radio[0].set_value(q["answer"])
            next(button for button in app.button if button.label == "Submit Answer").click().run()
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual((record["module"], record["score"], record["class_level"]), ("Fractions", 15, 5))
        self.assertEqual(sum("solution_chart" in a for a in record["attempts"]), 3)

    def test_multiples_factors_full_worksheet(self):
        from curriculum.class_5.multiples_factors import CHAPTER_NAME

        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        app.selectbox(key="chapter_class_5").select(CHAPTER_NAME).run()
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        for index in range(15):
            q = app.session_state.questions[index]
            if q["type"] == "fill":
                app.text_input[0].input(q["answer"])
            else:
                app.radio[0].set_value(q["answer"])
            next(button for button in app.button if button.label == "Submit Answer").click().run()
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual((record["module"], record["score"], record["class_level"]), (CHAPTER_NAME, 15, 5))
        self.assertEqual(sum("solution_chart" in a for a in record["attempts"]), 2)
        self.assertEqual(sum("solution_diagram" in a for a in record["attempts"]), 1)

    def test_multiplication_division_full_worksheet(self):
        from curriculum.class_5.multiplication_division import CHAPTER_NAME

        app = AppTest.from_file(str(APP)).run()
        app.selectbox(key="selected_class").select(5).run()
        app.selectbox(key="chapter_class_5").select(CHAPTER_NAME).run()
        next(button for button in app.button if button.label == "Start New Worksheet").click().run()
        for index in range(15):
            q = app.session_state.questions[index]
            if "diagram" in q:
                self.assertTrue(any("<svg" in item.proto.srcdoc for item in app.get("iframe")))
            if q["type"] == "fill":
                app.text_input[0].input(q["answer"].replace(",", "").replace(" R ", " remainder "))
            else:
                app.radio[0].set_value(q["answer"])
            next(button for button in app.button if button.label == "Submit Answer").click().run()
            if any(button.label == "Next Question" for button in app.button):
                next(button for button in app.button if button.label == "Next Question").click().run()
            self.assertFalse(app.exception)
        record = progress.load_progress()[0]
        self.assertEqual((record["class_level"], record["module"], record["score"]),
                         (5, CHAPTER_NAME, 15))
        self.assertEqual(db.get_scores()[0][1], CHAPTER_NAME)
        self.assertEqual(len(record["attempts"]), 15)


if __name__ == "__main__":
    unittest.main()
