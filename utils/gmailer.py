import yagmail

user = yagmail.SMTP(user='pythonemail1998@gmail.com', password='pwbyekrozdhzkqrz')

def send_email(recipient, emg_subject, emg_content, attachments=None):
    contents = [emg_content]
    if attachments:
        for attachment in attachments:
            contents.append(yagmail.inline(attachment))

    user.send(to=recipient,
              subject=emg_subject,
              contents=contents)
