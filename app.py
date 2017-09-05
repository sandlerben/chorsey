from flask import Flask, request

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK ;)'

@app.route('/messages_callback')
def messages_callback():
    content = request.get_json()
    return 'OK ;)'

if __name__ == '__main__':
    app.run(debug=True)
