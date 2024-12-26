import logging

def setup_logging():
    logging.basicConfig(filename='banking_system.log', level=logging.INFO)
    logging.info('Logging initialized.')

def log_transaction(action, details):
    logging.info(f'{action}: {details}')
