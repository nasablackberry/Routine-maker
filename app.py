from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store routines and their timers in memory
routines = []

class Routine:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None

    def start_timer(self):
        self.start_time = datetime.now()

    def stop_timer(self):
        self.end_time = datetime.now()

    def get_duration(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            minutes = delta.total_seconds() // 60
            seconds = delta.total_seconds() % 60
            return minutes, seconds
        return None, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_routine():
    routine_name = request.form.get('routine')
    if routine_name:
        routines.append(Routine(routine_name))
    return redirect(url_for('home'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete_routine(index):
    if 0 <= index < len(routines):
        routines.pop(index)
    return redirect(url_for('home'))

@app.route('/start/<int:index>', methods=['POST'])
def start_timer(index):
    if 0 <= index < len(routines):
        routines[index].start_timer()
    return redirect(url_for('home'))

@app.route('/stop/<int:index>', methods=['POST'])
def stop_timer(index):
    if 0 <= index < len(routines):
        routines[index].stop_timer()
    return redirect(url_for('home'))

@app.route('/routine_data', methods=['GET'])
def routine_data():
    data = [
        {
            'name': routine.name,
            'start_time': routine.start_time.strftime('%Y-%m-%d %H:%M:%S') if routine.start_time else None,
            'end_time': routine.end_time.strftime('%Y-%m-%d %H:%M:%S') if routine.end_time else None,
            'duration': routine.get_duration()
        }
        for routine in routines
    ]
    return jsonify(data)

@socketio.on('connect')
def handle_connect():
    emit('update_routines', get_routine_data())

def get_routine_data():
    return [
        {
            'name': routine.name,
            'start_time': routine.start_time.strftime('%Y-%m-%d %H:%M:%S') if routine.start_time else None,
            'end_time': routine.end_time.strftime('%Y-%m-%d %H:%M:%S') if routine.end_time else None,
            'duration': routine.get_duration()
        }
        for routine in routines
    ]

def update_routines_periodically():
    while True:
        time.sleep(1)  # Adjust the interval as needed
        socketio.emit('update_routines', get_routine_data())

if __name__ == '__main__':
    socketio.start_background_task(update_routines_periodically)
    socketio.run(app, debug=True)
