import os 
import uuid

import boto3
from boto3.dynamodb.conditions import Key


from flask import request, jsonify
from flask_lambda import FlaskLambda # flask and lambda wrapper

# extract environment variables
EXEC_ENV = os.environ['EXEC_ENV']
REGION = os.environ['REGION_NAME']
TABLE_NAME = os.environ['TABLE_NAME']

app = FlaskLambda(__name__)  #create an instance of the flask app with the name of the file

# check if testing is to be done locally
if EXEC_ENV == 'local':
    dynamodb = boto3.resource('dynamodb', endpoint_url = 'http://dynamodb:8000')
else:
    dynamodb = boto3.resource('dynamodb', region_name = REGION)


def db_table(table_name=TABLE_NAME):
    """This function returns the dynamodb table as an object"""

    return dynamodb.Table(table_name)

def parser_user_id(req):
    """parse and decode token to get user identification in 
        react front end app which is configured with AWS congito"""
    return req.headers['Authorization'].split()[1] # get the name out of the string array


def identity_check():
    """try and except block to check identity"""
    try:
         user_id = parser_user_id(request)
    except:
        return jsonify('Unauthorized'), 401
    return user_id

@app.route('/lists')
def fetch_lists():
    """This endpoint returns all the list present in  dynamodb to the front end app"""
    identity = identity_check()
    if type(identity) == tuple:
        return identity
    return jsonify(db_table().query(KeyConditionsExpression = Key('UserId').eq(identity))['Items'])

@app.route('/lists', methods=('POST',))
def create_list():
    """Generate list that is stored in dynamodb"""
    list_id = str(uuid.uuid4())
    identity = identity_check()
    if type(identity) == tuple: # the error output is deterministic, always a tuple
        return identity
    list_data = request.get_json()
    list_data.update(userId=identity, listId=list_id)
    tbl = db_table()
    tbl.put_item(Item=list_data)
    tbl_response = tbl.get_item(Key={'userId': identity, 'listId': list_id})
    return jsonify(tbl_response['Item']), 201

@app.route('/lists/<string: list_id>')
def fetch_list(list_id):
    """Fetch a particular list of individual"""
    identity = identity_check()
    if type(identity) == tuple: # the error output is deterministic, always a tuple
        return identity
    tbl_response = db_table().get_item(Key={'userId': identity, 'listId': list_id})
    return jsonify(tbl_response['Item'])


@app.route('/lists/<string: list_id>', methods=('PUT',))
def update_list(list_id):
    """This function modifies the existing dynamodb table data"""
    identity = identity_check()
    if type(identity) == tuple: # the error output is deterministic, always a tuple
        return identity
    list_data = {k: {'Value': v, 'Action': 'PUT'}
                 for k, v in request.get_json().items()}
    db_table().update_item(Key={'userId': identity, 'listId': list_id}, 
                                                                AttributeUpdates=list_data)
    return jsonify() # returns an empty json object


@app.route('/lists/<string:list_id>', methods=('DELETE',))
def delete_lists(list_id):
    """Delete a particular list_id or record"""
    identity= identity_check()
    if type(identity) == tuple: # the error output is deterministic, always a tuple
        return identity
    db_table().delete_item(Key={'userId': identity, 'list_id': list_id})
    return jsonify()

