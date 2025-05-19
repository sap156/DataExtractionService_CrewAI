# DataExtractionService_CrewAI

A powerful data extraction service built with CrewAI for web scraping, image text extraction, and file reading.

## 🚀 Features

- **Web Scraping**: Extract data from websites using CSS selectors
- **Structured Output**: Automatically formats scraped data into clean JSON
- **AI-Powered Analysis**: Ask questions about scraped data using GPT-4
- **File Reading**: Extract text from uploaded files
- **Image Text Extraction**: Extract text from images using OCR
- **Modular Design**: Built with FastAPI for high performance and scalability

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Node.js (for frontend)

## 🛠️ Backend Overview

The backend is built using FastAPI and consists of the following components:

### **`main.py`**

The entry point for the backend application. It initializes the FastAPI app and registers the routes for various functionalities:

- **`/api/scrape`**: Handles web scraping requests.
- **`/api/scrape-all`**: Scrapes all visible elements from a webpage.
- **`/api/vision`**: Extracts text from uploaded images using OCR.
- **`/api/read-file`**: Reads and processes uploaded files.
- **`/api/selectors`**: Debugs and inspects CSS selectors for a given webpage.

### **`routes/scrape.py`**

Handles web scraping functionality:

- **`POST /api/scrape`**: Extracts specific elements from a webpage using CSS selectors.
- **`GET /api/scrape-all`**: Scrapes all visible elements from a webpage and formats the data into JSON using OpenAI.
- **Chunking Helper**: Splits large scraped content into smaller chunks for processing by OpenAI.

### **`routes/vision.py`**

Handles image text extraction:

- **`POST /api/vision`**: Uses the VisionTool to extract text from uploaded images and formats the result into structured JSON using OpenAI.
- Includes robust error handling and temporary file cleanup.

### **`routes/file_read.py`**

Handles file reading functionality:

- **`POST /api/read-file`**: Reads the contents of uploaded files (e.g., `.txt`, `.csv`, `.json`) and returns structured data.
- Uses the FileReadTool to process the files and manage tasks with CrewAI.

### **`routes/selector_debugger.py`**

Handles CSS selector debugging:

- **`GET /api/selectors`**: Inspects a webpage and returns sample CSS selectors along with a preview of their content.
- Useful for debugging and refining CSS selectors for web scraping.

## 🔧 Usage

### Starting the Backend Server

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DataExtractionService_CrewAI.git
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

4. Start the server:
```bash
uvicorn backend.main:app --reload
```

### API Endpoints

#### **POST /api/scrape**
Extracts specific elements from a webpage using CSS selectors.

**Request Body:**
```json
{
  "url": "https://example.com",
  "selector": ".target-class"
}
```

**Response:**
```json
{
  "result": ["Extracted content"]
}
```

#### **GET /api/scrape-all**
Scrapes all visible elements from a webpage.

**Query Parameters:**
- `url`: The URL of the webpage to scrape.

**Response:**
```json
{
  "result": [
    {
      "tag_name": ["Extracted content"]
    }
  ]
}
```

#### **POST /api/vision**
Extracts text from an uploaded image using OCR.

**Request:**
- Upload an image file.

**Response:**
```json
{
  "result": "Extracted text from image"
}
```

#### **POST /api/read-file**
Reads and processes uploaded files.

**Request:**
- Upload a file (e.g., `.txt`, `.csv`, `.json`).

**Response:**
```json
{
  "result": "File contents or structured data"
}
```

#### **GET /api/selectors**
Inspects and debugs CSS selectors for a given webpage.

**Query Parameters:**
- `url`: The URL of the webpage to inspect.

**Response:**
```json
{
  "selectors": [
    {
      "selector": "div.class-name",
      "preview": "Sample content"
    }
  ]
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
