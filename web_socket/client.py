from bottle import route, run, template

@route('/')
def home():
    return template("index.html")

run(host='0.0.0.0', port=8000, debug=True)