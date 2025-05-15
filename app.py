from flask import Flask, render_template, request
from helpers.prompt_builder import build_battle_prompt
from helpers.hf_api import generate_image
import uuid
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

    # Build prompt from input
    prompt = build_battle_prompt(your_name, your_traits, friend_name, friend_traits)

    # Generate image from Hugging Face
    image_data = generate_image(prompt)

    # Save image to static folder
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join("static", "images", filename)
    with open(filepath, "wb") as f:
        f.write(image_data)

    # Pass image path to template
    image_url = f"/static/images/{filename}"

    return render_template("results.html", prompt=prompt, image_url=image_url)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
