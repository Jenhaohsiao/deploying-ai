# Radio DJ Chat — Weather & Music Assistant

A conversational AI chatbot that acts as a friendly radio DJ, offering **weather forecasts** and **music recommendations**.  
When you ask about the weather, it automatically suggests music that matches the mood.

---

## Core Services

### 1. Weather API Integration
- **APIs**: Nominatim (geocoding), 7Timer (weather)
- **Features**: 3-day forecasts, commuter advice, multi-language support  
- **Example**: “What’s the weather in Tokyo?” → Returns forecast + mood-based music

### 2. Semantic Music Search
- **Database**: ChromaDB with 500 Pitchfork reviews  
- **Technology**: OpenAI embeddings for semantic search  
- **Example**: “Recommend indie rock albums” → Returns relevant albums and excerpts

### 3. Function Calling
- **Tools**: `get_coordinates`, `get_weather`, `search_music`  
- **Logic**: The AI automatically chains tools to answer queries naturally

---

## Guardrails
- **Restricted Topics**: Cats/dogs, horoscopes, Taylor Swift  
- **Token Limit**: 200 per message  
- **Scope**: Weather and music only  

---

## Multi-Language Support
Auto-detects English, Traditional Chinese, Simplified Chinese, and Japanese.

---

## Quick Start

```bash
# 1. Configure API key
# Create file: 05_src/.secrets
# Add: OPENAI_API_KEY=your_api_key_here

# 2. Start ChromaDB
cd 05_src/deploying_ai_data
docker compose up -d chromadb

# 3. Initialize database
cd ../assignment_chat
python setup_chromadb.py

# 4. Run app
python app.py
```
Access at: `http://127.0.0.1:7860`
