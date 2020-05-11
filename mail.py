from flask import current_app, render_template
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import re

mail = Mail()


def send_confirm_mail(to, url, salt):
    token = generate_confirmation_token(to, salt)
    # confirm_url = url_for('confirm', token=token, _external=True)
    confirm_url = url + token
    html = render_template('confirm_email.html', confirm_url=confirm_url)
    msg = Message("Please confirm your email",
                  recipients=[to],
                  html=html,
                  sender=current_app.config['CONFIRM_MAIL_SENDER'])
    mail.send(msg)


# def email_is_valid(email):
#     pattern = re.compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
#     return pattern.fullmatch(email)


def generate_confirmation_token(email, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SERIALIZER_SECRET_KEY'])
    return serializer.dumps(email, salt)


def confirm_token(token, salt, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SERIALIZER_SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=salt,
            max_age=expiration
        )
    except:
        return False
    return email