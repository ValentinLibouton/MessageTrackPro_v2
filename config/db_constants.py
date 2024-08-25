class DBConstants:
    db_name: str = 'database.db'
    sql_name: str = 'database/database.sql'

    # Tables names
    CONTACTS_TABLE: str = 'Contacts'
    ALIAS_TABLE: str = 'Alias'
    EMAIL_ADDRESSES_TABLE: str = 'EmailAddresses'
    EMAILS_TABLE: str = 'Emails'
    DATE_TABLE: str = 'Date'
    TIMESTAMP_TABLE: str = 'Timestamp'
    ATTACHMENTS_TABLE: str = 'Attachments'


    # Columns
    CONTACTS_COLUMNS: list[str] = ['first_name', 'last_name']
    ALIAS_COLUMNS: list[str] = ['alias']
    EMAIL_ADDRESSES_COLUMNS: list[str] = ['email_address']
    EMAILS_COLUMNS: list[str] = ['id', 'filepath', 'filename', 'subject', 'body']
    DATE_COLUMNS: list[str] = ['date']
    TIMESTAMP_COLUMNS: list[str] = ['timestamp']
    ATTACHMENTS_COLUMNS: list[str] = ['id', 'filename', 'content', 'extracted_text']

    KEYWORD_SEARCH_FIELDS: list[str] = ['everywhere', 'contact', 'alias', 'address', 'subject', 'body',
                                        'attachment_name', 'attachment']