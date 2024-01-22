import spacy
from text_to_num import text2num

nlp = spacy.load("es_core_news_lg")

def lemmatize(input):
    lemmas = nlp(input)
    empty_list = []
    for token in lemmas:
        empty_list.append(token.lemma_.lower())
    final_string = ' '.join(map(str, empty_list))
    return final_string

def is_word_number(input_text):
    exceptions = ["un","una","unos","unas"]
    black_list = ["primero", "primera", "tercero","cuarto","quinto","sexto","septimo","octavo","noveno","decimo", "décimo", "séptimo", "vigésimo", "vigesimo", "trigésimo", "trigesimo", "documento", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "uno", "igual", "menor"]
    tokens = nlp(input_text)
    result = False
    for token in tokens:
        if token.text.lower() not in exceptions:
            try:
                numeric_value = text2num(token.text.lower(), 'es')
                result = result or True  # Update result to True if the current token is a valid number
            except ValueError:
                result = result or False  # Update result to False if the current token is not a valid number

        if token.text.lower() in exceptions:
            return False
        if token.text.lower() in black_list:
            return True

    return result

#if __name__ == "__main__":
#    print(is_word_number(input))