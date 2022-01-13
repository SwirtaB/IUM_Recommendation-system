import json


class Logger:
    """
    Logger class allows to store events (in .json form) to logging files.
    """
    def __init__(self, logging_fp):
        self.log_file = open(logging_fp, "a")

    def __del__(self):
        self.log_file.close()

    def log(self, json_data):
        self.log_file.write(json.dumps(json_data, indent=4) + '\n')
