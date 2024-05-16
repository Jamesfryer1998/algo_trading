import yagmail

user = yagmail.SMTP(user='pythonemail1998@gmail.com', password='pwbyekrozdhzkqrz')

def send_email(recipient, emg_subject, emg_content):
    user.send(to=recipient,
            subject = emg_subject, 
            contents = emg_content)
