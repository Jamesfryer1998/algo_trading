import yagmail
from utils.json_tools import *


def send_email(emg_subject, emg_content, attachments=None):
    username = load_json("utils/secrets.json")['gmail_username']
    password = load_json("utils/secrets.json")['gmail_password']
    send_to = load_json("utils/secrets.json")['send_to']
    user = yagmail.SMTP(user=username, password=password)
    contents = [yagmail.inline(emg_content)]
    
    if attachments:
        for attachment in attachments:
            contents.append(yagmail.inline(attachment))

    user.send(to=send_to,
              subject=emg_subject,
              contents=contents)
    
    print(f"Email sent successfully to {send_to}.")
