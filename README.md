# 🤖 Araf's Assistant — Multilingual AI Chatbot (Django + DRF)

A complete, production-ready, full-stack ChatGPT-style AI assistant built with **Django**, **Django REST Framework (DRF)**, **SQLite/PostgreSQL**, **HTML5/CSS3/Vanilla JS**, **SSE Streaming**, and **DuckDuckGo Web Search Grounding**.

---

## 🌟 Key Features

* 🇧🇩 **Multilingual & Banglish Support**: Speaks and understands বাংলা, English, Banglish (*"vai Django te authentication kivabe banabo?"*), and code-switching.
* ⚡ **Real-Time Token Streaming**: ChatGPT-style character-by-character typing animation using Server-Sent Events (SSE).
* 🌐 **Live Web Search Grounding**: DuckDuckGo search integration retrieves up-to-date facts and displays clickable source citations.
* 🧠 **Conversation Memory**: Maintains multi-turn context per conversation.
* 🔐 **Authentication**: User registration, login, token authentication, and isolated user chat histories.
* 🎨 **Modern Responsive UI**: Dark/Light mode, collapsible sidebar, Markdown rendering, syntax highlighted code blocks with one-click copy.
* 🚀 **Production Ready**: Dockerfile, Docker Compose, Nginx config, and Gunicorn configuration included.

---

## 🗓️ 10-Day Architecture Roadmap Overview

| Day | Feature | Tech / Implementation |
| :--- | :--- | :--- |
| **Day 1** | Foundation & Structure | Django 5.x project structure, environment configuration, settings |
| **Day 2** | Database Layer | `Conversation`, `Message`, `UserProfile`, and `AIUsage` models |
| **Day 3** | Authentication API | Token auth, registration, login, protected API endpoints |
| **Day 4** | AI Engine Integration | Multilingual prompt engineering, Gemini/OpenAI API + smart offline fallback |
| **Day 5** | Conversation Memory | Context window retrieval, chronological message buffering |
| **Day 6** | Web Search Grounding | DuckDuckGo search service, intent detection, source citations |
| **Day 7** | Modern Chat Frontend | Dark/Light UI, sidebar, message bubbles, markdown & code copy |
| **Day 8** | SSE Streaming & UX | `StreamingHttpResponse`, real-time chunks, auto-titling, rename/delete |
| **Day 9** | Security & Validation | CORS headers, payload validation, error handlers |
| **Day 10** | Production & Deployment | Dockerfile, docker-compose, Nginx reverse proxy, Gunicorn |

---

## 🚀 Quick Start (Local Setup)

### 1. Open the project in VS Code
Open folder:
```bash
C:\Users\HP\.gemini\antigravity\scratch\arafs_assistant
```

### 2. Configure Environment Variables (Optional)
Open `.env` and add your AI keys (e.g. Google Gemini API key):
```ini
GEMINI_API_KEY=your_gemini_api_key_here
AI_DEFAULT_MODEL=gemini-2.5-flash
```
*(If no API key is provided, the chatbot runs in an intelligent offline demo mode!)*

### 3. Run the Application
Execute with a single command:
```bash
python run.py
```
Or with standard Django commands:
```bash
python manage.py makemigrations accounts chatbot
python manage.py migrate
python manage.py runserver
```

### 4. Open in Browser
👉 **Web App:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
👉 **Register:** [http://127.0.0.1:8000/register/](http://127.0.0.1:8000/register/)  
👉 **Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)  
👉 **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📡 API Endpoints

### Authentication
* `POST /api/v1/auth/register/` — Create new account (returns Token)
* `POST /api/v1/auth/login/` — Login with username/email & password (returns Token)
* `POST /api/v1/auth/logout/` — Invalidate user token
* `GET /api/v1/auth/me/` — Get authenticated user details

### Chat & Conversations
* `GET /api/v1/chat/conversations/` — List all conversations of current user
* `POST /api/v1/chat/conversations/` — Create new conversation
* `GET /api/v1/chat/conversations/<id>/` — Get conversation details with full message history
* `PATCH /api/v1/chat/conversations/<id>/` — Rename or pin conversation
* `DELETE /api/v1/chat/conversations/<id>/` — Delete conversation
* `POST /api/v1/chat/stream/` — **SSE Streaming Chat Endpoint** (message, web search, model selection)
* `GET /api/v1/chat/search/?q=query` — Test web search grounding directly

---

## 🐳 Docker Deployment

To run the complete production stack (Django + PostgreSQL):

```bash
docker-compose -f deploy/docker-compose.yml up --build -d
```
"# Araf-s-AI" 
