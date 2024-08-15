from database.database_retriever import DatabaseRetriever

dbr = DatabaseRetriever()
results = dbr.simple_word_search(table='Emails', columns=['subject', 'body'], word='squid')
print(f"Simple word search: {len(results)} résultats.")
print(f"Id's: {results}")


results = dbr.all_words_search(table='Emails', columns=['subject', 'body'], words=['Valentin', 'Libouton'])
print(f"All words search: {len(results)} résultats.")
print(f"Id's: {results}")

results = dbr.any_words_search(table='Emails', columns=['subject', 'body'], words=['Valentin', 'Libouton'])
print(f"Any words search: {len(results)} résultats.")
print(f"Id's: {results}")