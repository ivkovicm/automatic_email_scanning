from base64 import b64decode, b64encode


class Message:
    def __init__(self):
        self.filename = "NO_FILENAME"
        self.analysis = "NO_ANALYSIS"
        self.payload = "NO_PAYLOAD"
        self.encoded_message = ""

    def parse_message(self, body) -> None:
        try:
            body_arguments = body.decode("UTF-8").split("|")
            self.filename = body_arguments[0]
            self.analysis = body_arguments[1]
            self.payload = b64decode(body_arguments[2].encode())
        except:
            logging.error("Error while decoding message!")
            raise MessageParsingError(self.filename)

    def prepare_message(self, filename, analysis, payload) -> None:
        try:
            self.filename = filename
            self.analysis = analysis
            self.payload = payload
            self.encoded_message = b64encode(self.filename + "|" + self.analysis + "|" + self.payload)
        except:
            logging.error("Error while preparing message for sending!")
            raise custom_errors.ErrorPreparingMessage

    def get_encoded_message(self) -> str:
        if self.encoded_message == "":
            logging.warning("Message isn't prepared for sending")
            raise custom_errors.MessageNotPrepared
        else:
            return self.encoded_message

    def get_decoded_message(self) -> tuple:
        return self.filename, self.analysis, self.payload
