class SQLRequest:
    @staticmethod
    def insert_contact():
        return "INSERT OR IGNORE Contacts (first_name, last_name) VALUES (?, ?)"

    @staticmethod
    def select_contact_id():
        return "SELECT id FROM Contacts WHERE first_name = ? and last_name = ? "

    @staticmethod
    def insert_alias():
        return "INSERT OR IGNORE Alias (alias) VALUES (?)"

    @staticmethod
    def select_alias_id():
        return "SELECT id FROM Alias WHERE alias = ?"

    @staticmethod
    def link_contact_id_to_alias_id():
        return "INSERT OR IGNORE Contacts_Alias (contact_id, alias_id) VALUES (?, ?)"

    @staticmethod
    def insert_email_address():
        return "INSERT OR IGNORE EmailAddresses (email_address) VALUES (?)"

    @staticmethod
    def select_email_address_id():
        return "SELECT id FROM EmailAddresses WHERE email_address = ?"

    @staticmethod
    def link_contact_id_to_email_address_id():
        return "INSERT OR IGNORE Contacts_EmailAddresses (contact_id, email_address_id) VALUES (?, ?)"

    @staticmethod
    def insert_email():
        return "INSERT OR IGNORE Email (id, filepath, filename, subject, body) VALUES (?, ?, ?, ?, ?)"

    @staticmethod
    def select_email_id():
        return "SELECT id FROM Email WHERE id = ?"

    @staticmethod
    def insert_date():
        return "INSERT OR IGNORE Date (date) VALUES (?)"

    @staticmethod
    def select_date_id():
        return "SELECT id FROM Date WHERE date = ?"

    @staticmethod
    def link_date_id_to_email_id():
        return "INSERT OR IGNORE Email_Date (email_id, date_id) VALUES (?, ?)"

    @staticmethod
    def insert_timestamp():
        return "INSERT OR IGNORE Timestamp (timestamp) VALUES (?)"

    @staticmethod
    def select_timestamp_id():
        return "SELECT id FROM Timestamp WHERE timestamp = ?"

    @staticmethod
    def link_timestamp_id_to_email_id():
        return "INSERT OR IGNORE Email_Timestamp (email_id, timestamp_id) VALUES (?, ?)"

    @staticmethod
    def link_from_email_address_id_to_email_id():
        return "INSERT OR IGNORE Email_From (email_id, email_address_id) VALUES (?, ?)"

    @staticmethod
    def link_to_email_address_id_to_email_id():
        return "INSERT OR IGNORE Email_To (email_id, email_address_id) VALUES (?, ?)"

    @staticmethod
    def link_cc_email_address_id_to_email_id():
        return "INSERT OR IGNORE Email_Cc (email_id, email_address_id) VALUES (?, ?)"

    @staticmethod
    def link_bcc_email_address_id_to_email_id():
        return "INSERT OR IGNORE Email_Bcc (email_id, email_address_id) VALUES (?, ?)"

    @staticmethod
    def insert_attachment():
        return "INSERT OR IGNORE Attachments (id, filename, content) VALUES (?, ?, ?)"

    @staticmethod
    def link_attachment_id_to_email_id():
        return "INSERT OR IGNORE Email_Attachments (email_id, attachment_id) VALUES (?, ?)"