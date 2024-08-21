from database.database_retriever import DatabaseRetriever

db_retriever = DatabaseRetriever(words=['juge'],
                                 words_localization=['attachment_name'],# 'address'],
                                 word_operator="OR",
                                 start_date="2018-10-17 00:00:00")

# Build the query with joins and where conditions
db_retriever.join().where()

# Show the query before executing it
query = db_retriever.show_query()
print("SQL Query:")
print(query)

# Execute the query and retrieve the IDs
ids = db_retriever.execute()

# Print the results
for i, id in enumerate(ids, start=1):
    print(f"ID{i}:\t{id[0]}")