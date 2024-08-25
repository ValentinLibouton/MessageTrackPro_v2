import logging
from utils.logger_manager import LoggerManager

log_manager = LoggerManager()


log_email_aggregator = log_manager.get_logger(logger_name='email-aggregator', log_file='logs/email_aggregator.log')
log_email_database = log_manager.get_logger(logger_name='email_database', log_file='logs/email_database.log')
log_file_retriever = log_manager.get_logger(logger_name='file_retriever', log_file='logs/file_retriever.log')
log_email_parser = log_manager.get_logger(logger_name='email_parser', log_file='logs/email_parser.log')
log_mbox_extractor = log_manager.get_logger(logger_name='mbox_extractor', log_file='logs/mbox_extractor.log')