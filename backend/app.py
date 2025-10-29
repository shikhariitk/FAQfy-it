from flask import Flask, jsonify, request
import pandas as pd
import os
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Flask app
app = Flask(__name__)
from flask_cors import CORS
CORS(app, origins=["http://localhost:3001"])

# Directory containing CSV files
CSV_DIR = os.path.join(os.path.dirname(__file__), 'csv_files')

# App data storage
app_data = {}

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Preprocessing function
stop_words = set(stopwords.words('english'))
# def preprocess(text, use_stopwords=True):
#     lemmatizer = WordNetLemmatizer()
#     stemmer = PorterStemmer()
#     text = re.sub(r'[^\w\s]', '', text)  # Remove non-alphanumeric characters
#     tokens = nltk.word_tokenize(text.lower())
#     if use_stopwords:
#         tokens = [token for token in tokens if token not in stop_words]
#     lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
#     stemmed_tokens = [stemmer.stem(token) for token in lemmatized_tokens]
#     return ' '.join(stemmed_tokens)
def preprocess(text, use_stopwords=True):
    if not text or not isinstance(text, str):  # Check if the text is empty or not a string
        return ""  # Return empty string if the text is invalid
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    text = re.sub(r'[^\w\s]', '', text)  # Remove non-alphanumeric characters
    tokens = nltk.word_tokenize(text.lower())
    if use_stopwords:
        tokens = [token for token in tokens if token not in stop_words]
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    stemmed_tokens = [stemmer.stem(token) for token in lemmatized_tokens]
    return ' '.join(stemmed_tokens)



# Load CSV files
# def load_data():
#     for csv_file in os.listdir(CSV_DIR):
#         if csv_file.endswith('.csv'):
#             app_name = os.path.splitext(csv_file)[0]
#             df = pd.read_csv(os.path.join(CSV_DIR, csv_file))
#             if 'question' in df.columns and 'answer' in df.columns:
#                 app_data[app_name] = df
#             else:
#                 print(f"Warning: {csv_file} is missing required columns.")

def load_data():
    print(f"Loading data from {CSV_DIR}")
    for csv_file in os.listdir(CSV_DIR):
        if csv_file.endswith('.csv'):
            app_name = os.path.splitext(csv_file)[0]
            print(f"Loading CSV file: {csv_file}")  # Debug print
            df = pd.read_csv(os.path.join(CSV_DIR, csv_file))
            if 'question' in df.columns and 'answer' in df.columns:
                app_data[app_name] = df
            else:
                print(f"Warning: {csv_file} is missing required columns.")


# Create TF-IDF vectorizer
def create_vectorizer(questions_list):
    vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize)
    X = vectorizer.fit_transform([preprocess(q) for q in questions_list])
    return vectorizer, X

# Get response
# def get_response(text, questions_list, answers_list, vectorizer, X):
#     text = TextBlob(text).correct()
#     processed_text = preprocess(text)
#     vectorized_text = vectorizer.transform([processed_text])
#     similarities = cosine_similarity(vectorized_text, X).flatten()
#     top_idx = similarities.argsort()[-1]

#     if similarities[top_idx] >= 0.9:
#         return {
#             "question": questions_list[top_idx],
#             "answer": answers_list[top_idx],
#             "similarity": similarities[top_idx],
#         }
#     return {"question": "No match found.", "answer": "", "similarity": 0}
def get_response(text, questions_list, answers_list, vectorizer, X):
    text = str(TextBlob(text).correct())  # Ensure that the corrected text is a string
    processed_text = preprocess(text)
    vectorized_text = vectorizer.transform([processed_text])
    similarities = cosine_similarity(vectorized_text, X).flatten()
    top_idx = similarities.argsort()[-1]

    if similarities[top_idx] >= 0.9:
        return {
            "question": questions_list[top_idx],
            "answer": answers_list[top_idx],
            "similarity": similarities[top_idx],
        }
    return {"question": "No match found.", "answer": "", "similarity": 0}



# Flask route
@app.route('/<app_name>', methods=['GET'])
def get_app_data(app_name):
    print(f"Received request for app: {app_name}")  # Debug print
    if app_name in app_data:
        df = app_data[app_name]
        question = request.args.get('question')
        print(f"Received question: {question}")  # Debug print
        if question:
            questions_list = df['question'].tolist()
            answers_list = df['answer'].tolist()
            vectorizer, X = create_vectorizer(questions_list)
            response = get_response(question, questions_list, answers_list, vectorizer, X)
            return jsonify(response)
        return jsonify({"error": "Question not provided."}), 400
    return jsonify({"error": "App not found."}), 404

if __name__ == '__main__':
    load_data()  # Ensure data is loaded before running the app
    app.run(debug=True,port=5000)
