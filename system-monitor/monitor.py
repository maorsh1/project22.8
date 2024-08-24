import psutil
import time
import logging
import requests
import smtplib
from email.mime.text import MIMEText
import sqlite3
from flask import Flask, render_template
import matplotlib.pyplot as plt

# --- Configurations ---
SMTP_SERVER = 'smtp.your-email-provider.com'
SMTP_PORT = 587
SMTP_USER = 'your-email@example.com'
SMTP_PASSWORD = 'your-password'
EMAIL_FROM = 'your-email@example.com'
EMAIL_TO = 'recipient-email@example.com'

CPU_THRESHOLD = 80.0  # 80%
MEMORY_THRESHOLD = 80.0  # 80%
DISK_THRESHOLD = 90.0  # 90%

# --- Initialize Logging ---
logging.basicConfig(filename='system_metrics.log', level=logging.INFO, format='%(asctime)s %(message)s')

# --- Initialize SQLite Database ---
conn = sqlite3.connect('metrics.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    bytes_sent INTEGER,
                    bytes_recv INTEGER)''')
conn.commit()

def collect_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    network_info = psutil.net_io_counters()

    metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'bytes_sent': network_info.bytes_sent,
        'bytes_recv': network_info.bytes_recv
    }

    return metrics

def collect_process_metrics(process_name):
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        if proc.info['name'] == process_name:
            return {
                'pid': proc.info['pid'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent']
            }
    return None

def log_metrics():
    metrics = collect_metrics()
    logging.info(f"CPU Usage: {metrics['cpu_usage']}%")
    logging.info(f"Memory Usage: {metrics['memory_usage']}%")
    logging.info(f"Disk Usage: {metrics['disk_usage']}%")
    logging.info(f"Bytes Sent: {metrics['bytes_sent']}")
    logging.info(f"Bytes Received: {metrics['bytes_recv']}")

    cursor.execute('''INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, disk_usage, bytes_sent, bytes_recv)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                   (time.strftime('%Y-%m-%d %H:%M:%S'),
                    metrics['cpu_usage'],
                    metrics['memory_usage'],
                    metrics['disk_usage'],
                    metrics['bytes_sent'],
                    metrics['bytes_recv']))
    conn.commit()

def check_thresholds(metrics):
    if metrics['cpu_usage'] > CPU_THRESHOLD:
        message = f"Warning: CPU usage is high at {metrics['cpu_usage']}%"
        logging.warning(message)
        send_email("CPU Usage Alert", message)
    if metrics['memory_usage'] > MEMORY_THRESHOLD:
        message = f"Warning: Memory usage is high at {metrics['memory_usage']}%"
        logging.warning(message)
        send_email("Memory Usage Alert", message)
    if metrics['disk_usage'] > DISK_THRESHOLD:
        message = f"Warning: Disk usage is high at {metrics['disk_usage']}%"
        logging.warning(message)
        send_email("Disk Usage Alert", message)

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())

def log_process_metrics(process_name):
    process_metrics = collect_process_metrics(process_name)
    if process_metrics:
        logging.info(f"Process: {process_name} PID: {process_metrics['pid']} "
                     f"CPU: {process_metrics['cpu_percent']}% "
                     f"Memory: {process_metrics['memory_percent']}%")
    else:
        logging.warning(f"Process {process_name} not found.")

if __name__ == "__main__":
    monitored_process = 'python.exe'
    while True:
        metrics = collect_metrics()
        log_metrics()
        check_thresholds(metrics)
        log_process_metrics(monitored_process)
        time.sleep(10)
