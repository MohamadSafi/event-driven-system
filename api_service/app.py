from flask import Flask, request, jsonify
import pika
import os

app = Flask(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_QUEUE = 'incoming_messages'

def publish_message(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=message
    )
    connection.close()

@app.route('/submit', methods=['POST'])
def submit_message():
    data = request.get_json()
    if not data or 'message' not in data or 'alias' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    message = {
        'alias': data['alias'],
        'message': data['message']
    }

    try:
        publish_message(str(message))
        return jsonify({'status': 'Message received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
