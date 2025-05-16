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
    your_name = request.form['your_name']
    your_traits = request.form['your_traits']
    friend_name = request.form['friend_name']
    friend_traits = request.form['friend_traits']

    # Build the battle prompt
    prompt = build_battle_prompt(your_name, your_traits, friend_name, friend_traits)

    try:
        # Generate & save the image locally
        output_path = generate_and_save_image(prompt, steps=25)
        # Derive the URL for the client
        filename = os.path.basename(output_path)
        image_url = url_for('static', filename=f'images/{filename}')
        return render_template('results.html', prompt=prompt, image_url=image_url)

    except Exception as e:
        # Generation failed — show error to user
        error_msg = f"Failed to generate image: {str(e)}"
        return render_template('results.html',
                               prompt=prompt,
                               image_url=None,
                               error=error_msg)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
