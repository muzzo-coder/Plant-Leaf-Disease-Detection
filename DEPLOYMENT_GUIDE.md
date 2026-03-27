# 🚀 Production Deployment Guide

This platform is containerized and abstracted. There are several ways to scale this to real users safely.

## Recommended Cloud Stack
- **Compute (Backend)**: Render, Google Cloud Run, or AWS App Runner.
- **Static Assets (Optional Frontend)**: Vercel or Netlify (if the frontend is cleanly detached from Flask). Here, Flask serves the UI, so containerized platform is best.

## Strategy: Docker & Gunicorn (Standard)

1. **Build Container:**
   ```bash
   docker build -t leafai-platform .
   ```
2. **Run Container Locally (Testing):**
   ```bash
   docker run -d -p 8000:8000 --env FLASK_DEBUG=False leafai-platform
   ```
   *Note: Gunicorn runs internally at port 8000 as specified in `gunicorn.conf.py`.*

3. **Deploy to Render.com:**
   - Connect your GitHub repository to Render.
   - Select "Web Service".
   - Environment: `Docker`.
   - Render will build the container automatically and expose the HTTPS routes. Set `PORT=8000` in the Environment Variables.

## Auto-Scaling Suggestions
1. **Model Cold Starts:** ML models take several seconds to load into memory (`app.py` -> `PredictionService`). You should ensure the hosting provider doesn't constantly spin down instances to zero unless you configure a warm-up ping.
2. **Memory Leaks:** For Keras/TensorFlow, thread pooling can occasionally cause memory footprint bloating over extensive periods. We configured `gunicorn` with a conservative thread count, but setting an explicit `--max-requests 500` flag in Gunicorn forces workers to rotate periodically, clearing RAM.

## Setting Up Custom Environments
Create a `.env` file for production keys:
```env
FLASK_DEBUG=False
SECRET_KEY=super-secure-generated-key-here
PORT=8000
```
*(The Flask app is set to dynamically pick these up via `src.config`.)*
