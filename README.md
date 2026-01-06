**AI Blog Generator using YouTube Video Link**




<p align="center">
  <img src="Ai logo.png" alt="AI logo" width="200">
</p>




📖 Introduction
The **AI Blog Generator** is a web-based application designed to streamline the content creation process by leveraging Artificial Intelligence. It addresses the challenge of manually converting video content into text by automating the transformation of YouTube videos into structured, professional blog posts.

Built using the **Django** framework, the system integrates **AssemblyAI** for accurate speech-to-text transcription and **OpenRouter (LLM)** for natural language generation. It allows users to input a YouTube link, automatically downloads the audio, transcribes it, and generates a formatted blog article.

## ✨ Key Features
* **Automated Content Creation:** Converts YouTube video URLs into human-readable blog posts using Large Language Models.
* **User Management:** Secure Sign Up, Login, Password Recovery, and Profile Management.
* **Content Dashboard:** A personal dashboard to View, Edit, and Manage generated blogs.
* **Soft Delete System:** Includes a "Recycle Bin" to restore accidentally deleted blogs.
* **Multilingual Support:** Real-time translation of blog content into **Hindi** and **Marathi**.
* **Accessibility:** Built-in **Text-to-Speech (TTS)** functionality to listen to generated blogs.
* **Export & Sharing:**
    * Download blogs as formatted **PDF** documents.
    * Generate **QR Codes** for mobile access.
    * Direct **WhatsApp** sharing links.

## 🛠️ Tech Stack
The project uses the following technologies and libraries:

* **Backend:** Python 3.10+, Django 4.1.7
* **Frontend:** HTML5, CSS3, Tailwind CSS
* **Database:** SQLite (Development) / MySQL
* **AI & APIs:**
    * `yt-dlp`: For extracting audio from YouTube videos.
    * `AssemblyAI API`: For Speech-to-Text transcription.
    * `OpenRouter API`: For LLM-based text generation.
* **Utilities:**
    * `xhtml2pdf`: For PDF generation.
    * `qrcode`: For QR code generation.
    * `googletrans` / `deep-translator`: For language translation.

## 📂 Project Structure
Based on the project report, the directory structure is as follows :

```text
AI-BLOG-ARTICLE-GENERATOR-MAIN/
│
├── ai_blog_app/            # Main Project Configuration
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── blog_generator/         # Main App Logic
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py           # Database Schema (BlogPost, User)
│   ├── urls.py
│   ├── views.py            # Business Logic & API Integration
│   └── ...
│
├── media/                  # Stored assets (QR codes, PDFs)
├── db.sqlite3              # Database file
├── manage.py               # Django command-line utility
└── requirements.txt        # Project dependencies


⚙️ Installation & Setup
Prerequisites
Python 3.10 or higher 

Git

API Keys for AssemblyAI and OpenRouter

Steps
Clone the Repository

Bash

git clone [https://github.com/yourusername/ai-blog-generator.git](https://github.com/yourusername/ai-blog-generator.git)
cd ai-blog-generator
Create a Virtual Environment

Bash

python -m venv venv
# Activate on Windows
venv\Scripts\activate
# Activate on macOS/Linux
source venv/bin/activate
Install Dependencies

Bash

pip install -r requirements.txt

(Note: Key dependencies include django, yt-dlp, assemblyai, openai, xhtml2pdf, qrcode, googletrans).

Configure API Keys

Set up your API keys in settings.py or a .env file (recommended for security).

Run Database Migrations

Bash

python manage.py makemigrations
python manage.py migrate
Run the Development Server

Bash

python manage.py runserver
Access the Application Open your browser and navigate to http://127.0.0.1:8000/.

🚀 Usage Guide

Sign Up/Login: Create an account to access the dashboard.


Generate Blog: Paste a YouTube URL into the input box on the Home page and click "Generate Blog".


Wait for Processing: The system will download audio, transcribe, and generate text (approx. 30-60 seconds).

Interact: Once generated, you can:

Edit the content.

Listen via the Play Audio button.

Translate to Hindi or Marathi.


Export as PDF or share via QR/WhatsApp .

⚠️ Limitations

Video Length: Optimized for short to medium videos (under 20 minutes) to avoid timeouts.


Language: Input videos must be primarily in English for accurate transcription.


Input Method: Currently only supports YouTube URLs (no local file uploads).

🔮 Future Scope
Support for direct audio/video file uploads (.mp4, .mp3).

Tone customization (Professional, Casual, Funny).

Automated SEO keyword suggestions.

Automatic thumbnail generation using Image AI (e.g., DALL-E).

👨‍💻 Author
Vikash Ramdarash Chaurasiya

Course: Master of Computer Application (MCA)

Institute: TIMSCDR, University of Mumbai

Year: 2025-26


This project was developed as an In-Semester Capstone Project.
