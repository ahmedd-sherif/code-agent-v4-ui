# Code Agent 🤖

AI Agent ذكي باستخدام Google Agent Development Kit (ADK) يقدر يكتب كود، يسطب مكتبات، ويرفع على GitHub.

## Features

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

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `.env` file and add your API keys:
```
GOOGLE_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

Run the development web interface:
```bash
adk web
```

Then open http://localhost:8000 in your browser and select `code_agent` from the dropdown.

## Example Prompts

- "اعمل لي ملف Python يطبع Hello World"
- "سطب مكتبة requests"
- "اعمل لي مشروع Flask بسيط"
- "ارفع المشروع على GitHub باسم my-project"

## License

MIT
