# Text Summarizer

A Flask-based application that provides text summarization functionality using both extractive and AI-powered methods.

## Features

- **Extractive Summarization**: Uses NLTK to identify and extract the most important sentences from a text
- **AI-Powered Summarization**: Leverages OpenAI's GPT models for more coherent, abstractive summaries
- **Multiple Input Methods**: Supports summarizing plain text, text files, and URLs (URL feature in development)
- **Customizable**: Adjust the length and type of summary based on your needs

## Technical Details

The application uses:
- Flask for the web framework
- NLTK for natural language processing and extractive summarization
- OpenAI API for AI-powered summarization
- Frequency distribution and sentence scoring algorithms for extractive summarization

## Getting Started

1. Install the required dependencies:
   ```
   pip install flask nltk python-dotenv openai
   ```

2. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```
   python summarizer.py
   ```

4. Access the application at `http://localhost:5000`

## API Endpoints

- `/summarize` - POST endpoint for summarizing text
- `/summarize_file` - POST endpoint for summarizing text files
- `/summarize_url` - POST endpoint for summarizing web content (in development)
