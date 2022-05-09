from flask import json

import pytest

from app import app
 




# def test_lambda_handler_write_file(apigw_event, mocker):
#     file_mock = mocker.patch.object(app, 'FILE')
#     file_mock.is_file.return_value = False

#     ret = app.lambda_handler(apigw_event, "")
#     data = json.loads(ret["body"])

#     assert ret["statusCode"] == 200
#     assert "file_contents" in ret["body"]
#     assert "created_file" in ret["body"]
#     assert data["file_contents"] == "Hello, EFS!\n"
#     assert data["created_file"] == True


def test_connnection():
    response = app.test_client().get('/lists')
    res = json.loads(response.data.decode('utf-8'))
    assert type(res) is dict
    assert response.status_code == 200
      


