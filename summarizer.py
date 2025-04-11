from flask import Flask, render_template, request, jsonify
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from string import punctuation
from heapq import nlargest
import os
from dotenv import load_dotenv
from openai import OpenAI

# Download necessary NLTK data (uncomment these if running for the first time)
# nltk.download('punkt')
# nltk.download('stopwords')

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env

# Initialize OpenAI client for advanced summarization
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_summarize_text(text, num_sentences=3):
    """
    Extractive summarization using NLTK.
    
    Args:
        text (str): The text to summarize
        num_sentences (int): Number of sentences to include in the summary
        
    Returns:
        str: The summarized text
    """
    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    
    # If text is too short, return the original text
    if len(sentences) <= num_sentences:
        return text
    
    # Preprocess the text
    stop_words = set(stopwords.words('english') + list(punctuation))
    words = word_tokenize(text.lower())
    
    # Remove stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    # Calculate word frequencies
    word_frequencies = FreqDist(filtered_words)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word]
                else:
                    sentence_scores[i] += word_frequencies[word]
    
    # Get the top N sentences with highest scores
    summary_sentences_indices = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary_sentences_indices.sort()  # Sort to maintain original order
    
    # Construct the summary
    summary = ' '.join([sentences[i] for i in summary_sentences_indices])
    
    return summary

def ai_summarize_text(text, max_tokens=150):
    """
    AI-powered summarization using OpenAI API.
    
    Args:
        text (str): The text to summarize
        max_tokens (int): Maximum tokens for the summary
        
    Returns:
        str: The AI-generated summary
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                {"role": "user", "content": f"Please summarize the following text in about {max_tokens} tokens:\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error with AI summarization: {str(e)}")
        # Fall back to extractive summarization if AI fails
        return extract_summarize_text(text)

@app.route('/')
def home():
    return render_template('summarizer.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    API endpoint to summarize text.
    """
    try:
        data = request.json
        text = data.get('text', '')
        method = data.get('method', 'extractive')  # 'extractive' or 'ai'
        sentences = int(data.get('sentences', 3))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        if method == 'ai':
            summary = ai_summarize_text(text)
        else:
            summary = extract_summarize_text(text, sentences)
            
        return jsonify({
            'original_text': text,
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary),
            'reduction_percentage': round((1 - len(summary) / len(text)) * 100, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize_file', methods=['POST'])
def summarize_file():
    """
    API endpoint to summarize a text file.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and (file.filename.endswith('.txt') or file.filename.endswith('.pdf')):
            # Read the file content
            if file.filename.endswith('.txt'):
                text = file.read().decode('utf-8')
            else:
                # For PDF files, you would need to add PyPDF2 or a similar library
                return jsonify({'error': 'PDF parsing not implemented yet'}), 501
            
            method = request.form.get('method', 'extractive')
            sentences = int(request.form.get('sentences', 3))
            
            if method == 'ai':
                summary = ai_summarize_text(text)
            else:
                summary = extract_summarize_text(text, sentences)
                
            return jsonify({
                'filename': file.filename,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'reduction_percentage': round((1 - len(summary) / len(text)) * 100, 2)
            })
        else:
            return jsonify({'error': 'Invalid file type. Please upload a TXT file'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize_url', methods=['POST'])
def summarize_url():
    """
    API endpoint to summarize content from a URL.
    """
    try:
        data = request.json
        url = data.get('url', '')
        method = data.get('method', 'extractive')
        sentences = int(data.get('sentences', 3))
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
            
        # Here you would typically use requests or similar to fetch the URL content
        # For now, we'll return an error
        return jsonify({'error': 'URL fetching not implemented yet'}), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
