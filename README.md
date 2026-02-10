# EchoBI - Self-Service Analytics Platform

EchoBI is a no-code self-service analytics platform that transforms raw data into actionable insights with intelligent classification, preprocessing, and visualization.

![EchoBI](https://img.shields.io/badge/Version-2.0-gold) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![React](https://img.shields.io/badge/React-18+-61dafb)

---

## ✨ Features

- **📤 Smart Upload** - Drag & drop CSV/Excel files
- **🏷️ Auto-Classification** - Automatically detects dataset type (Financial, Sales, Time-Series, Healthcare, Generic)
- **🔍 Column Analysis** - Semantic type detection, statistics, and quality scoring
- **⚙️ Domain-Specific Preprocessing** - Context-aware data cleaning with full audit trail
- **💡 Intelligent Insights** - Statistical analysis and AI-generated insights
- **📊 Smart Visualizations** - Auto-recommended charts based on data patterns
- **💬 Chat with Data** - Ask questions about your dataset in natural language

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- Git (optional)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EchoBI-4
```

### 2. Set Up Backend

```bash
# Navigate to backend folder
cd backend

# Create virtual environment (skip if echovenv already exists)
python3 -m venv echovenv

# Activate virtual environment
# On macOS/Linux:
source echovenv/bin/activate
# On Windows:
echovenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up AI Features - copy .env.example to .env and add your Gemini API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend API will start at **http://localhost:8000**

### 3. Set Up Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend folder
cd frontend/echo-bi

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start at **http://localhost:5173** or **http://localhost:5174**

### 4. Open in Browser

Navigate to **http://localhost:5173** (or the port shown in your terminal)

### 5. (Optional) Enable AI-Powered Chat

To enable GPT-powered chat responses:

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a `.env` file in the `backend/` folder:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Restart the backend server

Without the API key, the chat will use a rule-based fallback system.

---

## 📁 Project Structure

```
EchoBI-4/
├── backend/
│   ├── main.py              # FastAPI backend with all endpoints
│   ├── requirements.txt     # Python dependencies
│   └── echovenv/            # Python virtual environment
│
├── frontend/
│   └── echo-bi/
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── pages/       # Page components
│       │   ├── services/    # API service functions
│       │   └── App.jsx      # Main app component
│       ├── package.json     # Node dependencies
│       └── vite.config.js   # Vite configuration
│
└── README.md
```

---

## 📋 Workflow

1. **Upload** - Upload your CSV or Excel file
2. **Classification** - System auto-detects dataset type (confirm or override)
3. **Analysis** - View column profiles, data types, and quality scores
4. **Preprocessing** - Apply domain-specific cleaning operations
5. **Insights** - Explore statistical findings and patterns
6. **Dashboard** - View auto-generated visualizations
7. **Chat** - Ask questions about your data

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload a dataset file |
| POST | `/api/v1/analyze/{session_id}` | Analyze dataset and classify |
| POST | `/api/v1/confirm-classification` | Confirm or override classification |
| GET | `/api/v1/preprocessing/suggestions/{session_id}` | Get preprocessing suggestions |
| GET | `/api/v1/insights/{session_id}` | Get statistical insights |
| GET | `/api/v1/visualizations/recommendations/{session_id}` | Get chart recommendations |
| POST | `/api/v1/visualizations/generate` | Generate a specific chart |
| POST | `/api/v1/chat` | Chat with your dataset (AI-powered) |
| GET | `/api/v1/ai-summary/dataset/{session_id}` | Get AI-generated dataset summary |
| GET | `/api/v1/ai-summary/preprocessing/{session_id}` | Get AI-generated preprocessing summary |

API Documentation: **http://localhost:8000/docs** (Swagger UI)

---

## 🤖 AI Features (Powered by Gemini)

EchoBI uses Google's Gemini AI for intelligent features:

### AI Chat
- Ask questions about your dataset in natural language
- Get contextual answers based on your data

### AI Dataset Summary
- Generate executive summaries of your data
- Understand key characteristics and patterns automatically

### AI Preprocessing Summary
- Get plain-language explanations of all preprocessing steps
- Understand what transformations were applied and why

**To enable AI features:**
1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the backend folder
3. Add: `GEMINI_API_KEY=your_api_key_here`

---

## 🛠️ Development

### Running in Development Mode

**Backend (with auto-reload):**
```bash
cd backend
source echovenv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend (with hot reload):**
```bash
cd frontend/echo-bi
npm run dev
```

### Building for Production

**Frontend build:**
```bash
cd frontend/echo-bi
npm run build
```

---

## 🎨 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Plotly** - Interactive visualizations

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Plotly.js** - Chart rendering

---

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed: `python3 --version`
- Activate the virtual environment before running
- Check all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Ensure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### CORS errors
- Ensure backend is running on port 8000
- Check that frontend is running on port 5173 or 5174

### Upload fails
- Check file format (CSV or Excel only)
- Ensure file size is reasonable (< 50MB recommended)
- Check backend terminal for error messages

---

## 📊 Project Statistics

- **Test Pass Rate:** 83% (5/6 features operational)
- **Features Complete:** 100%
- **Frontend:** 21 components, 7 pages
- **Backend:** 10 endpoints
- **Total Files:** 70+

---

## 📄 License

This project is for educational and demonstration purposes.

---

**Made with ❤️ using Python & React**
