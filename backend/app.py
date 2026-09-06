from flask import Flask, request, jsonify
from flask_cors import CORS


# for  Deep Learning  RNN Model 
import tensorflow as tf
import numpy as np
import pickle
import json


# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)
CORS(app)


# -----------------------------
# Load Trained RNN Model
# -----------------------------
model = tf.keras.models.load_model("model.keras")


# -----------------------------
# Load Tokenizer
# -----------------------------
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)


# -----------------------------
# Load Config
# -----------------------------
with open("config.json", "r") as f:
    config = json.load(f)

max_sequence_len = config["max_sequence_len"]


# -----------------------------
# Reverse Word Index
# -----------------------------
reverse_word_index = {
    value: key
    for key, value in tokenizer.word_index.items()
}


# -----------------------------
# Predict Next Word
# -----------------------------
def predict_next_word(seed_text):

    token_list = tokenizer.texts_to_sequences([seed_text])[0]

    token_list = tf.keras.preprocessing.sequence.pad_sequences(
        [token_list],
        maxlen=max_sequence_len - 1,
        padding="pre"
    )

    prediction = model.predict(token_list, verbose=0)

    predicted_id = np.argmax(prediction, axis=-1)[0]

    predicted_word = reverse_word_index.get(
        predicted_id,
        ""
    )

    return predicted_word


# -----------------------------
# API Route
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    text = data.get("text", "").strip()

    if not text:
        return jsonify({
            "error": "Please enter a sentence"
        }), 400

    next_word = predict_next_word(text)

    complete_sentence = text + " " + next_word

    return jsonify({
        "input": text,
        "next_word": next_word,
        "sentence": complete_sentence
    })


# -----------------------------
# Home Route
# -----------------------------
@app.route("/")
def home():
    return "RNN Next Word Prediction API is running!"


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)



   