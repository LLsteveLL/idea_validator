# Frontend

This folder contains a minimal static frontend for the Idea Validator backend.

## Pages

- `index.html`: idea input form
- `loading.html`: analysis progress transition page
- `result.html`: analysis result view
- `history.html`: saved analysis list
- `detail.html`: single saved analysis detail

## Run Locally

From the project root:

```bash
cd frontend
python3 -m http.server 3000
```

Then open:

- `http://127.0.0.1:3000`

The frontend expects the FastAPI backend to be running at:

- `http://127.0.0.1:8000`
