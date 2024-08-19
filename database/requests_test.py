from database.database_retriever import DatabaseRetriever

db_retriever = DatabaseRetriever(words=['emploi', 'travail'],
                                 words_localization=['everywhere'],
                                 word_operator="OR")
db_retriever.join().where()
#query = db_retriever.build_query()
print(db_retriever.show_query())
