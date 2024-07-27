import yagmail

user = yagmail.SMTP(user='pythonemail1998@gmail.com', password='pwbyekrozdhzkqrz')

def send_email(recipient, emg_subject, emg_content, image_path=None):
    contents = [emg_content]
    if image_path:
        contents.append(yagmail.inline(image_path))
    
    user.send(to=recipient,
              subject=emg_subject, 
              contents=contents)
