import logging

debug_logger = logging.getLogger('debug')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('db.log')
debug_logger.addHandler(debug_handler)

info_logger = logging.getLogger('info')
info_logger.setLevel(logging.INFO)
info_handler = logging.FileHandler('db.log')
info_logger.addHandler(info_handler)