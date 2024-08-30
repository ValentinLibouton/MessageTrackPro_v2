class DatabaseRetrieverConstants:
    """For DatabaseRetriever class"""
    WORDS_LOCALIZATION: str = 'words_localization'
    KEYWORD_SEARCH_FIELDS: list[str] = ['everywhere', 'contact', 'alias', 'address', 'subject', 'body',
                                        'attachment_name', 'attachment']
    EVERYWHERE_LOCALISATION: str = 'everywhere'
    DEFAULT_WORD_OPERATOR: str = 'OR'
    START_DATE: str = 'start_date'
    END_DATE: str = 'end_date'

class DBConstants:
    DB_NAME: str = 'database.db'
    SQL_NAME: str = 'database/database.sql'




    # CONTACTS
    CONTACTS_TABLE: str = 'Contacts'
    CONTACTS_COLUMNS: list[str] = ['first_name', 'last_name']

    # Alias
    ALIAS_TABLE: str = 'Alias'
    ALIAS_COLUMNS: list[str] = ['alias']

    # Contacts_Alias
    CONTACT_ALIAS_TABLE: str = 'Contact_Alias'
    CONTACT_ALIAS_COLUMNS: list['contact_id', 'alias_id']

    # EmailAddresses
    EMAIL_ADDRESSES_TABLE: str = 'EmailAddresses'
    EMAIL_ADDRESSES_COLUMNS: list[str] = ['email_address']

    # Contacts_EmailAddresses
    CONTACT_EMAIL_ADDRESSES_TABLE: str = 'Contacts_EmailAddresses'
    CONTACT_EMAIL_ADDRESSES_COLUMNS: list[str] = ['contact_id', 'email_address_id']

    # Emails
    EMAILS_TABLE: str = 'Emails'
    EMAILS_COLUMNS: list[str] = ['id', 'filepath', 'filename', 'subject', 'body']

    # Date
    DATE_TABLE: str = 'Date'
    DATE_COLUMNS: list[str] = ['date']

    # Email_Date
    EMAIL_DATE_TABLE: str = 'Email_Date'
    EMAIL_DATE_COLUMNS: list[str] = ['email_id', 'date_id']

    # Timestamp
    TIMESTAMP_TABLE: str = 'Timestamp'
    TIMESTAMP_COLUMNS: list[str] = ['timestamp']

    # Email_Timestamp
    EMAIL_TIMESTAMP_TABLE: str = 'Email_Timestamp'
    EMAIL_TIMESTAMP_COLUMNS: list[str] = ['email_id', 'timestamp_id']

    # Email_From
    EMAIL_FROM_TABLE: str = 'Email_From'
    EMAIL_FROM_COLUMNS: list[str] = ['email_id', 'email_address_id']

    # Email_To
    EMAIL_TO_TABLE: str = 'Email_To'
    EMAIL_TO_COLUMNS: list[str] = ['email_id', 'email_address_id']

    # Email_Cc
    EMAIL_CC_TABLE: str = 'Email_Cc'
    EMAIL_CC_COLUMNS: list[str] = ['email_id', 'email_address_id']

    # Email_Bcc
    EMAIL_BCC_TABLE: str = 'Email_Bcc'
    EMAIL_BCC_COLUMNS: list[str] = ['email_id', 'email_address_id']

    # Attachments
    ATTACHMENTS_TABLE: str = 'Attachments'
    ATTACHMENTS_COLUMNS: list[str] = ['id', 'filename', 'content', 'extracted_text']

    # Email_Attachments
    EMAIL_ATTACHMENTS_TABLE: str = 'Email_Attachments'
    EMAIL_ATTACHMENTS_COLUMNS: list[str] = ['email_id', 'attachment_id']