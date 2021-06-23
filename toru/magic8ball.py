#!/usr/bin/env python3
import requests
import json
import urllib.parse


class Magic8Ball:
    def __init__(self):
        self.domain = 'https://8ball.delegator.com'

    # Given an str of a question, return an random answer
    def ask(self, question):
        question = urllib.parse.quote(question)
        response = requests.get(f'{self.domain}/magic/JSON/{question}')

        if response.status_code != 200:
            return 'Yeah, I don\'t know man'

        answer = json.loads(response.text)['magic']['answer']
        return answer
