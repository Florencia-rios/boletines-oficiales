from codecs import open
from unidecode import unidecode

male_lines = open('Resources/male.txt', 'r', 'utf-8').readlines()
male_names = [unidecode(item.split(',')[0].lower()) for item in male_lines]
female_lines = open('Resources/female.txt', 'r', 'utf-8').readlines()
female_names = [unidecode(item.split(',')[0].lower()) for item in female_lines]
unisex_lines = open('Resources/unisex.csv', 'r', 'utf-8').readlines()
unisex_names = [unidecode(item.split(',')[0].lower()) for item in male_lines]
lista = male_names + female_names + unisex_names

def validate_name(name):
    if name in lista:
        return True
    return False

if __name__ == "__main__":
    print(validate_name(name))