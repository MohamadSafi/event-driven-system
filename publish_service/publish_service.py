import pika
import os
import ast
import smtplib
from email.mime.text import MIMEText

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
INCOMING_QUEUE = 'final_messages'

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'your_email@example.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_password')
RECIPIENTS = os.environ.get('RECIPIENTS', 'recipient1@example.com,recipient2@example.com').split(',')

def send_email(alias, message_text):
    msg = MIMEText(f"From user: {alias}\nMessage: {message_text}")
    msg['Subject'] = 'New Message'
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(RECIPIENTS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())

def callback(ch, method, properties, body):
    message = ast.literal_eval(body.decode())
    alias = message.get('alias', '')
    text = message.get('message', '')
    try:
        send_email(alias, text)
        print(f"Email sent for message: {text}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

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
