from flask import Flask, request
from job_tasks import word_length_blob, celery_app
from celery.result import AsyncResult
from celery.task.control import inspect
import json

app = Flask(__name__)

#Error Handler
@app.errorhandler(404)
def not_found(e):
  return "Please check the URL and input correctly. If working on checking status, please give taskID.", 404

# Count endpoint for queueing the task.
@app.route('/count', methods=["POST"])
def count():
    try: 
        data = request.get_json()
        if 'text' in data:
            text = data["text"]
            result = word_length_blob.delay(text)
            return json.dumps({"id": result.id}), 200
        else:
            return json.dumps({"Invalid Input"}), 204 
    except Exception as e:
        if 'text' in str(e):
            return str(e) + " attribute is not given in the input. Try again. Give json input as {'text': '<input>'}.", 400
        elif 'JSON' in str(e):
            return "JSON object not given properly. Give json input as {'text': '<input>'}.", 400
        elif 'bad' in str(e).lower():
            return "Input Error. Give json input as {'text': '<input>'} if not given already", 400

# Code for checking ids in the task queue.
def key_in_list(k, l):
    return bool([True for i in l if k in i.values()])
def check_task(task_id):
    task_value_dict = inspect().active().values()
    for task_list in task_value_dict:
        if key_in_list(task_id, task_list):
             return True
    return False

#Checking the status of an id.
@app.route('/status/<string:id>', methods = ['GET'])
def status(id):
    if id is None:
        return "Invalid Url input. Please give some task ID." , 400
    try:
        res = AsyncResult(id, app=celery_app)
        if res.status == "SUCCESS":
            return json.dumps({"count": res.get(), "Status": res.status}), 200
        elif res.status == "FAILED":
            return json.dumps({"Status": "Task has failed. Try Again.", "Status": res.status}), 400
        elif (res.status == "PENDING" and (check_task(id)==True)):
            return json.dumps({"Error": "The job is in process. Try again after sometime.", "Status": res.status}), 400
        elif (res.status == "PENDING" and (check_task(id)==False)):
            return json.dumps({"Error": "The job id is invalid. Please check the id input."}), 404
        return json.dumps({"Something went wrong. Check the input and try again"}), 400
    except Exception as e:
            return str(e), 400
