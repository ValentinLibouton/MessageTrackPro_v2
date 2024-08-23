from utils.logger_manager import LoggerManager
log_manager = LoggerManager(log_file='application.log')
log_email_aggregator = log_manager.get_logger('email_aggregator')
log_email_database = log_manager.get_logger('email_database')
log_file_retriever = log_manager.get_logger('file_retriever')
log_email_parser = log_manager.get_logger('email_parser')
log_mbox_extractor = log_manager.get_logger('mbox_extractor')