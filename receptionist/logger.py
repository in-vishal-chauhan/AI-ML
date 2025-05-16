import logging

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("webhook.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
