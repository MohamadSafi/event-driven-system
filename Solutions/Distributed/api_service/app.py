from flask import Flask, request, jsonify
import pika
import os
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
RABBITMQ_QUEUE = 'incoming_messages'

def publish_message(message):
    logger.info("Attempting to publish message to RabbitMQ")
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=False)
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=message
    )
    logger.info(f"Successfully published message to queue {RABBITMQ_QUEUE}")
    connection.close()

@app.route('/submit', methods=['POST'])
def submit_message():
    logger.info("Received POST request to /submit")
    data = request.get_json()
    if not data or 'message' not in data or 'alias' not in data:
        logger.error("Invalid input: missing required fields")
        return jsonify({'error': 'Invalid input'}), 400

    message = {
        'alias': data['alias'],
        'message': data['message']
    }
    logger.info(f"Processing message from {message['alias']}")

    try:
        publish_message(str(message))
        logger.info("Message successfully processed and published")
        return jsonify({'status': 'Message received'}), 200
    except Exception as e:
        logger.error(f"Error publishing message: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting API service")
    app.run(host='0.0.0.0', port=5000)
