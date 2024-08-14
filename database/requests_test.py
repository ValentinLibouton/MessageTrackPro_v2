from database.database_retriever import DatabaseRetriever

dbr = DatabaseRetriever()
results = dbr.simple_word_search(table='Emails', columns=['subject', 'body'], word='Squid')
print(results)