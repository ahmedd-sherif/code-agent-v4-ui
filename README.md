# Code Agent V4 🤖 (UI Edition)

AI Agent ذكي باستخدام Google Agent Development Kit (ADK) يقدر يكتب كود، يسطب مكتبات، ويرفع على GitHub.

## Features

- 🖥️ **Streamlit UI** - واجهة رسومية سهلة الاستخدام
- 🧠 **Persistent Memory** - ذاكرة دائمة للمحادثات
- 🌐 **Web Search** - بحث ذكي باستخدام Tavily
- ✍️ **Code Writing** - يكتب كود من البرومبت اللي تديهوله
- 📋 **Planning** - يعمل خطة ويستنى موافقتك قبل التنفيذ
- 💻 **Terminal** - يسطب مكتبات ويشغل أوامر
- 📁 **File Management** - يقرأ ويكتب ويمسح ملفات
- 🐙 **GitHub** - يرفع الكود على GitHub

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Running the UI

```bash
python -m streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Configuration

Edit `.env` file and add API keys:
```
GOOGLE_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
TAVILY_API_KEY=tvly-...
```
