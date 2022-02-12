from smtplib import SMTP
import email
from other import custom_errors, loger_setup, rabbit_manipulation, config_loader, parse_message


class EmailSender:
    def __init__(self, config: dict):
        # TODO: Error handling
        try:
            self.config = config_loader.SMTPClientConfiguration(config)
            self.rabbit_object = rabbit_manipulation.RabbitObject(config)
            self.message = parse_message.Message()
        except:
            pass

        self.smtp_sender = SMTP("localhost", self.config.egress_port)


    def start_working(self) -> None:
        self.rabbit_object.verdict_receive(self.callback())

    def callback(self, ch, method, properties, body) -> None:
        self.message.parse_message(body)
        filename, analysis, payload, verdict = self.message.get_decoded_message()
        if verdict == custom_types.VERDICT.SUSPICIOUS or verdict == custom_types.VERDICT.MALICIOUS:
            self.quaranteine_mail(filename)
        elif verdict == custom_types.VERDICT.MANUAL:
            self.need_manual_review(filename)
        elif verdict == custom_types.VERDICT.GOODWARE:
            self.send_mail(filename)
        else:
            logging.error("Error with verdict entry!")

    def send_mail(self, hash: str) -> None:
        mail = email.parser.BytesParser()
        mail_path = self.config.email_path + hash
        fh = open(mail_path, "r")
        mail.parse(fh)

        # TODO: need to parse and set mail_from, mail_to
        try:
            self.smtp_sender.sendmail(mail_from, mail_to, body)
            file_handling.rm_file(mail_path)
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

    def quaranteine_mail(self, hash: str) -> None:
        src = self.config.email_path + hash
        dst = self.config.quarantine_path + hash
        file_manipulation.move_file(dst, src)

    def need_manual_review(self, hash: str) -> None:
        src = self.config.email_path + hash
        dst = self.config.manual_path + hash
        file_manipulation.move_file(dst, src)

if __init__ == "__main__":
    config = config_loader.load_config()
    mail_client = EmailSender(config)
    try:
        mail_client.