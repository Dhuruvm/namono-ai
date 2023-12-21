from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import re
import openai
from flask import url_for
app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = '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'

# Placeholder for preprocessed text
preprocessed_text = ''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')
# Route to handle the file upload
@app.route('/upload', methods=['POST'])
def upload():
    global preprocessed_text  # Access the global variable
    try:
        pdf_file = request.files['pdf_file']
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Save the PDF file
            pdf_path = f'pdf-data/{pdf_file.filename}'
            pdf_file.save(pdf_path)

            # Analyze the PDF content (replace this with your analysis logic)
            pdf_text = extract_text_from_pdf(pdf_path)
            preprocessed_text = preprocess_text(pdf_text)

            # Return success response
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid file format. Please upload a PDF file.'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

# Function to preprocess text data
def preprocess_text(text):
    # Remove non-alphanumeric characters and extra whitespaces
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# Route to handle user questions and interact with OpenAI GPT-3
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        user_question = request.form['user_question']
        answer = ask_openai(user_question, str(preprocessed_text))
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)})

# Function to interact with OpenAI GPT-3
def ask_openai(question, context):
    # Truncate context to fit within the model's limit
    max_context_length = 4097
    context = context[-max_context_length:]

    prompt = f'Context: {context}\nQuestion: {question}'
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=prompt,
        temperature=0.7,
        max_tokens=250,
        n=1,
    )
    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run(debug=True)
