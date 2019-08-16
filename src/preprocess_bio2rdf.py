import sys
import gzip
import re
import argparse





if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True , dest='input', help='enter the input file to preprocess')
    parser.add_argument('-o', required=True , dest='output', help='enter the output file')
    
    args = parser.parse_args()
    inputfile = args.input
    outputfile = args.output
    
    fw = gzip.open(outputfile, 'wt')

    with gzip.open(inputfile,'rb') as nqfile:
        for line in nqfile:
            line = str(line)
            line =  line.replace("\\'","'").replace('%','')
            line = line.replace('> <','>\t<').replace('\" <','\"\t<').replace('> \"','>\t\"')
            line = line.split('\t')

            if line[0].startswith('<'):
                line[0] =line[0].replace(' ','')
            if line[2].startswith('<'):
                line[2] =line[2].replace(' ','')
            fw.write('\t'.join(line))

