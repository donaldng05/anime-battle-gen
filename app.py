from flask import Flask, render_template, request
from helpers.prompt_builder import build_battle_prompt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    your_name = request.form['your_name']
    your_traits = f"{request.form['your_hair']}, {request.form['your_vibe']}"
    friend_name = request.form['friend_name']
    friend_traits = f"{request.form['friend_hair']}, {request.form['friend_vibe']}"

    prompt = build_battle_prompt(your_name, your_traits, friend_name, friend_traits)

    return render_template('results.html', prompt=prompt)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
