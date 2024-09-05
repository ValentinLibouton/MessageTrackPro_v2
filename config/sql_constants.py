# sql_constants.py

# Table Names
TABLE_EMAILS = 'Emails'
TABLE_EMAIL_FROM = 'Email_From'
TABLE_EMAIL_TO = 'Email_To'
TABLE_EMAIL_CC = 'Email_Cc'
TABLE_EMAIL_BCC = 'Email_Bcc'
TABLE_EMAIL_TIMESTAMP = 'Email_Timestamp'
TABLE_EMAIL_ATTACHMENTS = 'Email_Attachments'
TABLE_EMAIL_ADDRESSES = 'EmailAddresses'
TABLE_TIMESTAMP = 'Timestamp'
TABLE_ATTACHMENTS = 'Attachments'
TABLE_CONTACTS_EMAIL_ADDRESSES = 'Contacts_EmailAddresses'
TABLE_CONTACTS = 'Contacts'
TABLE_IMAGE_FROM_CONTENT = 'ImageFromContent'
TABLE_CONTACTS_ALIAS = 'Contacts_Alias'
TABLE_ALIAS = 'Alias'

# Aliases for Tables in SQL Queries
ALIAS_EMAILS = 'e'
ALIAS_EMAIL_FROM = 'ef'
ALIAS_EMAIL_TO = 'et'
ALIAS_EMAIL_CC = 'ec'
ALIAS_EMAIL_BCC = 'eb'
ALIAS_EMAIL_TIMESTAMP = 'eti'
ALIAS_EMAIL_ATTACHMENTS = 'ea'
ALIAS_EMAIL_ADDRESSES_FROM = 'ea1'
ALIAS_EMAIL_ADDRESSES_TO = 'ea2'
ALIAS_EMAIL_ADDRESSES_CC = 'ea3'
ALIAS_EMAIL_ADDRESSES_BCC = 'ea4'
ALIAS_TIMESTAMP = 'ts'
ALIAS_ATTACHMENTS = 'a'
ALIAS_CONTACTS_EMAIL_ADDRESSES_FROM = 'cea1'
ALIAS_CONTACTS_EMAIL_ADDRESSES_TO = 'cea2'
ALIAS_CONTACTS_EMAIL_ADDRESSES_CC = 'cea3'
ALIAS_CONTACTS_EMAIL_ADDRESSES_BCC = 'cea4'
ALIAS_ATTACHMENTS_IMAGE_FROM_CONTENT = 'ai'
ALIAS_CONTACTS_FROM = 'c1'
ALIAS_CONTACTS_TO = 'c2'
ALIAS_CONTACTS_CC = 'c3'
ALIAS_CONTACTS_BCC = 'c4'
ALIAS_IMAGE_FROM_CONTENT = 'i'
ALIAS_CONTACTS_ALIAS_FROM = 'ca1'
ALIAS_CONTACTS_ALIAS_TO = 'ca2'
ALIAS_CONTACTS_ALIAS_CC = 'ca3'
ALIAS_CONTACTS_ALIAS_BCC = 'ca4'
ALIAS_ALIAS_FROM = 'a1'
ALIAS_ALIAS_TO = 'a2'
ALIAS_ALIAS_CC = 'a3'
ALIAS_ALIAS_BCC = 'a4'

# Table: Emails
E_ID = 'e.id'
E_FILEPATH = 'e.filepath'
E_FILENAME = 'e.filename'
E_SUBJECT = 'e.subject'
E_BODY = 'e.body'

# Table: Email_From
EF_EMAIL_ID ='ef.email_id'
EF_EMAIL_ADDRESS_ID ='ef.email_address_id'

# Table: Email_To
ET_EMAIL_ID ='et.email_id'
ET_EMAIL_ADDRESS_ID ='et.email_address_id'

# Table: Email_Cc
EC_EMAIL_ID ='ec.email_id'
EC_EMAIL_ADDRESS_ID ='ec.email_address_id'

# Table: Email_Bcc
EB_EMAIL_ID = 'eb.email_id'
EB_EMAIL_ADDRESS_ID = 'eb.email_address_id'

# Table: Email_Timestamp
ETI_EMAIL_ID = 'eti.email_id'
ETI_TIMESTAMP_ID = 'eti.timestamp_id'

# Table: Email_Attachments
EA_EMAIL_ID = 'ea.email_id'
EA_ATTACHMENT_ID = 'ea.attachment_id'

# Table: EmailAddresses (from)
EA1_ID = 'ea1.id'
EA1_EMAIL_ADDRESS = 'ea1.email_address'

# Table: EmailAddresses (to)
EA2_ID = 'ea2.id'
EA2_EMAIL_ADDRESS = 'ea2.email_address'

# Table: EmailAddresses (cc)
EA3_ID = 'ea3.id'
EA3_EMAIL_ADDRESS = 'ea3.email_address'

# Table: EmailAddresses (bcc)
EA4_ID = 'ea4.id'
EA4_EMAIL_ADDRESS = 'ea4.email_address'

# Table Timestamp
TS_ID = 'ts.id'
TS_TIMESTAMP = 'ts.timestamp'

# Table: Attachments
A_ID = 'a.id'
A_FILENAME = 'a.filename'
A_CONTENT = 'a.content'
A_EXTRACTED_TEXT = 'a.extracted_text'

# Table: Contacts_EmailAddresses (from)
CEA1_CONTACT_ID = 'cea1.contact_id'
CEA1_EMAIL_ADDRESS_ID = 'cea1.email_address_id'

# Table: Contacts_EmailAddresses (to)
CEA2_CONTACT_ID = 'cea2.contact_id'
CEA2_EMAIL_ADDRESS_ID = 'cea2.email_address_id'

# Table: Contacts_EmailAddresses (cc)
CEA3_CONTACT_ID = 'cea3.contact_id'
CEA3_EMAIL_ADDRESS_ID = 'cea3.email_address_id'

# Table: Contacts_EmailAddresses (bcc)
CEA4_CONTACT_ID = 'cea4.contact_id'
CEA4_EMAIL_ADDRESS_ID = 'cea4.email_address_id'

# Table: Contacts (from)
C1_ID = 'c1.id'
C1_FIRST_NAME = 'c1.first_name'
C1_LAST_NAME = 'c1.last_name'

# Table: Contacts (to)
C2_ID = 'c2.id'
C2_FIRST_NAME = 'c2.first_name'
C2_LAST_NAME = 'c2.last_name'

# Table: Contacts (cc)
C3_ID = 'c3.id'
C3_FIRST_NAME = 'c3.first_name'
C3_LAST_NAME = 'c3.last_name'

# Table: Contacts (bcc)
C4_ID = 'c4.id'
C4_FIRST_NAME = 'c4.first_name'
C4_LAST_NAME = 'c4.last_name'

# Table: ImageFromContent
I_ID = 'i.id'
I_IMAGE = 'i.image'
I_EXTRACTED_TEXT = 'i.extracted_text'

# Table: Contacts_Alias (from)
CA1_CONTACT_ID = 'ca1.contact_id'
CA1_ALIAS_ID = 'ca1.alias_id'

# Table: Contacts_Alias (to)
CA2_CONTACT_ID = 'ca2.contact_id'
CA2_ALIAS_ID = 'ca2.alias_id'

# Table: Contacts_Alias (cc)
CA3_CONTACT_ID = 'ca3.contact_id'
CA3_ALIAS_ID = 'ca3.alias_id'

# Table: Contacts_Alias (bcc)
CA4_CONTACT_ID = 'ca4.contact_id'
CA4_ALIAS_ID = 'ca4.alias_id'

# Table: Alias (from)
A1_ID = 'a1.id'
A1_ALIAS = 'a1.alias'

# Table: Alias (to)
A2_ID = 'a2.id'
A2_ALIAS = 'a2.alias'

# Table: Alias (cc)
A3_ID = 'a3.id'
A3_ALIAS = 'a3.alias'

# Table: Alias (bcc)
A4_ID = 'a4.id'
A4_ALIAS = 'a4.alias'


C_FIRST_NAME = [C1_FIRST_NAME, C2_FIRST_NAME, C3_FIRST_NAME, C4_FIRST_NAME]
C_LAST_NAME = [C1_LAST_NAME, C2_LAST_NAME, C3_LAST_NAME, C4_LAST_NAME]