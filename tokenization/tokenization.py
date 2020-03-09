from os import walk
from bs4 import BeautifulSoup
from tqdm import tqdm

import re
import sys, os, time, html
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

INPUT_DIR = './' + sys.argv[1]
OUTPUT_DIR = sys.argv[2]
OUT_DIR_PATH = './' + OUTPUT_DIR


# Function that display the graph
# The graph shows the time taken to process a file vs the number of characters in the file
def display_graph(char_count, proc_times_per_file):
    plt.ylabel('Time in milliseconds')
    plt.xlabel('Number of characters in a file')
    plt.grid(True)

    colors = cm.rainbow(np.linspace(0, 1, len(proc_times_per_file)))
    for x, y, c in zip(char_count, proc_times_per_file, colors):
        plt.scatter(x, y, color=c)
    
    plt.savefig(OUT_DIR_PATH+'/time_vs_charcount.png')
    plt.show()

def display_line_graph(proc_times_cumulative):
    plt.ylabel('Time in milliseconds')
    plt.xlabel('Number of files')
    plt.grid(True)
    plt.plot(proc_times_cumulative)
    
    plt.savefig(OUT_DIR_PATH+'/time_vs_no_files.png')
    plt.show()

# Get list of all input files from the directory
def get_file_list():
    file_list = []
    if not os.path.exists(INPUT_DIR):
        print("Input directory does not exist")
    else:
        for (dirpath, dirnames, filenames) in walk(INPUT_DIR):
            file_list.extend(filenames)
            return file_list

# Create the output Directory if it doesn't exist
def validate_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
        print("Directory with name " , OUTPUT_DIR,  " created.")
    else:    
        print("Directory with name " , OUTPUT_DIR,  " already exists.")


# Dictionary to maitain word frequency
wordcount = {}

# List to store time taken to process each file
proc_times_per_file  = []
proc_times_cumulative  = [0]

# List to store number of words
char_count = []

file_list = get_file_list()

for fl in tqdm(file_list):
    path = INPUT_DIR + '/' + fl
    f = open(path, 'r', encoding="utf-8", errors='ignore')
    result_path = OUT_DIR_PATH + '/' + fl + '.txt'
    writer = open(result_path, 'w')
    try:
        file_data = f.read()
        
        # start recording time
        start_time = time.time()
        soup = BeautifulSoup(file_data, 'html.parser')
        html_data = soup.get_text()
        html_data = html.unescape(html_data).lower()
        processed_data = " ".join(re.findall("[a-zA-Z]+", html_data))
        
        char_count.append(len(processed_data))
        processed_data = processed_data.split(' ')

        # stop recording time
        end_time = time.time()

        processing_time = (end_time - start_time)*1000
        proc_times_per_file.append(processing_time)
        proc_times_cumulative.append(proc_times_cumulative[-1] + processing_time)

        for l in processed_data:

            writer.write(l)
            writer.write('\n')
        
            if l in wordcount:
                wordcount[l] += 1
            else:
                wordcount[l] = 1

    finally:
        writer.close()
        f.close()


#sort words by their frequency(descending order) and persist in file
freq_list =  sorted(wordcount.items(), key=lambda kv: kv[1], reverse=True)
writer = open(OUT_DIR_PATH + '/frequency_sorted_list.txt', 'w')
for item in freq_list:
    writer.write(item[0])
    writer.write(" ")
    writer.write(str(item[1]))
    writer.write('\n')
writer.close()

# sort words alphabetically and persist in file
alpha_list = sorted(wordcount.items())
writer = open( OUT_DIR_PATH + '/alphabetically_sorted_list.txt', 'w')
for item in alpha_list:
    writer.write(item[0])
    writer.write(" ")
    writer.write(str(item[1]))
    writer.write('\n')
writer.close()

display_graph(char_count, proc_times_per_file)
proc_times_cumulative.pop(0)
display_line_graph(proc_times_cumulative)
