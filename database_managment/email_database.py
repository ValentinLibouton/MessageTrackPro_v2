import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import time
from datetime import timedelta


class EmailDatabase:
    def __init__(self, db_name='database.db'):
        self._db_name = db_name
        self._create_tables()

        self.buffer = {
            'contacts': {},  # {(first_name, last_name): id}
            'email_addresses': {},  # {address: id}
            'aliases': {},  # {alias: id}
            'email_ids': set()  # set(id_1, id_2,...)
        }

    def _create_tables(self):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT)'''

        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Alias (
            id INTEGER PRIMARY KEY,
            alias TEXT)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts_Alias(
            contact_id INTEGER,
            alias_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contacts(id),
            FOREIGN KEY(alias_id) REFERENCES Alias(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS EmailAddresses(
            id INTEGER PRIMARY KEY,
            email_address TEXT UNIQUE)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts_EmailAddresses(
            contact_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contacts(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Emails (
            id TEXT PRIMARY KEY,
            filepath TEXT,
            filename TEXT,
            from_id INTEGER,
            subject TEXT,
            date TEXT,
            date_iso8601 TEXT,
            body TEXT,
            FOREIGN KEY(from_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_To(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Cc(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Bcc(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Attachments(
            id TEXT PRIMARY KEY,
            filename TEXT,
            content BLOB)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Attachments(
            email_id TEXT,
            attachment_id TEXT,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(attachment_id) REFERENCES Attachments(id))'''
        )

        conn.commit()
        conn.close()

    def get_buffered_data(self, buffer_name, data):
        if buffer_name not in self.buffer:
            print(f"Data type {buffer_name} not found in buffer.")
            return None
        elif isinstance(self.buffer[buffer_name], dict):
            value = self.buffer[buffer_name][data]
            if value is not None:
                print(f"Get buffered data for {buffer_name}: tuple({data},{value})")
                return data, value

        elif isinstance(self.buffer[buffer_name], set):
            if data in self.buffer[buffer_name]:
                return data

    def get_buffered_datas(self, buffer_name, data):
        """
        :data_type: (str): Le type de données, par exemple 'email_addresses'.
        :keys: (collection of str): Les clés à rechercher dans le sous-dictionnaire (peut être une liste ou un set).
        :return: Un dictionnaire contenant les paires clé-valeur pour les clés trouvées.
        """

        if buffer_name not in self.buffer:
            print(f"Data type {buffer_name} not found in buffer.")
            return None
        elif isinstance(self.buffer[buffer_name], dict):
            buffer_dict = {}
            for key in data:
                if key in self.buffer[buffer_name]:
                    value = self.buffer[buffer_name][key]
                    if value is not None:
                        buffer_dict[key] = value
            print(f"Get buffered data for {buffer_name}: dict({buffer_dict})")
            return buffer_dict

        elif isinstance(self.buffer[buffer_name], set):
            buffer_set = self.buffer[buffer_name] & set(data)
            print(f"Get buffered data for {buffer_name}: set({buffer_set})")
            return buffer_set

    def buffering(self, buffer_name, data):
        if isinstance(data, dict):
            if buffer_name not in self.buffer:
                self.buffer[buffer_name] = {}

        elif isinstance(data, set):
            if buffer_name not in self.buffer:
                self.buffer[buffer_name] = set()
        print(f"Buffering {buffer_name}: {data}")
        self.buffer[buffer_name].update(data)



    def select(self, table: str, columns: list, where_col: str, values_list: list):
        query = f"""SELECT {', '.join(columns)} FROM {table} WHERE {where_col} IN {', '.join('?' for _ in values_list)}"""
        conn = sqlite3.connect(self._db_name)
        try:
            c = conn.cursor()
            c.execute(query, values_list)
            result = c.fetchall()
            return result
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def select_with_conditions(self, table: str, columns: list, where_cols: list, values_list: list):
        results = []
        conn = sqlite3.connect(self._db_name)
        try:
            c = conn.cursor()
            for values in values_list:
                conditions = ' AND '.join(f"{col} = ?" for col in where_cols)
                query = f"""SELECT {', '.join(columns)} FROM {table} WHERE {conditions}"""
                c.execute(query, values)
                result = c.fetchall()
                results.extend(result)
            return results
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def insert_many(self, table: str, columns: list, values_list: list):
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        insert_query = f"""INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"""
        select_query = f"""SELECT id, {columns_str} FROM {table} WHERE ({columns_str}) IN ({', '.join('?' for _ in values_list)})"""

        conn = sqlite3.connect(self._db_name)
        try:
            c = conn.cursor()
            c.executemany(insert_query, values_list)
            conn.commit()

            # Prepare a flat list of values for the SELECT query
            flat_values = [item for sublist in values_list for item in sublist]
            c.execute(select_query, flat_values)
            inserted_rows = c.fetchall()

            return inserted_rows
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()



    # Todo ############################################################################################################
    def insert_email_addresses(self, emails_addr):
        """
        Args:
            email_addr: list(email)
        Returns:
        """

        email_addr_set = set(emails_addr)
        print(f"Email addresses to insert: {email_addr_set}")

        buffered_data = self.get_buffered_datas('email_addresses', email_addr_set)
        if buffered_data is None:
            buffered_data = {}
        print(f"Buffered data: {buffered_data}")

        addresses_not_in_buffer = email_addr_set - set(buffered_data.keys())
        print(f"Addresses not in buffer: {addresses_not_in_buffer}")

        if addresses_not_in_buffer:
            addresses_not_in_buffer_tuples = [(address,) for address in addresses_not_in_buffer]
            inserted_data_in_db = self.insert_many(table='EmailAddresses', columns=['email_address'],
                                                   values_list=list(addresses_not_in_buffer_tuples))
            print(f"Inserted data in DB: {inserted_data_in_db}")

            inserted_data_in_db_dict = {email: id for id, email in inserted_data_in_db}
            print(f"Inserted data in DB dict: {inserted_data_in_db_dict}")

            self.buffering('email_addresses', inserted_data_in_db_dict)

            buffered_data.update(inserted_data_in_db_dict)

            ids = [buffered_data[address] for address in emails_addr]
            print(f"Returning IDs: {ids}")
            return ids
        return []

    def process_insertion(self, data, buffer_name):
        data_set = set(data)
        print(f"Data to insert: {data_set}")

        buffered_data = self.get_buffered_datas(buffer_name=buffer_name, data=data_set)




class EmailLoader:
    def __init__(self, emails: list, db_name='database.db'):
        self.db = EmailDatabase(db_name)
        self._time_dict = {}
        self._emails = emails
        self._load_emails_into_db(emails=self._emails)

    def _load_email_into_db(self, email):
        from_email = email['from_email']
        from_name = email['from_name']
        from_email_id = self.db.insert_email_addresses(emails_addr=[from_email])[0]
        contact_alias_id = self.db.insert_aliases(alias=from_name)

        email_data = (
        email['id'], email['filepath'], email['filename'], from_email_id, email['subject'], str(email['date_obj']),
        str(email['date_iso8601']), email['body'])
        email_id = self.db.insert_email(email_data)

        if email['to_emails']:
            to_ids = self.db.insert_email_addresses(email['to_emails'])
            if to_ids is not None:
                self.db.link_recipients([(email_id, email_address_id) for email_address_id in to_ids])

        if email['cc_emails']:
            cc_ids = self.db.insert_email_addresses(email['cc_emails'])
            if cc_ids is not None:
                self.db.link_ccs([(email_id, email_address_id) for email_address_id in cc_ids])

        if email['bcc_emails']:
            bcc_ids = self.db.insert_email_addresses(email['bcc_emails'])
            if bcc_ids is not None:
                self.db.link_bccs([(email_id, email_address_id) for email_address_id in bcc_ids])

        if email['attachments']:
            #attachments = [(att['id'], att['filename'], att['content']) for att in email['attachments']]
            attachment_ids = self.db.insert_attachments(email['attachments'])

            self.db.link_attachments_to_email(email_id, attachment_ids)

    def _load_emails_into_db(self, emails, multi_processing=False):
        start_time = time.time()
        # ToDo: Multiprocessing does not save db insertion time!
        if multi_processing:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self._load_email_into_db, email) for email in emails]
                for future in tqdm(as_completed(futures), total=len(futures), desc="Load emails into db"):
                    future.result()
        else:
            for email in tqdm(emails, desc="Load emails into db"):
                self._load_email_into_db(email)
        end_time = time.time()
        self._time_dict['Load emails into db'] = end_time - start_time

    @property
    def log_execution_time(self):
        if self._time_dict:
            for text, seconds in self._time_dict.items():
                elapsed_time = timedelta(seconds=seconds)
                hours, remainder = divmod(elapsed_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if elapsed_time.days > 0:
                    print(
                        f"{text}: {elapsed_time.days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
                elif hours > 0:
                    print(f"{text}: {hours} hours, {minutes} minutes, {seconds} seconds")
                elif minutes > 0:
                    print(f"{text}: {minutes} minutes, {seconds} seconds")
                else:
                    print(f"{text}: {seconds} seconds")
