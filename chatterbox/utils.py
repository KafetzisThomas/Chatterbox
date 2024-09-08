from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_ping_notification(current_user, mentioned_user, message):
    subject = f"{current_user}: Sent you a new message!"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [mentioned_user.email]

    html_message = render_to_string(
        "email_templates/new_message.html",
        {"current_user": current_user, "message": message},
    )

    send_mail(subject, None, email_from, recipient_list, html_message=html_message)
