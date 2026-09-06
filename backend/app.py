from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

import tensorflow as tf
import numpy as np
import pickle
import json


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# Load trained RNN model
# This happens ONCE when Flask starts.
# --------------------------------------------------

model = tf.keras.models.load_model(
    BASE_DIR / "model.keras"
)


# --------------------------------------------------
# Load tokenizer
# --------------------------------------------------

with open(BASE_DIR / "tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)


# --------------------------------------------------
# Load configuration
# --------------------------------------------------

with open(BASE_DIR / "config.json", "r") as f:
    config = json.load(f)

max_sequence_len = config["max_sequence_len"]


# --------------------------------------------------
# Reverse word index
# number -> word
# --------------------------------------------------

reverse_word_index = {
    value: key
    for key, value in tokenizer.word_index.items()
}


# --------------------------------------------------
# Model inference function
# --------------------------------------------------

def predict_next_word(seed_text):

    # 1. Text -> token IDs
    token_list = tokenizer.texts_to_sequences(
        [seed_text]
    )[0]


    # 2. Pad sequence to model's expected length
    token_list = tf.keras.preprocessing.sequence.pad_sequences(
        [token_list],
        maxlen=max_sequence_len - 1,
        padding="pre"
    )


    # 3. Run the already-loaded trained model
    prediction = model.predict(
        token_list,
        verbose=0
    )


    # 4. Get ID of the word with highest probability
    predicted_id = int(
        np.argmax(prediction, axis=-1)[0]
    )


    # 5. Convert predicted ID -> actual word
    predicted_word = reverse_word_index.get(
        predicted_id,
        ""
    )


    return predicted_word


# --------------------------------------------------
# API endpoint
# JavaScript sends:
# {
#     "text": "I love"
# }
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()


    if not text:

        return jsonify({
            "error": "Please enter a sentence."
        }), 400


    try:

        next_word = predict_next_word(text)

        complete_sentence = (
            text + " " + next_word
        ).strip()


        # Send JSON response back to JavaScript
        return jsonify({
            "input": text,
            "next_word": next_word,
            "sentence": complete_sentence
        })


    except Exception as error:

        print("Prediction error:", error)

        return jsonify({
            "error": "Prediction failed. Check the model, tokenizer and config files."
        }), 500


# --------------------------------------------------
# Home route
# --------------------------------------------------

@app.route("/")
def home():

    return "RNN Next Word Prediction API is running!"


# --------------------------------------------------
# Start Flask server
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
