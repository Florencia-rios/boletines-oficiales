import pprint
from spacy_llm.util import assemble
import os
import glob
from gender_detection import *
from lemmatizer import *
from pos_tagger import *
from spelling import *
from unidecode import unidecode
import re
import time
from fuzzywuzzy import fuzz
from collections import Counter

import time

##### OCR OUTPUT########################################
directory_path = "./Documents/Boletin"
########################################################

nlp = assemble("config.cfg")

##################NUMBER OF JOINT SENTENCES: DEFAULT 2#################
def split_string_on_double_occurrence(input_string, character):
    pattern = character + r"(?=(?:.*" + character + "){2})"
    parts = re.split(pattern, input_string)
    return parts
character = "\."
########################################################################

############# EN CASO DE USO DE HUGGINGFACE###############
#from huggingface_hub import login
#access_token_read = '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'
#login(token = access_token_read)
#######################################


############################# PREPARE CHUNKS###############
def get_chunks(text, max_length):
    out = []
    threshold = max_length
    for chunk in text.split('.'):
        if out and len(chunk)+len(out[-1]) < threshold:
            out[-1] += ' '+chunk+'.'
        else:
            out.append(chunk+'.')
    return out

############################# NER #########################
def extract_ner(input, index):

    b_list = get_chunks(input.replace('\n', ' ') , 2000)

    annotations = []

    nlp.initialize()
    for sent in b_list:
        print(sent)
        doc = nlp(sent.replace('-', ' '))
        for ent in doc.ents:

            ###############PERSONAS DEBEN TENER PRIMER NOMBRE VALIDADO##################
            if ent.label_ == "PERSON":
                if not validate_name(unidecode(ent.text.split()[0].lower())) or ' ' not in ent.text:
                    continue
                if is_word_number(ent.text.lower()):
                    continue
            #############################################################################

            #####ORGANIZATION NO CONTIENE NUMEROS####################################
            if ent.label_ == "ORGANIZATION":
                if re.search(r'\d', ent.text):
                    continue
            ##########################################################################

            #####NUMBER NO CONTIENE NUMEROS####################################
            if ent.label_ == "DATE":
                if re.search(r'^\d', ent.text):
                    continue
            ##########################################################################

            #####CAPITAL NO CONTIENE NUMEROS####################################
            if ent.label_ == "CAPITAL":
                if re.search(r'^\d', ent.text):
                    continue
                   
            ##########################################################################

            #####LOCATION NO CONTIENE NUMEROS####################################
            if ent.label_ == "LOCATION":
                if re.search(r'^\d', ent.text):
                    continue
                   
            ##########################################################################            

            annotations.append((spelling(ent.text).lower() if ent.label_ in ['AUTHORIZATION', 'OCCUPATION'] else ent.text.lower(), ent.label_, ent.start_char + index, ent.end_char + index))

        index += len(sent)

    unique_annotations = set((x[0], x[1]) for x in annotations)
    counts = Counter((item[0], item[1]) for item in annotations)

    return (list(sorted(unique_annotations)))

##### MAIN ###############################################################
index = 0

def process_file(file_path):
#    global index
    with open(file_path, 'r') as file:
        file_contents = file.read()
        print("----------STARTING PROCESS--------------")
        print(f"Contents of {file_path}, Current Index: {index}")
        print(f"Size of page: {len(file_contents)}")
        return extract_ner(file_contents, index)


def filter_similar_names(data, similarity_threshold=85):
    unique_names = {}
    result = []

    for item in data:
        name = item['final_key'][0]
        label = item['final_key'][1]

        # Check for similar names in the unique_names dictionary
        is_unique = True
        for key, value in unique_names.items():
            similarity = fuzz.ratio(name, key)
            if similarity >= similarity_threshold:
                is_unique = False
                break

        if is_unique:
            unique_names[name] = label
            result.append(item)

    return result


start = time.time()

################################################
###INPUT FOLDER PAGED
txt_files = sorted(glob.glob(os.path.join(directory_path, "*.txt")), key=lambda x: int(os.path.basename(x).split('.')[0]))
####WHEN INPUT FOLDER IS NOT PAGED
temp_output = []
for txt_file in txt_files:
    temp_output.extend(process_file(txt_file))
##################################################


filtered_list = [(term, category) for term, category in temp_output if category != 'X']

final_counts = Counter((item[0], item[1]) for item in filtered_list)
new_filtered_list = []
for l in filtered_list:
    a = dict(final_counts)
    for k,v in dict(final_counts).items():
        if l[0] in str(k):
            new_filtered_list.append({"final_key":l,"freq":v})
data_sorted = sorted(new_filtered_list, key=lambda x: (x['freq'], x['final_key']), reverse = True)
summed_entries = {}

# Iterate through the data
for entry in data_sorted:
    final_key = entry['final_key']
    freq = entry['freq']

    # If the final_key is not in the summed_entries dictionary, add it with the current frequency
    if final_key not in summed_entries:
        summed_entries[final_key] = freq
    else:
        # If the final_key is already in the dictionary, add the current frequency to the existing one
        summed_entries[final_key] += freq

# Convert the summed_entries dictionary back to a list of dictionaries
summed_data = [{'final_key': key, 'freq': value} for key, value in summed_entries.items()]


final_output = list(sorted(set(filtered_list)))


###############IDENTITY MATCHER ACTIVATED (OPCIONAL) ################
merged_tuples = filter_similar_names(summed_data)
###################################################################

print("----------FINAL EXTRACTIONS -----------------")
pprint.pprint(merged_tuples)

end = time.time()
print("----------ELAPSED SECONDS-----------------" + str(end - start))

