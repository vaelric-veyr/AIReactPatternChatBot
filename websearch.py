import wikipedia

def web_search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except:
        return "No relevant information found."
    

print(wikipedia.summary("artificial intelligence", sentences=2))