import pika
import os
import ast

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
INCOMING_QUEUE = 'filtered_messages'
OUTGOING_QUEUE = 'final_messages'

def callback(ch, method, properties, body):
    message = ast.literal_eval(body.decode())
    text = message.get('message', '')
    message['message'] = text.upper()
    publish_message(str(message))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def publish_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=OUTGOING_QUEUE, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=OUTGOING_QUEUE,
        body=message
    )
    connection.close()

def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=INCOMING_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=INCOMING_QUEUE, on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    consume_messages()
