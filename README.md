# DataExtractionService_CrewAI

A powerful data extraction service built with CrewAI for web scraping, image text extraction, and file reading.

## 🚀 Features

- **Web Scraping**: Extract data from websites using CSS selectors
- **Structured Output**: Automatically formats scraped data into clean JSON
- **AI-Powered Analysis**: Ask questions about scraped data using GPT-4
- **Modular Design**: Built with FastAPI for high performance and scalability

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Node.js (for frontend)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/sap156/DataExtractionService_CrewAI.git
cd DataExtractionService_CrewAI
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## 🔧 Usage

### Starting the Server

```bash
uvicorn backend.main:app --reload
```

### API Endpoints

- **POST /scrape**
  - Scrapes specific elements using CSS selectors
  ```json
  {
    "url": "https://example.com",
    "selector": ".target-class"
  }
  ```

- **GET /scrape-all**
  - Scrapes all visible elements from a webpage
  ```
  /scrape-all?url=https://example.com
  ```

- **POST /ask**
  - Ask questions about scraped data
  ```json
  {
    "data": "<scraped_json_data>",
    "question": "What are the main topics?"
  }
  ```

## 🔒 Security

- Environment variables for sensitive data
- Git-ignored configuration files
- Push protection for secrets

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- CrewAI for the AI agent framework
- OpenAI for GPT integration
- FastAPI for the web framework
