from flask import Flask, render_template, request, url_for
from helpers.prompt_builder import build_battle_prompt
from helpers.local_infer import generate_and_save_image
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    your_name       = request.form['your_name']
    your_traits     = request.form['your_traits']
    friend_name     = request.form['friend_name']
    friend_traits   = request.form['friend_traits']
    background_fx   = request.form.get('background_effects')   # new
    style           = request.form.get('anime_style')

    prompt = build_battle_prompt(
        your_name, your_traits,
        friend_name, friend_traits,
        style=style,
        background_effects=background_fx
    )

    try:
        # style passed into generate_and_save_image → fallback to base if None
        output_path = generate_and_save_image(prompt, steps=20, style=style)
        filename  = os.path.basename(output_path)
        image_url = url_for('static', filename=f'images/{filename}')
        return render_template('results.html',
                               prompt=prompt,
                               image_url=image_url,
                               style=style)
    except Exception as e:
        return render_template('results.html',
                               prompt=prompt,
                               image_url=None,
                               error=str(e),
                               style=style)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
