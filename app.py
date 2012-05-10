from flask import Flask, redirect, render_template, jsonify
import os

app = Flask(__name__)

# Redirecting to static frontend

@app.route('/')
def index():
    return render_template('index.html');

# Populating frontend conf file with environment variables

@app.route('/config/config.json')
def conf():
    return jsonify(GOOGLE_FUSION_ID=os.environ['GOOGLE_FUSION_ID']);
    
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)