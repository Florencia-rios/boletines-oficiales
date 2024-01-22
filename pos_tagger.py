import spacy

nlp = spacy.load("es_core_news_lg")

def pos_tag(input):
    doc = nlp(input)
    for token in doc:
        if token.pos_ == 'VERB':
            return True
    return False

#if __name__ == "__main__":
#    print(pos_tag(input))