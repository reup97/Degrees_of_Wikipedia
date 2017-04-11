def send_email(user, passwd, recipient, subject, body):
    ''' a function to send email.
    Time complexity: O(1) in general, or
                     O(n) in terms of the size of message to be send
                          or size of recipient list. 
    Arguments:
        user: a string of email address that will send emails from.
        passwd: a string of password of the user.
        recipient: a list of recepients or only one recepient.
        subject: a string that contains the subject of the email.
        body: a string that contains the content of the email.
    Raises Exception if failed to send email.
    '''
    import smtplib

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
