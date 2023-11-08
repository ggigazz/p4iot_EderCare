# Find the Sinch phone number assigned to your app
# and your application key and secret
# at dashboard.sinch.com/voice/apps
import requests
from flask import Flask, request, jsonify, send_file, send_from_directory
from waitress import serve

key = "1c313da3-97a7-4a2e-bb1a-282b4336fc74"
secret = "qvPJpiFAdUW/G0O+u7OZsg=="
fromNumber = "+447520651976"
locale = "it-IT"
url = "https://calling.api.sinch.com/calling/v1/callouts"

app = Flask(__name__)


@app.route('/emergency_call', methods=['POST'])
def emergency_call():

    payload_json = request.json
    # For every number in 'to' list, make a call
    for number in payload_json['to']:
        payload = {
            "method": "ttsCallout",
            "ttsCallout": {
                "cli": fromNumber,
                "destination": {
                    "type": "number",
                    "endpoint": number
                },
                "locale": locale,
                "text": f"Buongiorno, questa e' una chiamata del servizio EderCare. Il dispositivo del paziente {payload_json['patient_name']} ha rilevato un allarme"
            }
        }

        headers = {"Content-Type": "application/json"}
        # Make the POST call request to Sinch API
        response = requests.post(
            url, json=payload, headers=headers, auth=(key, secret))
        '''
        data = response.json()
        print(data)
        '''
        print(f"Chiamata a {payload_json['patient_name']} effettuata")
    return {'result': True}


if __name__ == "__main__":
    serve(app, port=17368, host='0.0.0.0', url_scheme="https")
    # app.run(host='0.0.0.0', debug=True, port=17863)
