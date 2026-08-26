"""
AI Service for Araf's Assistant.
Supports Google Gemini, OpenAI, and smart offline simulated mode.
"""
import os
import json
import time
import requests
import logging
from typing import List, Dict, Generator, Any

logger = logging.getLogger(__name__)

def call_gemini_api_stream(messages: List[Dict[str, str]], api_key: str, model: str = "gemini-2.5-flash") -> Generator[str, None, None]:
    """
    Calls Google Gemini REST API with SSE streaming.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
    
    contents = []
    system_instruction = None
    
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        
        if role == "system":
            system_instruction = {"parts": [{"text": content}]}
        elif role == "user":
            contents.append({"role": "user", "parts": [{"text": content}]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": content}]})
            
    payload: Dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
        }
    }
    if system_instruction:
        payload["systemInstruction"] = system_instruction

    try:
        response = requests.post(url, json=payload, stream=True, timeout=60)
        if response.status_code != 200:
            err_msg = f"Gemini API error ({response.status_code}): {response.text}"
            logger.error(err_msg)
            yield f"\n[Error: {err_msg}]"
            return

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                data_json = line_str[6:].strip()
                try:
                    data = json.loads(data_json)
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text_chunk = part.get("text", "")
                            if text_chunk:
                                yield text_chunk
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.exception("Gemini API streaming failed")
        yield f"\n[Network Error communicating with Gemini: {str(e)}]"


def call_openai_api_stream(messages: List[Dict[str, str]], api_key: str, model: str = "gpt-4o-mini") -> Generator[str, None, None]:
    """
    Calls OpenAI REST API with SSE streaming.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
        if response.status_code != 200:
            err_msg = f"OpenAI API error ({response.status_code}): {response.text}"
            logger.error(err_msg)
            yield f"\n[Error: {err_msg}]"
            return

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                data_json = line_str[6:].strip()
                if data_json == "[DONE]":
                    break
                try:
                    data = json.loads(data_json)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.exception("OpenAI API streaming failed")
        yield f"\n[Network Error communicating with OpenAI: {str(e)}]"


def simulate_offline_response(last_user_message: str) -> Generator[str, None, None]:
    """
    Provides rich, contextual multilingual responses in offline/demo mode when no API keys are provided.
    """
    msg = last_user_message.lower().strip()
    
    greetings = ['hello', 'hi', 'hey', 'salam', 'সালাম', 'কেমন আছ', 'kemon acho', 'kemon asen']
    is_greeting = False
    if msg in greetings:
        is_greeting = True
    elif len(msg) < 15 and any(greet in msg for greet in greetings):
        is_greeting = True

    if is_greeting:
        reply = (
            "Hi! 😊 I’m doing great, thanks for asking! How are you doing? What are we working on today? 🚀\n\n"
            "আমি **Araf's Assistant** — তোমার পার্সোনাল মাল্টিলিঙ্গুয়াল এআই অ্যাসিস্ট্যান্ট।\n\n"
            "আমি বাংলা, English, এবং Banglish-এ যেকোনো প্রশ্নের উত্তর ও কোডিং হেল্প দিতে পারি।\n\n"
            "**আমি তোমাকে কীভাবে সাহায্য করতে পারি?**\n"
            "- 💻 পাইথন / সি / জ্যাঙ্গো প্রোগ্রামিং\n"
            "- 🌐 ওয়েব ডেভেলপমেন্ট ও এপিআই ডিজাইন\n"
            "- 🔍 অনলাইন সার্চ ও রিয়েল-টাইম তথ্য অনুসন্ধান\n"
            "- 📝 সাধারণ আলোচনা ও প্রজেক্ট প্ল্যানিং\n\n"
            "*টিপ: ফুল ক্লাউড এলএলএম (Gemini বা OpenAI) চালু করতে `.env` ফাইলে `GEMINI_API_KEY` যুক্ত করতে পারো।* 🚀"
        )
    elif 'c program' in msg or 'c language' in msg or 'c ল্যাঙ্গুয়েজ' in msg or 'c নিয়ে' in msg or 'c programming' in msg:
        reply = (
            "অবশ্যই! 😊 C Programming নিয়ে একদম basic থেকে বুঝিয়ে বলতে পারি।\n\n"
            "🔹 **C Programming কী?**\n"
            "C হলো একটি powerful, fast এবং widely-used programming language। এটি দিয়ে software, operating system, embedded system, compiler ইত্যাদি তৈরি করা যায়।\n\n"
            "🔹 **C Programming-এ প্রধান যেসব বিষয় শিখবে:**\n"
            "- **Basic Syntax**: `#include <stdio.h>`, `main()`, `printf()`, `return 0`\n"
            "- **Variables & Data Types**: `int age = 20;`, `float price = 99.50;`, `char grade = 'A';`\n"
            "- **Input / Output**: `scanf()` & `printf()`\n"
            "- **Operators**: Arithmetic (`+ - * / %`), Relational (`> < == !=`), Logical (`&& || !`)\n"
            "- **Conditional Statements**: `if`, `else if`, `else`, `switch`\n"
            "- **Loops**: `for`, `while`, `do-while`\n"
            "- **Array & String**\n"
            "- **Functions & Recursion**\n"
            "- **Pointers ⭐**: C-এর সবচেয়ে গুরুত্বপূর্ণ এবং পাওয়ারফুল বিষয়\n"
            "- **Structure & Union**\n"
            "- **File Handling & Dynamic Memory Allocation** (`malloc()`, `free()`)\n\n"
            "🔥 **একটা খুব basic C program:**\n"
            "```c\n"
            "#include <stdio.h>\n\n"
            "int main() {\n"
            "    printf(\"Hello World!\\n\");\n"
            "    return 0;\n"
            "}\n"
            "```\n\n"
            "🎯 তুমি যদি C শিখতে চাও, আমরা আজ থেকেই **Lesson 1: C Programming Zero to Hero** শুরু করতে পারি!"
        )
    elif 'add' in msg or 'sum' in msg or 'যোগ' in msg or ('python' in msg and ('code' in msg or 'number' in msg or 'সংখ্যা' in msg or 'likhe' in msg)):
        reply = (
            "অবশ্যই 😊 Python দিয়ে দুইটি সংখ্যা যোগ করার খুব সহজ code:\n\n"
            "```python\n"
            "# Python - Adding two numbers from user input\n"
            "num1 = int(input(\"Enter first number: \"))\n"
            "num2 = int(input(\"Enter second number: \"))\n\n"
            "result = num1 + num2\n\n"
            "print(\"Sum =\", result)\n"
            "```\n\n"
            "**উদাহরণ:**\n"
            "যদি তুমি input দাও:\n"
            "```text\n"
            "Enter first number: 10\n"
            "Enter second number: 20\n"
            "```\n"
            "তাহলে output হবে:\n"
            "```text\n"
            "Sum = 30\n"
            "```\n\n"
            "আরেকটি সহজ উপায়ে সরাসরি করার নিয়ম:\n"
            "```python\n"
            "a = 10\n"
            "b = 20\n"
            "print(a + b)  # Output: 30\n"
            "```"
        )
    elif 'english' in msg or 'কীভাবে' in msg or 'translate' in msg or 'english এ' in msg:
        reply = (
            "অবশ্যই! 😊 আপনার বাক্যটির সুন্দর ও প্রাকৃতিক English রূপ নিচে দেওয়া হলো:\n\n"
            "**বাংলা / বাংলিশ:** \"Hi, tumi kmn aso? atar english thik kore likhe daw\"\n\n"
            "🇬🇧 **Correct English Translation:**\n"
            "> *\"Hi! How are you doing? Please write this correctly in English.\"*\n\n"
            "অথবা ফ্রেন্ডলি স্টাইলে:\n"
            "> *\"Hi! How are you? Could you please translate this into English?\"*\n\n"
            "আপনার কি অন্য কোনো বাক্যের ইংরেজি অনুবাদ লাগবে?"
        )
    elif 'django' in msg or 'জ্যাঙ্গো' in msg:
        reply = (
            "### 🚀 Django Framework Guide\n\n"
            "**Django** হলো Python-এর একটি অত্যন্ত জনপ্রিয়, হাই-লেভেল এবং 'Batteries-included' ওয়েব ফ্রেমওয়ার্ক।\n\n"
            "🔹 **কেন Django সেরা?**\n"
            "1. **MVT Architecture**: Model-View-Template প্যাটার্ন সাপোর্ট করে।\n"
            "2. **Built-in Admin Panel**: কোনো বাড়তি কোড ছাড়াই অটোমেটিক অ্যাডমিন ড্যাশবোর্ড পাওয়া যায়।\n"
            "3. **ORM**: SQL না লিখেও Python ক্লাসের মাধ্যমে ডাটাবেজ হ্যান্ডেল করা যায়।\n"
            "4. **Security**: CSRF, SQL Injection, XSS প্রটেকশন ডিফল্টভাবেই থাকে।\n\n"
            "```python\n"
            "# Django Model Example\n"
            "from django.db import models\n\n"
            "class Article(models.Model):\n"
            "    title = models.CharField(max_length=200)\n"
            "    content = models.TextField()\n"
            "    created_at = models.DateTimeField(auto_now_add=True)\n"
            "```"
        )
    elif 'fastapi' in msg:
        reply = (
            "### ⚡ FastAPI Framework Guide\n\n"
            "**FastAPI** হলো Python 3.8+ ভিত্তিক একটি আধুনিক, ফাস্ট (high-performance) ওয়েব ফ্রেমওয়ার্ক যা RESTful API তৈরির জন্য জনপ্রিয়।\n\n"
            "🔹 **প্রধান সুবিধাসমূহ:**\n"
            "- ⚡ **High Performance**: NodeJS ও Go-এর সমকক্ষ পারফরম্যান্স।\n"
            "- 📖 **Auto OpenAPI**: `/docs` ও `/redoc` এ রিয়েল-টাইম ইন্টারেক্টিভ ডকুমেন্টেশন পাওয়া যায়।\n"
            "- 🛡️ **Pydantic Validation**: ইনপুট ডাটার শক্তিশালী টাইপ চেকিং।"
        )
    elif 'python' in msg or 'পাইথন' in msg:
        reply = (
            "### 🐍 Python Programming Language\n\n"
            "Python হলো একটি versatile, readable এবং dynamic প্রোগ্রামিং ভাষা।\n\n"
            "```python\n"
            "# Python List Comprehension Example\n"
            "numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"
            "evens = [n for n in numbers if n % 2 == 0]\n"
            "print('Even numbers:', evens)  # Output: [2, 4, 6, 8, 10]\n"
            "```"
        )
    elif 'node' in msg or 'js' in msg or 'javascript' in msg or 'react' in msg:
        reply = (
            "### 🟢 Node.js & JavaScript (JS) পরিচিতি\n\n"
            "**Node.js** হলো একটি asynchronous, event-driven JavaScript runtime পরিবেশ যা Chrome-এর V8 JavaScript 엔진-এর উপর তৈরি। এটি দিয়ে সার্ভার-সাইড (Backend) ওয়েব অ্যাপ্লিকেশন এবং API তৈরি করা হয়।\n\n"
            "🔹 **Node.js-এর প্রধান সুবিধাসমূহ:**\n"
            "1. **Non-blocking I/O**: একসাথে হাজার হাজার ক্লায়েন্ট রিকোয়েস্ট খুব দ্রুত প্রসেস করতে পারে।\n"
            "2. **Single Programming Language**: ফ্রন্টএন্ড এবং ব্যাকএন্ড উভয়েই JavaScript ব্যবহার করা যায়।\n"
            "3. **NPM (Node Package Manager)**: বিশ্বের সবচেয়ে বড় ওপেন সোর্স প্যাকেজ লাইব্রেরি।\n\n"
            "🔥 **একটি সহজ Node.js HTTP Server উদাহরণ:**\n"
            "```javascript\n"
            "const http = require('http');\n\n"
            "const server = http.createServer((req, res) => {\n"
            "  res.statusCode = 200;\n"
            "  res.setHeader('Content-Type', 'text/plain');\n"
            "  res.end('Hello World from Node.js!');\n"
            "});\n\n"
            "server.listen(3000, () => {\n"
            "  console.log('Server running at http://localhost:3000/');\n"
            "});\n"
            "```\n\n"
            "🎯 আপনি কি Node.js Express.js বা REST API শেখা শুরু করতে চান?"
        )
    elif 'html' in msg or 'css' in msg or 'web' in msg or 'frontend' in msg:
        reply = (
            "### 🌐 Web Development (HTML, CSS & JavaScript)\n\n"
            "ওয়েব ডেভেলপমেন্ট মূলত তিনটি মূল উপাদানের ওপর দাঁড়িয়ে আছে:\n"
            "1. 🧱 **HTML**: ওয়েবসাইটের কঙ্কাল বা স্ট্রাকচার তৈরি করে।\n"
            "2. 🎨 **CSS**: ডিজাইন, কালার এবং রেসপন্সিভ লেআউট দেয়।\n"
            "3. ⚡ **JavaScript**: ওয়েবসাইটে লজিক, ইন্টারঅ্যাকশন ও অ্যানিমেশন যুক্ত করে।\n\n"
            "```html\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><title>My Web Page</title></head>\n"
            "<body>\n"
            "  <h1>Hello, Web Development!</h1>\n"
            "</body>\n"
            "</html>\n"
            "```"
        )
    elif 'sql' in msg or 'database' in msg or 'postgres' in msg or 'mongo' in msg:
        reply = (
            "### 🗄️ Database System (SQL vs NoSQL)\n\n"
            "ডাটাবেজ হলো তথ্য গুছিয়ে রাখার এবং দ্রুত খুঁজে বের করার সিস্টেম।\n\n"
            "🔹 **Relational Database (SQL)**: Table ও Row আকারে ডাটা রাখে (যেমন: PostgreSQL, MySQL, SQLite)।\n"
            "🔹 **NoSQL Database**: JSON/Document আকারে ডাটা রাখে (যেমন: MongoDB)।\n\n"
            "```sql\n"
            "-- SQL Table Creation Example\n"
            "CREATE TABLE users (\n"
            "    id SERIAL PRIMARY KEY,\n"
            "    username VARCHAR(50) NOT NULL,\n"
            "    email VARCHAR(100) UNIQUE NOT NULL\n"
            ");\n"
            "```"
        )
    else:
        topic = last_user_message.strip()
        reply = (
            f"### 🤖 Araf's Assistant Guide\n\n"
            f"আপনি জানতে চেয়েছেন: **\"{topic}\"**\n\n"
            "এটি একটি চমৎকার প্রশ্ন! আমি সি, পাইথন, জাভাস্ক্রিপ্ট, নোড.জেএস, জ্যাঙ্গো, ডাটাবেজ এবং যেকোনো টেকনোলজি বা অনুবাদের প্রশ্নের ডাইনামিক উত্তর দিতে প্রস্তুত।\n\n"
            "💡 **একটি ছোট আপডেট:**\n"
            "বর্তমানে প্রজেক্টটি **Offline Demo Mode**-এ চলছে বলে যেকোনো সম্পূর্ণ নতুন প্রশ্নের উত্তর স্বয়ংক্রিয়ভাবে জেনারেট হতে `.env` ফাইলে একটি ফ্রি `GEMINI_API_KEY` প্রয়োজন।\n\n"
            "🔑 **ফ্রি API Key পাওয়ার ৩টি সহজ ধাপ:**\n"
            "1. [aistudio.google.com](https://aistudio.google.com/) এ গিয়ে **Create API Key** বাটনে চাপ দিন।\n"
            "2. Key-টি কপি করে প্রজেক্টের `.env` ফাইলে বসিয়ে দিন: `GEMINI_API_KEY=your_key`\n"
            "3. সাথে সাথে আপনার Araf's Assistant সব প্রশ্নের 100% আসল AI উত্তর দেবে!"
        )

    words = reply.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.02)


def stream_ai_response(messages: List[Dict[str, str]], model: str = None) -> Generator[str, None, None]:
    """
    Main entry point for streaming AI responses.
    Checks environment keys and selects the best provider. Auto-reloads .env dynamically.
    """
    from dotenv import load_dotenv
    load_dotenv(override=True)

    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    default_model = model or os.getenv('AI_DEFAULT_MODEL', 'gemini-2.5-flash')

    if gemini_key:
        yield from call_gemini_api_stream(messages, api_key=gemini_key, model=default_model)
    elif openai_key:
        yield from call_openai_api_stream(messages, api_key=openai_key, model="gpt-4o-mini")
    else:
        last_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_msg = m.get("content", "")
                break
        yield from simulate_offline_response(last_msg)



def generate_ai_response(messages: List[Dict[str, str]], model: str = None) -> str:
    """
    Synchronous response generator.
    """
    chunks = []
    for chunk in stream_ai_response(messages, model=model):
        chunks.append(chunk)
    return "".join(chunks)
