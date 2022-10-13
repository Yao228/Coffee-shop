from crypt import methods
from curses import newpad
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Header",
                         "Content-Type, Authorization, true")
    response.headers.add("Access-Control-Allow-Methods",
                         "GET,POST,DELETE,OPTIONS,PUT, PATCH")
    return response


@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def drinks(payload):
    drinks = Drink.query.all()
    formated_drinks = [drink.short() for drink in drinks]
    if len(formated_drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': formated_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    drinks = Drink.query.all()
    formated_drinks = [drink.long() for drink in drinks]
    if len(formated_drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': formated_drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    try:
        body = request.get_json()
        new_title = json.dumps(body.get("title"))
        new_recipe = json.dumps(body.get("recipe"))

        try:
            drink = Drink(title=new_title, recipe=new_recipe)
            drink.insert()
        except:
            abort(422)

        return jsonify({
            'success': True,
            'drink': [drink.long()]
        })
    except:
        abort(403)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        formated_drink = [drink.long()]
        if drink is None:
            abort(404)

        if 'title' in body:
            title = json.dumps(body.get('title'))
            drink.title = title
            drink.update()

        if 'recipe' in body:
            recipe = json.dumps(body.get('recipe'))
            drink.recipe = recipe
            drink.update()

        return jsonify({
            'success': True,
            'updated': id,
            'drinks': formated_drink
        })
    except:
        abort(403)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        drinks = Drink.query.filter(Drink.id == id).one_or_none()
        if drinks is None:
            abort(404)

        drinks.delete()

        return jsonify({
            'success': True,
            'status_code': 200,
            'delete': id
        })
    except:
        abort(403)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        'success': False,
        'error': auth_error.status_code,
        'message': auth_error.error
    }), 401
