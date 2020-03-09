from os import walk
from bs4 import BeautifulSoup
from tqdm import tqdm

import re
import sys, os, time, html, math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from collections import Counter

OUTPUT_DIR = sys.argv[2]
INPUT_DIR_PATH = './' + sys.argv[1]
OUT_DIR_PATH = './' + OUTPUT_DIR
DOC_NUMBERS_TO_PLOT = [10, 20, 40, 80, 100, 200, 300, 400, 500]

def main():

    # Dictionary to maitain word frequency across documents
    word_freq_per_doc = {}
    doc_len = {}

    # List to store time taken to process each file
    proc_times_per_file = []
    proc_times_cumulative  = [0]
    proc_times_cumulative = [0]

    file_list = get_file_list()
    num_of_files = len(file_list)
    validate_output_directory()
    
    global_word_counter = extract_data(file_list, word_freq_per_doc, doc_len, proc_times_cumulative)

    doc_freq_per_word = calculate_doc_freq_per_word(global_word_counter, word_freq_per_doc)

    idf_per_word = calculate_idf(doc_freq_per_word, num_of_files)
    calculate_and_store_weights(word_freq_per_doc)

    proc_times_cumulative.pop(0)

    display_line_graph(DOC_NUMBERS_TO_PLOT, proc_times_cumulative)

def extract_data(file_list, word_freq_per_doc, doc_len, proc_times_cumulative):
    s = set()
    global_word_counter = Counter()
    
    f = open("stopwords.txt", "r")
    stopwords = np.loadtxt(f, dtype=str)
    f.close()

    # start recording time
    start_time = time.time()
    file_count = 0
    
    for fl in tqdm(file_list):
        file_count += 1
        wordcount = Counter()

        path = INPUT_DIR_PATH + '/' + fl
        f = open(path, 'r', encoding="utf-8", errors='ignore')

        try:
            file_data = f.read()
            soup = BeautifulSoup(file_data, 'html.parser')
            html_data = soup.get_text()
            html_data = html.unescape(html_data).lower()
            extracted_data = " ".join(re.findall("[a-zA-Z]+", html_data))

            extracted_data = extracted_data.split(' ')
            
            for word in extracted_data:
                if word not in stopwords and len(word) > 1:
                    if word in global_word_counter:
                        global_word_counter.update({word: 1})
                    elif word in s:
                        global_word_counter.update({word: 2})
                    else:
                        s.add(word)
                    
                    wordcount.update({word: 1})

            # stop recording time
            end_time = time.time()
            processing_time = (end_time - start_time)*1000

            if file_count in DOC_NUMBERS_TO_PLOT:
                proc_times_cumulative.append(proc_times_cumulative[-1] + processing_time)

        finally:
            f.close()

        word_freq_per_doc[fl] = wordcount
        doc_len[fl] = sum(wordcount.values())

    return global_word_counter

def calculate_doc_freq_per_word(global_word_counter, word_freq_per_doc):
    doc_freq_per_word = {}
    for word in global_word_counter:
        count = 0
        for elem in word_freq_per_doc.items():
            words = elem[1]
            if word in words.keys():
                count += 1

        if count > 0:
            doc_freq_per_word[word] = count

    return doc_freq_per_word

def calculate_idf(doc_freq_per_word, num_of_files):
    idf_per_word = {}
    for elem in doc_freq_per_word.items():
        idf = math.log(num_of_files/elem[1])
        idf_per_word[elem[0]] = idf

    return idf_per_word

def calculate_and_store_weights(word_freq_per_doc):
    for item in word_freq_per_doc.items():
        word_freq = dict(item[1])

        denominator = sum(word_freq.values())
        result_path = OUT_DIR_PATH + '/' + item[0] + '.wts'
        writer = open(result_path, 'w')
        
        for word, count in word_freq.items():
            numerator = count
            tf = numerator/denominator

            writer.write(word)
            writer.write(" ")
            writer.write(str(tf))
            writer.write("\n")
        writer.close()


def display_line_graph(xaxis, proc_times_cumulative):
    plt.title("Processing times vs number of documents processed")
    plt.ylabel('Time in milliseconds')
    plt.xlabel('Number of files')
    plt.grid(True)
    plt.plot(xaxis, proc_times_cumulative)
    
    plt.savefig(OUT_DIR_PATH+'/time_vs_no_files.png')
    plt.show()

# Get list of all input files from the directory
def get_file_list():
    file_list = []
    if not os.path.exists(INPUT_DIR_PATH):
        print("Input directory does not exist")
    else:
        for (dirpath, dirnames, filenames) in walk(INPUT_DIR_PATH):
            file_list.extend(filenames)
            return file_list

# Create the output Directory if it doesn't exist
def validate_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
        print("Directory with name " , OUTPUT_DIR,  " created.")
    else:    
        print("Directory with name " , OUTPUT_DIR,  " already exists.")


main()
