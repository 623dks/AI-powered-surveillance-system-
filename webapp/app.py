import os
import cv2
import numpy as np
from flask import Flask, request, render_template, jsonify
from ultralytics import YOLO
import base64
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO

app = Flask(__name__)

# Load model with fallback
MODEL_PATH = os.getenv('MODEL_PATH', 'weights/best.pt')
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model from {MODEL_PATH}: {e}")
    model = None

CLASSES = ['Grenade', 'Knife', 'Missile', 'Pistol', 'Rifle']

def send_threat_email(detections, image_b64):
    """Send email alert when threat is detected"""
    sender_email = os.getenv('SENDER_EMAIL', 'your_email@gmail.com')
    sender_password = os.getenv('SENDER_PASSWORD', 'your_app_password')
    recipient_email = os.getenv('RECIPIENT_EMAIL', 'alert@example.com')
    
    if sender_email == 'your_email@gmail.com':
        print("⚠️  Email credentials not configured. Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL env vars")
        return False
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        threat_list = '\n'.join([f"  • {d['class']}: {d['confidence']}% confidence" for d in detections])
        
        msg = MIMEText(f"""
⚠️ THREAT DETECTED ⚠️

Timestamp: {timestamp}
Threats Found: {len(detections)}

Detected Objects:
{threat_list}

Visit your dashboard for more details.
""")
        msg['Subject'] = f'🚨 ALERT: {len(detections)} Weapon(s) Detected - {timestamp}'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Send via Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✅ Email alert sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return jsonify({'error': 'Invalid image format'}), 400

    # Allow client to override confidence via form field (useful for camera mode)
    try:
        conf_threshold = float(request.form.get('conf', os.getenv('CONF_THRESHOLD', '0.5')))
    except Exception:
        conf_threshold = 0.5
    results = model(frame, conf=conf_threshold)
    annotated = results[0].plot()

    detections = []
    for box in results[0].boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        detections.append({
            'class': CLASSES[cls],
            'confidence': round(conf * 100, 1)
        })

    _, buffer = cv2.imencode('.jpg', annotated)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    # Send email alert if threats detected
    if len(detections) > 0:
        send_threat_email(detections, img_b64)

    return jsonify({
        'image': img_b64,
        'detections': detections,
        'count': len(detections),
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'email_sent': len(detections) > 0
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes': CLASSES
    })

if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
