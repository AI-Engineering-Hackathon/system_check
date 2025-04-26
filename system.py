import psutil
import time
from ping3 import ping
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# =============== LOAD ENV VARIABLES ===============
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
CHECK_INTERVAL= int(os.getenv("CHECK_INTERVAL"))
UTILIZATION_THRESHOLD= int(os.getenv("UTILIZATION_THRESHOLD"))
LATENCY_THRESHOLD_MS= int(os.getenv("LATENCY_THRESHOLD_MS"))
# =============== CONFIGURATION ===============
SERVER_TO_PING = "http://127.0.0.1:8010"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# =============== FUNCTIONS ===============

def send_alert(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Alert email sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def check_resources():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    print(f"[Resource Check] CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")
    return cpu, memory, disk

def check_latency(server):
    latency = ping(server)
    if latency is not None:
        latency_ms = latency * 1000
        print(f"[Latency Check] {server}: {latency_ms:.2f} ms")
        return latency_ms
    else:
        print(f"[Latency Check] Failed to ping {server}")
        return float('inf')

# =============== MAIN LOOP ===============

print("🚀 Starting system monitor...")

while True:
    cpu, memory, disk = check_resources()
    latency_ms = check_latency(SERVER_TO_PING)

    if (cpu > UTILIZATION_THRESHOLD or 
        memory > UTILIZATION_THRESHOLD or 
        disk > UTILIZATION_THRESHOLD or 
        latency_ms > LATENCY_THRESHOLD_MS):
        
        alert_subject = "⚠️ System Alert: High Usage or Latency"
        alert_body = (f"Resource/Latency Alert!\n\n"
                      f"CPU: {cpu}%\n"
                      f"Memory: {memory}%\n"
                      f"Disk: {disk}%\n"
                      f"Latency: {latency_ms:.2f} ms\n")
        send_alert(alert_subject, alert_body)

    time.sleep(CHECK_INTERVAL)
