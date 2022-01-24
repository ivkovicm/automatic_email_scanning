from smtplib import SMTP


class EmailSender:
    def __init__(self, config: MailConfigurations):
        self.config = config
        self.smtp_sender = SMTP("localhost", self.config.egress_port)

    def send_mail(self, mail_from, mail_to, body):
        try:
            self.smtp_sender.sendmail(mail_from, mail_to, body)
        except smtplib.SMTPException:
            logging.error('Error "Exception SMTPException" while injecting mail into postfix!')
            pass
        except smtplib.SMTPServerDisconnected:
            logging.error('Error "Exception SMTPServerDisconnected" while injecting mail into postfix!')
            pass
        except smtplib.SMTPResponseException:
            logging.error('Error "Exception SMTPResponseException" while injecting mail into postfix!')
            pass
        except smtplib.SMTPSenderRefused:
            logging.error('Error "Exception SMTPSenderRefused" while injecting mail into postfix!')
            pass
        except smtplib.SMTPRecipientsRefused:
            logging.error('Error "Exception SMTPRecipientsRefused" while injecting mail into postfix!')
            pass
        except smtplib.SMTPDataError:
            logging.error('Error "Exception SMTPDataError" while injecting mail into postfix!')
            pass
        except smtplib.SMTPConnectError:
            logging.error('Error "Exception SMTPConnectError" while injecting mail into postfix!')
            pass
        except smtplib.SMTPHeloError:
            logging.error('Error "Exception SMTPHeloError" while injecting mail into postfix!')
            pass
        except smtplib.SMTPAuthenticationError:
            logging.error('Error "Exception SMTPAuthenticationError" while injecting mail into postfix!')
            pass
        except:
            logging.error('Error "Exception Undefined exception" while injecting mail into postfix!')
            logging.error(traceback.format_exc())