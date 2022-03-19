import app
from flask_mail import Mail, Message
from flask import current_app as app
from decouple import config



class MailService():
    def __init__(self):
        try:
            self.mail=Mail()
        except Exception as e:
            print(e)
            print("MailService: mail not configured")
            self.mail=None
    def send_mail(self,subject,recipient,body,attachment=None,html=None):
        try:
            msg=Message(subject,recipients=[recipient],body=body,
                        sender="abhi.sharma1114@gmail.com",charset='utf-8',
                        extra_headers={'Disposition-Notification-To':'abhi.sharma1114@gmail.com'}) # to send mail receipt to admin
            # send the path of the attachment that is to be sent
            if attachment:
                with app.open_resource(attachment) as fp:
                    msg.attach(attachment.split('/')[-1],'application/octet-stream', fp.read())
            if html:
                msg.html=html
            self.mail.send(msg)
        except Exception as e:
            print(e)
            print("MailService: mail not sent")
            return False
        return True   
