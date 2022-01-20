from base64 import b64decode


class Message:
    def __init__(self, mssg):
        self.filename = "NO_FILENAME"
        self.analysis = "NO_ANALYSIS"
        self.payload = "NO_PAYLOAD"
        self.parse_body(mssg)

    def parse_body(self, body):
        try:
            body_arguments = body.decode("UTF-8").split("|")
            self.filename = body_arguments[0]
            self.analysis = body_arguments[1]
            self.payload = b64decode(body_arguments[2].encode())
        except:
            raise MessageParsingError(self.filename)
