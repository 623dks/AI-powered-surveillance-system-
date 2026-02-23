# AEGIS Weapon Detection System - Deployment Guide

## 📋 Prerequisites
- Python 3.11+ installed locally
- `best.pt` model in `weights/` folder
- Git installed
- Render.com account

---

## 🧪 Local Testing

### 1. **Set up virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

### 3. **Run Flask app**
```powershell
$env:FLASK_ENV = "development"
python app.py
```
Visit: `http://localhost:5000`

### 4. **Test detection endpoint**
```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:5000/detect
```

---

## 🚀 Deploy to Render

### 1. **Prepare GitHub repository**
```powershell
git add .
git commit -m "Add weapon detection webapp"
git push
```

### 2. **Create Render Web Service**
- Go to [render.com](https://render.com)
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repo
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- Set **Environment**: Python 3.11

### 3. **Upload Model to Render**
Option A (Recommended): Add to `.env` on Render:
```
MODEL_PATH=weights/best.pt
```

Option B (Large file issue - 200MB limit):
- Use a cloud storage service (AWS S3, Firebase)
- Update `MODEL_PATH` env variable in Render dashboard
- Modify `app.py` to download model on startup

### 4. **Deploy**
- Push changes to GitHub
- Render auto-deploys on push

### 5. **Test Live API**
```bash
curl https://your-app.onrender.com/health
curl -X POST -F "image=@test.jpg" https://your-app.onrender.com/detect
```

---

## ⚠️ Important Notes

- **Model Size**: `best.pt` is ~200MB. Render free tier has file limits.
  - Solution: Use S3 or other cloud storage
- **Cold Starts**: First request takes 10-20s (model loading)
- **Confidence Threshold**: Currently set to 0.5, adjust in `app.py` line 40 if needed
- **CORS**: Add `flask-cors` if frontend is on different domain

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not loading | Check `MODEL_PATH` env var, verify best.pt exists |
| 503 Service Unavailable | Model failed to load; check Render logs |
| Slow inference | Normal for YOLOv8n; consider GPU for production |
| File size too large | Move model to cloud storage, download at runtime |

---

## 📊 API Reference

### `GET /`
Returns HTML interface

### `GET /health`
```json
{
  "status": "healthy",
  "model_loaded": true,
  "classes": ["Grenade", "Knife", "Missile", "Pistol", "Rifle"]
}
```

### `POST /detect`
**Request**: multipart form with `image` field  
**Response**:
```json
{
  "image": "base64_encoded_jpg",
  "detections": [
    {"class": "Pistol", "confidence": 92.3},
    {"class": "Rifle", "confidence": 87.1}
  ],
  "count": 2,
  "timestamp": "14:32:58"
}
```

---

## 📝 Next Steps
1. Test locally with real images
2. Push to GitHub
3. Create Render web service
4. Monitor detection accuracy with live data
5. Add database logging for detected weapons/timestamps
