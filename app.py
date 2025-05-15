from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    your_name = request.form['your_name']
    your_traits = request.form['your_traits']
    friend_name = request.form['friend_name']
    friend_traits = request.form['friend_traits']

    prompt = f"An anime-style battle scene between {your_name}, who has {your_traits}, and {friend_name}, who has {friend_traits}. Glowing energy, destroyed city background, intense action, cinematic lighting."

    return render_template('results.html', prompt=prompt)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
