def send_email(user, passwd, recipient, subject, body):
    import smtplib
    from email.mime.text import MIMEText

    gmail_user = user
    gmail_pwd = passwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # prepare actual message
    message = """From: {}\nTo: {}\nSubject: {}\n\n{}
        """.format(FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the email')
    except Exception as e:
        print('failed to send email')
        raise e

if __name__ == '__main__':
    pass
