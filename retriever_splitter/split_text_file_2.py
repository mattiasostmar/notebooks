
import os
import glob
import re
import nltk
import codecs

def create_filename(source_file, file_counter):
    split = os.path.basename(source_file).split('.')
    return "{0}_{1:04d}.{2}".format(split[0], file_counter, split[1])

def process_file(source_folder, source_file, destination_folder, split_count):
    
    pattern = r"(\w+[-]\w+)|(\w*)(?:[-][\r\n]+)(?:\W*)(\w+)|(\w+)"

    data = nltk.data.load(os.path.join(source_folder, source_file), 'text')    
    tokenizer = nltk.tokenize.RegexpTokenizer(pattern, gaps=False, discard_empty=True, flags=re.UNICODE | re.MULTILINE | re.DOTALL)
    
    file_counter = 0
    counter = 0
    for word in tokenizer.tokenize(data):
        
        if counter % split_count == 0:
            
            if counter > 0:
                counter = 0
                outfile.close()
            
            file_counter += 1
            destination_file = os.path.join(destination_folder, create_filename(source_file, file_counter))
            outfile = open(destination_file, "w", encoding="utf8")

        counter += 1
        
        outfile.write(''.join(word) if isinstance(word, (list, tuple)) else word)
        
        outfile.write(" ")

def split_files_in_folder(source_folder, destination_folder, chunk_size):
    files = [ os.path.basename(f) for f in glob.glob(os.path.join(source_folder,"*.txt")) ]
    for source_file in files:
        print("Processing file {0}...".format(source_file))
        process_file("", source_file, destination_folder, chunk_size)

if __name__ == "__main__":
    
    #source_folder = "M:/#Temp/sou/1970-talet/"
    #destination_folder = "\\\\HORSE.humlab.umu.se\\Delad\\#Temp\\sou\\splits\\"
    source_folder = "Desktop/pressmaterial"
    destination_folder = "Desktop/pressmat"

    chunk_size = 1000
    
    if not os.path.isdir(destination_folder):
        print("Please create destination library first")
        exit()
        
    nltk.data.path.append(source_folder)
    
    split_files_in_folder(source_folder, destination_folder, chunk_size)
    
