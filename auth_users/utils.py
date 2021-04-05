import threading
from django.core.mail import EmailMessage


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send()


class EmailMessageThread(threading.Thread):
    def __init__(self, subject, content, recipient_list, sender):
        self.subject = subject
        self.recipient_list = recipient_list
        self.content = content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.content, self.sender, self.recipient_list)
        msg.send()


def send_html_mail(subject, html_content, recipient_list, sender):
    EmailThread(subject, html_content, recipient_list, sender).start()


def send_text_mail(subject, content, recipient_list, sender):
    EmailMessageThread(subject, content, recipient_list, sender).start()