from flask import Flask, g, redirect
from dal.db import get_db_connection
from routes.api_routes import api_bp
from routes.ui_routes import ui_bp

import i_am_a_fake_module_that_will_crash_the_app

app = Flask(__name__)
app.secret_key = 'corpseat-secret-key-2026'
app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)

@app.route('/')
def index():
    return redirect('/ui/offices')

@app.before_request
def before_request():
    g.db = get_db_connection()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
