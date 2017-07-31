from threading import Thread
from flask import current_app, render_template
from flask_mail import Mail, Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['AAAS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['AAAS_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_email_simple(to, subject, body=""):
    app = current_app._get_current_object()

    mail = Mail(app)

    print("sending message using server "+app.config["MAIL_SERVER"])

    msg = Message(subject,
                  sender=app.config['AAAS_MAIL_SENDER'],
                  recipients=[to])
    msg.body = body
    msg.html = body

    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return