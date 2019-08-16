import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint
import requests
import time
import csv
#from itertools import izip
from requests.exceptions import ConnectionError

## register account in ncbo to use the annotator
## and use the provided api key in the code
REST_URL = "http://data.bioontology.org"
API_KEY = "put your key here"

def get_json(url):
    opener = urllib.build_opener()
    #print opener
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    #print opener
    return json.loads(opener.open(url).read())

def print_annotations(annotations, get_class=True):
    for result in annotations:
        #print result
        time.sleep(5)
        class_details = get_json(result["annotatedClass"]["links"]["self"]) #if get_class else result["annotatedClass"]
        #print class_details
        id = class_details["@id"]
        print (id[-7:])
 

tic = time.time()

meshTermList = []
omimList = []

### input directory containing all omim files
indir = '/Users/sayyar/Documents/openpredict/data/'
for root,dirs,filenames in os.walk(indir):
    for f in filenames:
        meshList = []
        #print(f)
        fullpath = os.path.join(indir, f)
        jsonFile = open(fullpath, 'r')

        try: 
            values = json.load(jsonFile)
            jsonFile.close()
            omim = values['omim']['entryList'][0]['entry']['mimNumber']
            omimList.append(omim)
            text = values['omim']['entryList'][0]['entry']['textSectionList']#[4]['textSection']['textSectionContent']
            subtext = ""

            l = len(text)
            for i in range(l):
                subtext += str(text[i])

            text_to_annotate = subtext
            
            #annotations = get_json(REST_URL + "/annotator?text=" + urllib2.quote(text_to_annotate) + "&ontologies=MESH"  + "&longest_only=true")
            #print_annotations(annotations)

            annotations = requests.post(REST_URL + "/annotator", {"text": subtext, "ontologies": "MESH", "longest_only": "true", "apikey": "0450cae7-bbf6-42c7-a390-24c15862de60"})

            inp = annotations.text
            List=eval(inp)
            
            for i in range(len(List)): 
                meshTerm = List[i]["annotatedClass"]["@id"][-7:]                
                meshList.append(meshTerm)            
            meshTermList.append(meshList)
            print (omim, ','.join(meshList))

            ## this is the default time interval for the ncbo annotator for post requests
            ## It can take 10 requests/sec per user
            time.sleep(1)
        ### Error handling    
        except (ValueError, e):
            print("Invalid Json file: %s", e)
        except ConnectionError as k:   
            print (k)
        except (IOError,e):
            if e.errno == errno.ENOENT:
                print ("Error: the given file does not exist.")
                sys.exit()


toc = time.time()
print ('Time taken so far = ', toc - tic)

#text_to_annotate = "Melanoma is a malignant tumor of melanocytes which are found predominantly in skin but also in the bowel and the eye."


