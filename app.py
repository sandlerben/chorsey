import os

from flask import Flask, request

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK ;)'

@app.route('/messages_callback')
def messages_callback():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        if mode == 'subscribe' and verify_token == os.environ['facebook_secret']:
            return request.args.get('hub.challenge')
        else:
            return 'Failed challenge', 403
    content = request.get_json()
    print(content)
    return 'OK ;)'

if __name__ == '__main__':
    app.run(debug=True)
