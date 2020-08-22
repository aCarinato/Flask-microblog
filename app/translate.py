import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language, dest_language):
    '''
    Function to translate text using the Microsoft Translator API
    '''
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured')

    # To authenticate with the service, it is needed to pass a key in a given HTTP header. This is passed in the request as a header argument
    auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
            # 'Ocp-Apim-Subscription-Region': 'westeurope'
            }
    # send an HTTP request with a GET method to the URL given as the first argument
    # the /v2/Ajax.svc/Translate is an endpoint from the translation service that returns translations as a JSON payload

    # base_url = 'https://api.cognitive.microsofttranslator.com'
    # path = '/translate?api-version=3.0'
    # params = '&to=' + language_output
    # constructed_url = base_url + path + params


    r = requests.get('https://api.cognitive.microsofttranslator.com'
                     '/Translate?text={}&from={}&to={}'.format(
                         text, source_language, dest_language),
                     headers=auth)
    # requests.get() returns a response object which contains all the details provided by the service


    if r.status_code != 200:
        return _('Error: the translation service failed')
    print('so far no errors')
    # the return value of request is a JSON encoded string with string that contains all the details provided by the service. It has to be decoded.
    return json.loads(r.content.decode('utf-8-sig'))
