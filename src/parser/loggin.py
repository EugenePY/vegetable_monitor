import logging

FORMAT = '%(asctime)-15s %(user)-8s %(message)s'
d = {"user": __name__ + ' Eugene'}
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
