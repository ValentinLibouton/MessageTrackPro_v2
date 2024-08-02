CREATE TABLE IF NOT EXISTS Contacts (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE IF NOT EXISTS Alias (
    id INTEGER PRIMARY KEY,
    alias TEXT
);

CREATE TABLE IF NOT EXISTS Contacts_Alias(
    contact_id INTEGER,
    alias_id INTEGER,
    FOREIGN KEY(contact_id) REFERENCES Contacts(id),
    FOREIGN KEY(alias_id) REFERENCES Alias(id)
);

CREATE TABLE IF NOT EXISTS EmailAddresses(
    id INTEGER PRIMARY KEY,
    email_address TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Contacts_EmailAddresses(
    contact_id INTEGER,
    email_address_id INTEGER,
    FOREIGN KEY(contact_id) REFERENCES Contacts(id),
    FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id)
);

CREATE TABLE IF NOT EXISTS Emails (
    id TEXT PRIMARY KEY,
    filepath TEXT,
    filename TEXT,
    from_id INTEGER,
    subject TEXT,
    date TEXT,
    date_iso8601 TEXT,
    body TEXT,
    FOREIGN KEY(from_id) REFERENCES EmailAddresses(id)
);

CREATE TABLE IF NOT EXISTS Email_To(
    email_id TEXT,
    email_address_id INTEGER,
    FOREIGN KEY(email_id) REFERENCES Emails(id),
    FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id)
);

CREATE TABLE IF NOT EXISTS Email_Cc(
    email_id TEXT,
    email_address_id INTEGER,
    FOREIGN KEY(email_id) REFERENCES Emails(id),
    FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id)
);

CREATE TABLE IF NOT EXISTS Email_Bcc(
    email_id TEXT,
    email_address_id INTEGER,
    FOREIGN KEY(email_id) REFERENCES Emails(id),
    FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id)
);

CREATE TABLE IF NOT EXISTS Attachments(
    id TEXT PRIMARY KEY,
    filename TEXT,
    content BLOB
);

CREATE TABLE IF NOT EXISTS Email_Attachments(
    email_id TEXT,
    attachment_id TEXT,
    FOREIGN KEY(email_id) REFERENCES Emails(id),
    FOREIGN KEY(attachment_id) REFERENCES Attachments(id)
);
