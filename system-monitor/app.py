from flask import Flask, render_template
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)

def get_metrics():
    conn = sqlite3.connect('metrics.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 10')
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/')
def index():
    metrics = get_metrics()
    times = [row[0] for row in metrics]
    cpu_usage = [row[1] for row in metrics]
    memory_usage = [row[2] for row in metrics]
    disk_usage = [row[3] for row in metrics]

    plt.figure(figsize=(10, 5))
    plt.plot(times, cpu_usage, label='CPU Usage')
    plt.plot(times, memory_usage, label='Memory Usage')
    plt.plot(times, disk_usage, label='Disk Usage')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig('static/metrics.png')
    plt.close()

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
