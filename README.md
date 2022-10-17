# The Trivia app of Udacity

This project is a Trivia app initially developped by Udacity. As a part of the Fullstack Nanodegree, it serves as a practice project for lessons from Course 2 (API Development and Documentation). By completing this project, the goal was to learn and apply our skills structuring and implementing well formatted API endpoints that leverage knowledge of HTTP and API development best practices. In particular we had mission to develop the api part of this app (in the backend), test it and integrate it with the frontend. At the end, user of this app should be able to:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

All backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/). 

## Initial instructions

You can see here intial [instructions](INSTRUCTIONS.md) from udacity. 

## Getting Started

### Pre-requisites and Local Development 
Developers using this project should already have Python3, pip and node installed on their local machines.

#### Backend

From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file. 

To run the application run the following commands: 
```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration. 

#### Frontend

From the frontend folder, run the following commands to start the client: 
```
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on localhost:3000. 

### Tests
In order to run tests navigate to the backend folder and run the following commands: 

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

The first time you run the tests, omit the dropdb command. 

All tests are kept in that file and should be maintained as updates are made to app functionality. 

## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 
- 405: Method not allowed 
- 500: Internal server error

### Endpoints 

#### GET '/categories'
- General:

    - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
    - Request Arguments: None
    - Returns: An object with a single key, categories, that contains an object of id: category_string key:value pairs.

- Sample: `curl http://127.0.0.1:5000/categories`

``` 
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

#### GET '/questions?page=${integer}'
- General:
    
    - Fetches a paginated set of questions, a total number of questions, all categories and current category string.
    - Request Arguments: page - integer
    - Returns: An object with 10 paginated questions, total questions, object including all categories, and current category string
 
- `curl http://127.0.0.1:5000/questions?page=1`
```
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 2
    }
  ],
  "totalQuestions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": "History"
}
```
#### GET '/categories/${id}/questions'
- General:
    
    - Fetches questions for a cateogry specified by id request argument
    - Request Arguments: id - integer
    - Returns: An object with questions for the specified category, total questions, and current category string
 
- `curl http://127.0.0.1:5000/categories/3/questions`

```
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 4
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "History"
}

```

#### DELETE '/questions/${id}'
- General:
    
    - Deletes a specified question using the id of the question
    - Request Arguments: id - integer
    - Returns: Does not need to return anything besides the appropriate HTTP status code. Optionally can return the id of the question. If you are able to modify the frontend, you can have it remove the question using the id instead of refetching the questions.
 
- `curl -X DELETE http://127.0.0.1:5000/questions/9`
```
{
  "deleted_id": 9,
}
```

#### POST '/quizzes'
- General:
    
    - Sends a post request in order to get the next question
    - Request Body: An object containy the previous question list and the current quizz category
    - Returns: a single new question object or an empty object

- `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [1, 4, 20, 15], "quiz_category": "current category"}'`
```
{
  "question": {
    "id": 1,
    "question": "This is a question",
    "answer": "This is an answer",
    "difficulty": 5,
    "category": 4
  }
}
or
{}
```

#### POST '/questions'
- General:
    
    - Sends a post request in order to add a new question
    - Request Body: An object containy the question text, question answer, question category and question difficulty
    - Returns: Does not return any new data (precisely return an empty object)

- `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question": "Heres a new question string","answer": "Heres a new answer string","difficulty": 1,"category": 3}'`
```
{}
```

#### POST '/questions'
- General:
    
    - Sends a post request in order to search for a specific question by search term
    - Request Body: An object containy the search term
    - Returns: Returns: any array of questions, a number of totalQuestions that met the search term and the current category string

- `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm": "title"}'`
```
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 5
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "Entertainment"
}
```


## Deployment N/A

## Authors
Udacity and Kengne Mabou 

## Acknowledgements 
The awesome team at Udacity ! 


