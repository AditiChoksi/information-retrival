import os, codecs, sys, time, math, re
import html2text as h2t
from bs4 import BeautifulSoup
import html

# Checking the number of command line arguments
# Input and output directory path must be specified
if len(sys.argv) != 3:
    print("Input and Output directory path must be specified.")
    exit()

# Get the input directory and output directory path from command line
inpath = sys.argv[1]
outpath = sys.argv[2]

# Create a new directory if it does not exist already
if not os.path.exists(outpath):
    os.mkdir(outpath)

doc_freq = {}
freq_dist = {}
tf = {}

# Register the program's start time
prev = time.time()

# File counter
filenumber=0

# ngram of 5 chars
ngram_number = 5

# Access files in the input folder
files  = os.listdir(inpath)
print("Preprocessing times for files")
# # IDEA: terate through all the files in input directory
for file in files:
    if file.endswith(".html"):
        # open the file with ascii encoding and ignore encoding errors
        fr = open(os.path.join(inpath, file), "r",  encoding="ascii", errors="ignore")
        # read html content of the file
        file_data = fr.read()
        soup = BeautifulSoup(file_data, 'html.parser')
        html_data = soup.get_text()
        html_data = html.unescape(html_data).lower()
        text = " ".join(re.findall("[a-zA-Z]+", html_data))
        fr.close()

        #text = re.sub(r'\s+', ' ', text)

        # contains token frequency for each file
        freq_dist[file] = {}
        # contains term frequency weight of tokens for each file
        tf[file] = {}

        length = len(text) - ngram_number
        # iterate all tokens and create hashmap with frequency and document count
        for i in range(length):
            # extract 5 character token
            token = text[i:i+ngram_number]
            token = token.lower()

            # create frequency distrbution hashmap
            if token in freq_dist[file]:
                freq_dist[file][token] += 1
            else:
                freq_dist[file][token] = 1

            # create document frequency hashmap
            if token in doc_freq:
                if file not in doc_freq[token]:
                    doc_freq[token].append(file)
            else:
                doc_freq[token] = [file]

        for token in freq_dist[file]:
            # calculate term frequency weights, tf = f(d,w)/|D|
            wordtf = (freq_dist[file][token] * ngram_number)/length
            tf[file][token] = wordtf

        # find elapsed CPU time of files proccessed
        if filenumber in [10, 20, 40, 80, 100, 200, 300, 400, 500]:
            print(time.time() - prev)

        # increment file counter
        filenumber += 1

# total number of documents
collection = filenumber

filenumber = 0
# get programs start time
prev = time.time()

print("Weighing time for files")
# calculate and store tf-idf weights of tokens
for file in freq_dist:
    # conatins tf-idf for each token
    tfidf = {}
    tokens = freq_dist[file]
    for tok in tokens:
        # calculate idf = |c|/df(w)
        idf = math.log(collection/len(doc_freq[tok]))
        # calculate tfidf = tf(d,w) * idf(w)
        tfidf[tok] = tf[file][tok] * idf

    if filenumber in [10, 20, 40, 80, 100, 200, 300, 400, 500]:
        print(time.time() - prev)

    filenumber += 1

    # write tfidf weights to filename.wts as tsv
    fobj = codecs.open(os.path.join(outpath, file) +".ngram.wts", 'w', encoding='ascii',errors="ignore")
    # sort tokens in descending order of tfidf weights
    sortedvals = sorted(tfidf.items(), key=lambda kv: kv[1], reverse=True)
    for tok, tfidf in sortedvals:
        # write weights to wts file
        fobj.write(tok + "\t" + str(tfidf) + "\n")
    # close file
    fobj.close()
