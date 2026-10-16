# Snap and Study 📸📚

**Snap and Study** is a Python-based learning assistant built with Streamlit and Google's Gemini AI. The project aims to make studying easier by bringing AI-powered learning support into a simple web application.

## ✨ Features

- AI-powered study assistance using the Gemini API
- Interactive web interface built with Streamlit
- Reusable prompt logic for study-related tasks
- Email-related functionality through a separate Python module

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Git and GitHub

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Abhi-cybe-sys/Snap-and-Study.git
cd Snap-and-Study
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create `.streamlit/secrets.toml` and add your Gemini API key:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

Replace the placeholder with your own key. **Never upload this file or share your API key publicly.**

### 5. Run the application

```powershell
python -m streamlit run app.py
```

## 🔐 Security

API keys and other credentials should be stored securely and must not be committed to the public repository.

## 👨‍💻 Author

**Veerabhi Vardhan**

GitHub: [Abhi-cybe-sys](https://github.com/Abhi-cybe-sys)

## 📄 License

No license has been specified yet.