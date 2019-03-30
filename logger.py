# -*- coding: utf-8 -*-
# filename: logger.py

import logging

class Logger():

  def __init__(self, file_name):
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG,
      # filename=file_name,
      format='%(asctime)s - %(levelname)s: %(message)s')

  def info(self, message):
    self.logger.info(message)

  def warning(self, message):
    self.logger.warning(message)

  def error(self, message):
    self.logger.error(message)

  def debug(self, message):
    self.logger.debug(message)

