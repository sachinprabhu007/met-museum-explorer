# Met Museum Explorer

A full-stack museum collection explorer built with **React** and **FastAPI**, using the Metropolitan Museum of Art Collection API and a Groq-powered LLM Museum Guide.

## Features

- Search the Met Museum collection
- Artist-based filtering
- Artwork images and metadata
- Progressive **Load More** results
- Backend batching and caching
- Controlled requests to the external API
- LLM-powered **Museum Guide**
- Ask questions about the currently retrieved artworks
- Conversation history in the Museum Guide
- Markdown-rendered LLM responses
- LLM evaluation with **DeepEval**
- Answer Relevancy and Faithfulness evaluation

## Tech Stack

- **Frontend:** React, Vite, JavaScript, CSS
- **Backend:** Python, FastAPI, HTTPX, Pydantic
- **LLM:** Groq
- **LLM Evaluation:** DeepEval
- **Museum API:** Metropolitan Museum of Art Collection API

## Architecture

```text
                         ┌─────────────────────┐
                         │   React Frontend    │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                  Search                    Museum Guide
                     │                             │
                     ▼                             ▼
              GET /search                POST /museum-guide
                     │                             │
                     ▼                             │
             FastAPI Backend                       │
                     │                             │
                     ▼                             │
             Met Museum API                        │
                     │                             │
                     ▼                             │
              Artwork records                      │
                     │                             │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                            Artwork Context
                                    │
                                    ▼
                               Groq LLM
                                    │
                                    ▼
                               LLM Answer
                                    │
                                    ▼
                               DeepEval
                              ┌─────┴─────┐
                              │           │
                              ▼           ▼
                       Answer Relevancy  Faithfulness
```

### Museum Guide 
The Museum Guide uses the artwork results already retrieved from the Met Museum API.

For example:
```
Search
  ↓
vincent
  ↓
Met Museum results
  ↓
Artwork context
  ↓
Museum Guide
```
When the user asks a question, the frontend sends only the question to:
```POST /museum-guide```

The backend combines the question with the currently retrieved artwork context before sending it to the LLM.

This allows questions such as:

```Which Vincent van Gogh artworks are in these Met Museum results?```
or:
```Which of these artworks are tagged as still lifes?```

The Museum Guide is displayed only after search results are available.

### LLM Evaluation

The generated Museum Guide response is evaluated in the backend using DeepEval.

Currently, the system evaluates:

### Answer Relevancy

Measures whether the generated answer is relevant to the user's question.

### Faithfulness

Measures whether the generated answer is supported by the retrieved Met Museum artwork context.

The evaluation uses the same artwork context supplied to the Museum Guide:

```
Met Museum artwork data
        ↓
   retrieval_context
        ↓
      DeepEval
        ↓
Answer Relevancy
Faithfulness
```
Example evaluation from the Vincent van Gogh test case:
```
Answer Relevancy | score=1.000
Faithfulness     | score=1.000
```
These scores represent a specific test run and are not intended to represent universal system performance.

Evaluation results are currently written to the backend terminal logs.

### Search and Progressive Loading

The backend searches the Met Museum collection and retrieves artwork metadata in controlled batches.

For example, searching for:

```vincent```

returns candidate object IDs from the Met API. The backend processes these in batches and returns matching artwork records to the frontend.

The frontend supports progressive loading using Load More.

### Running

### Backend

```bash
cd backend
uv run uvicorn main:app --reload
```

API: http://localhost:8000

Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

### Environment Variables

Backend environment variables are stored locally in:

```backend/.env```

An example configuration is provided in:

```backend/.env.example```

The Groq API key is kept on the backend and is never exposed to the React frontend.

The frontend uses:

```VITE_API_URL```

for the backend API URL.

### Example

Searching for `vincent` returns 193 candidate objects from the Met API.

Results are loaded progressively:

```
0–69     → 5 matches
70–139   → 5 matches
140–192  → 0 matches
```

The search returns 10 Vincent van Gogh artworks in total.

### Project Structure

```
met-museum-explorer/
│
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── service.py
│   ├── llm_service.py
│   ├── evaluation.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── api/
    │       └── museum.js
    ├── index.html
    ├── package.json
    └── package-lock.json
```

### Notes

The backend processes requests in controlled batches and caches retrieved artwork records to reduce repeated API calls and avoid excessive requests to the Met Museum API.

The LLM operates on the artwork context retrieved by the backend rather than making an independent museum search for every question.

DeepEval runs on the backend and currently reports evaluation metrics in the terminal.