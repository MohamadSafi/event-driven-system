from multiprocessing import Process, Queue
from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# Queues for inter-process communication
queue_input = Queue()
queue_filter = Queue()
queue_screaming = Queue()

def filter_process(input_queue, output_queue):
    STOP_WORDS = {'bird-watching', 'ailurophobia', 'mango'}
    while True:
        message = input_queue.get()
        if message is None:
            break  # Exit condition
        text = message.get('message', '')
        if any(stop_word in text for stop_word in STOP_WORDS):
            print(f"Message discarded due to stop-word: {text}")
        else:
            output_queue.put(message)

def screaming_process(input_queue, output_queue):
    while True:
        message = input_queue.get()
        if message is None:
            break  # Exit condition
        message['message'] = message['message'].upper()
        output_queue.put(message)

def publish_process(input_queue):
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.example.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER', 'your_email@example.com')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_password')
    RECIPIENTS = os.environ.get('RECIPIENTS', 'recipient@example.com').split(',')

    while True:
        message = input_queue.get()
        if message is None:
            break  # Exit condition
        alias = message.get('alias', '')
        text = message.get('message', '')

        try:
            msg = MIMEText(f"From user: {alias}\nMessage: {text}")
            msg['Subject'] = 'New Message'
            msg['From'] = SMTP_USER
            msg['To'] = ', '.join(RECIPIENTS)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())
            print(f"Email sent for message: {text}")
        except Exception as e:
            print(f"Failed to send email: {e}")

@app.route('/submit', methods=['POST'])
def submit_message():
    data = request.get_json()
    if not data or 'message' not in data or 'alias' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    message = {
        'alias': data['alias'],
        'message': data['message']
    }

    queue_input.put(message)
    return jsonify({'status': 'Message received'}), 200

if __name__ == '__main__':
    # Start the filter, screaming, and publish processes
    p_filter = Process(target=filter_process, args=(queue_input, queue_filter))
    p_screaming = Process(target=screaming_process, args=(queue_filter, queue_screaming))
    p_publish = Process(target=publish_process, args=(queue_screaming,))

    p_filter.start()
    p_screaming.start()
    p_publish.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)

    # Wait for processes to finish (they won't unless we implement a shutdown)
    p_filter.join()
    p_screaming.join()
    p_publish.join()
