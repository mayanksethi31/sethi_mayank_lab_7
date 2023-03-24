import os
from celery import Celery
import time

broker_url = os.environ.get("CELERY_BROKER_URL"),
res_backend = os.environ.get("CELERY_RESULT_BACKEND")

celery_app = Celery(name='job_tasks', broker=broker_url, result_backend=res_backend)

@celery_app.task
def word_length_blob(text):
    try:
        word_length = len(text.split())
        time.sleep(word_length)
        return word_length
    except:
        return 0