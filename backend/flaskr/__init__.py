import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

ITEMS_PER_PAGE = 10

def base_retrieve_questions(selection, categ_id=None, with_categ=True):

    current_questions = paginate_items(request, selection)
    current_category = Category.query.filter(Category.id == categ_id).one_or_none()
    current_categ_name = None
    if not current_category:
        """Provide a default category if no category is provided"""
        current_categ_name = 'All'
    else:
        current_categ_name = current_category.type

    if len(current_questions) == 0:
        abort(404)

    res = {
            "questions": current_questions,
            "totalQuestions": selection.count(),
            "currentCategory": current_categ_name
        }

    if with_categ:
        res[ 'categories'] = get_categories_for_api()

    return jsonify(
        res
    )

def from_categobjects_to_dict(request, selection):
    categs_as_dict = dict()
    for categ in selection:
        categs_as_dict[categ.id] = categ.type
    return categs_as_dict

def paginate_items(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    items = [item.format() for item in selection]
    current_items = items[start:end]

    return current_items

def get_categories_for_api():
    selection = Category.query.order_by(Category.id).all()
    current_categs = from_categobjects_to_dict(request, selection)
    return current_categs

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def retrieve_categories():

        current_categs = get_categories_for_api()

        if len(current_categs) == 0:
            abort(404)

        return jsonify(
            {
                "categories": current_categs,
                "total_categories": len(Category.query.all()),
            }
        )

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        categ_name = request.args.get("category_name", '', type=str)
        selection = None
        categ_id = None
        print(categ_name)
        if not categ_name:
            selection = Question.query.order_by(Question.id.desc())
        else:
            current_category = Category.query.filter(Category.type == categ_name).first()
            categ_id = current_category.id
            selection = Question.query.filter(Question.category == str(categ_id)).order_by(Question.id.desc())

        return base_retrieve_questions(selection, categ_id=categ_id)

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "deleted": question_id,
                }
            )

        except:
            abort(422)
    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )

                return base_retrieve_questions(selection, with_categ=False)
            else:
                question = Question(question=new_question, answer=new_answer,
                                    category=new_category, difficulty=new_difficulty)
                question.insert()


                # selection = Question.query.order_by(Question.id).all()
                # current_questions = paginate_items(request, selection)

                # return jsonify(
                #     {
                #         "success": True,
                #         "created": question.id,
                #         "questions": current_questions,
                #         "total_questions": len(Question.query.all()),
                #     }
                # )
                return jsonify({})

        except:
            abort(422)
    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    
    Please see create_question endpoint
    """

    """
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:categ_id>/questions")
    def get_questions_by_category(categ_id):
        selection = Question.query.filter(Question.category == str(categ_id))
        return base_retrieve_questions(selection, categ_id=categ_id, with_categ=False)

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def navigate_quizz_questions():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)
        # print(quiz_category)
        # print(previous_questions)

        try:
            all_questions = list()
            next_question = None
            current_category = None

            if quiz_category:
                current_category = Category.query.filter(Category.id == int(quiz_category.get('id',None))).one_or_none()

            if not current_category and (not quiz_category or int(quiz_category.get('id',None)) == 0):
                all_questions = [quest.id for quest in Question.query.all()]
                # print('all')
            elif current_category:
                # print('filter')
                all_questions = [quest.id for quest in Question.query.filter(Question.category == str(current_category.id))]
            # print(all_questions)
            # print(current_category.type)
            # print(Question.query.filter(Question.category == 'Entertainment').all())
            if not previous_questions:
                previous_questions = list()

            if len(previous_questions) >= len(all_questions) and current_category:
                return jsonify({})

            question_id = random.choice(all_questions)

            while question_id in previous_questions and len(previous_questions) < len(all_questions):
                question_id = random.choice(all_questions)

            
            if not current_category:
                next_question = Question.query.filter(Question.id == question_id).one_or_none()
            else:
                next_question = Question.query.filter(Question.id == question_id,
                                                      Question.category == str(current_category.id)).one_or_none()
            if not next_question:
                abort(404)

            return jsonify(
                {
                    "question": next_question.format()
                }
            )

        except:
            abort(422)

    """
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Internal server error"}), 500,
        )

    return app

