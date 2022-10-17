import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import TEST_DB_NAME


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = TEST_DB_NAME
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.new_question = {"question": "Test", "answer": "Neil", "category": 1,'difficulty':2}
        self.navigate_quizz_with_categ = {"previous_questions":[4], "quiz_category":{'id':5, 'type':'Entertainment'}}
        self.navigate_quizz_unknow_categ = {"previous_questions": [4], "quiz_category": {'id':1000, 'type':'Unknow'}}
        self.navigate_quizz_no_categ = {"previous_questions":[4], "quiz_category":{'id':0, 'type':'Click'}}
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))

    def test_405_retrieve_categories_not_allowed(self):
        res = self.client().post("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


    def test_retrieve_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))

    def test_404_retrieve_paginated_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/9")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 9).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["deleted"], 9)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        # data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


    def test_navigate_question_with_category(self):
        res = self.client().post("/quizzes", json= self.navigate_quizz_with_categ)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["question"]))
        self.assertEqual(str(data["question"]['category']),'5')


    def test_navigate_quizzes_no_category(self):
        res = self.client().post("/quizzes", json=self.navigate_quizz_no_categ)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["question"]))

    def test_navigate_question_unknow_category(self):
        res = self.client().post("/quizzes", json=self.navigate_quizz_unknow_categ)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_search_question(self):
        res = self.client().post("/questions", json={'searchTerm':'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertNotIn('categories', data)

    def test_405_search_question_not_allowed(self):
        res = self.client().put("/questions", json={'searchTerm':'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_get_question_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertNotIn('categories', data)

    def test_get_question_by_category_unknow(self):
        res = self.client().get("/categories/10000/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()