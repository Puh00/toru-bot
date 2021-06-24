#!/usr/bin/env python3
import requests
import json
import urllib.parse


_8BALL_API_DOMAIN_ = 'https://8ball.delegator.com'

# Given an str of a question, return an random answer
def ask(question):
    question = urllib.parse.quote(question)
    response = requests.get(f'{_8BALL_API_DOMAIN_}/magic/JSON/{question}')

    if response.status_code != 200:
        return 'Yeah, I don\'t know man'

    answer = json.loads(response.text)['magic']['answer']
    return answer
