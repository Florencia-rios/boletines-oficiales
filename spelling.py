from spellchecker import SpellChecker
input = "directores tituleres"

def spelling(input):
    empty_list = []
    input = input.split()
    spell = SpellChecker(language='es')

    for token in input:
        empty_list.append(spell.correction(token) if spell.correction(token) else token)
    final_string = ' '.join(map(str, empty_list))
    return final_string


if __name__ == "__main__":
    print(spelling(input))