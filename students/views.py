from django.http import HttpResponse, JsonResponse
from processor import *
import json

def index(req):
    return HttpResponse('<h3>Welcome to admin chatbot</h3>')

def chatbot(req):
    if req.method == 'POST':
        data = json.loads(req.body)
        response = chatbot_response(data.get('question'))
    return JsonResponse({"response": response});