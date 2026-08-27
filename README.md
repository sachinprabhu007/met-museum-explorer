# Met Museum Explorer

A full-stack museum collection explorer built with **React** and **FastAPI**, using the Metropolitan Museum of Art Collection API.

## Features

- Search the Met Museum collection
- Artist-based filtering
- Artwork images and metadata
- Progressive **Load More** results
- Backend batching and caching
- Controlled requests to the external API

## Tech Stack

- **Frontend:** React, Vite, JavaScript, CSS
- **Backend:** Python, FastAPI, HTTPX, Pydantic
- **API:** Metropolitan Museum of Art Collection API

## Architecture

```text
React
  │
  ▼
FastAPI
  │
  ▼
Met Museum API
  │
  ▼
Object IDs
  │
  ├── batches
  ├── caching
  └── artist filtering
  │
  ▼
React
  │
  └── Load More
```
## Running

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

### Example

Searching for `vincent` returns 193 candidate objects from the Met API.

Results are loaded progressively:

```
0–69     → 5 matches
70–139   → 5 matches
140–192  → 0 matches
```

The search returns 10 Vincent van Gogh artworks in total.

### Notes

The backend processes requests in controlled batches and caches retrieved artwork records to reduce repeated API calls and avoid excessive requests to the external API.