from flask import Flask, render_template, request
from helpers.prompt_builder import build_battle_prompt
from helpers.local_infer import generate_image
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

    # Build prompt
    prompt = build_battle_prompt(your_name, your_traits, friend_name, friend_traits)

    # Call Hugging Face API
    image_data = generate_image(prompt)

    if image_data:
        # Save image
        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join("static", "images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(image_data)

        image_url = f"/static/images/{filename}"
        return render_template("results.html", prompt=prompt, image_url=image_url)
    else:
        # API failed — show error to user
        return render_template("results.html", prompt=prompt, image_url=None, error="Failed to generate image. Please try again.")

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
