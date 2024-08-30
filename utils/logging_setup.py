import logging

from config.log_constants import LogConstants
from utils.logger_manager import LoggerManager
from utils.string_cleaner import StringCleaner

sc = StringCleaner().create_directory(dir_path=LogConstants.LOG_PATH)
log_manager_info = LoggerManager(log_level=logging.INFO)
log_manager_debug = LoggerManager(log_level=logging.DEBUG)
log_manager_error = LoggerManager(log_level=logging.ERROR)
log_manager_warning = LoggerManager(log_level=logging.WARNING)

log_email_aggregator_info = log_manager_info.get_logger(logger_name='email-aggregator', log_file='logs/email_aggregator.log')
log_email_aggregator_debug = log_manager_debug.get_logger(logger_name='email-aggregator', log_file='logs/email_aggregator.log')
log_email_aggregator_error = log_manager_error.get_logger(logger_name='email-aggregator', log_file='logs/email_aggregator.log')

log_email_database = log_manager_info.get_logger(logger_name='email_database', log_file='logs/email_database.log')
log_file_retriever = log_manager_info.get_logger(logger_name='file_retriever', log_file='logs/file_retriever.log')

log_email_parser_info = log_manager_info.get_logger(logger_name='email_parser', log_file='logs/email_parser.log')
log_email_parser_debug = log_manager_debug.get_logger(logger_name='email_parser', log_file='logs/email_parser.log')
log_email_parser_warning = log_manager_warning.get_logger(logger_name='email_parser', log_file='logs/email_parser.log')

log_mbox_extractor = log_manager_info.get_logger(logger_name='mbox_extractor', log_file='logs/mbox_extractor.log')
log_file_content_extractor = log_manager_info.get_logger(logger_name='file_content_extractor', log_file='logs/file_content_extractor.log')

