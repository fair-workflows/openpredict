#!/usr/bin/env python
# coding: utf-8

# In[1]:

import ml
import utils
import random
import numpy as np
import pandas as pd
import math
import time

from sklearn import tree, ensemble
from sklearn import svm, linear_model, neighbors
from sklearn import model_selection
from sklearn.model_selection import GroupKFold

from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph, Namespace



import time


# # Get the features and gold standard 
rel_path = '../data/features/'
drugfeatfiles = ['drugs-fingerprint-sim.csv','drugs-se-sim.csv', 
                 'drugs-ppi-sim.csv', 'drugs-target-go-sim.csv','drugs-target-seq-sim.csv']
diseasefeatfiles =['diseases-hpo-sim.csv',  'diseases-pheno-sim.csv' ]

drugfeatfiles = [ rel_path+fn for fn in drugfeatfiles]
diseasefeatfiles = [ rel_path+fn for fn in diseasefeatfiles]


goldindfile = '../data/input/openpredict-omim-drug.csv'
drugDiseaseKnown = pd.read_csv(goldindfile,delimiter=',') 
drugDiseaseKnown.head()

drugDiseaseKnown.rename(columns={'drugid':'Drug','omimid':'Disease'}, inplace=True)
drugDiseaseKnown.Disease = drugDiseaseKnown.Disease.astype(str)
drugDiseaseKnown.head()


drug_df, disease_df = ml.mergeFeatureMatrix(drugfeatfiles, diseasefeatfiles)

# # Generate positive and negative pairs
pairs, classes = ml.generatePairs(drug_df, disease_df, drugDiseaseKnown)

# # Balance negative samples/postives 
n_proportion = 2
pairs, classes= ml.balance_data(pairs, classes, n_proportion)


# # Train-Test Splitting
pairs_train, pairs_test, classes_train, classes_test = model_selection.train_test_split(pairs, classes, stratify=classes, test_size=0.2, shuffle=True)

print ('# of train samples',len(pairs_train),'# of test samples', len(pairs_test))


# # Feature extraction (Best Combined similarity)
knownDrugDisease= pairs_train[classes_train==1]
train_df, test_df = ml.calculateCombinedSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)


# # Model Training


n_seed = 100
clf = linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.0001, C=1.0, random_state=n_seed) 
clf = ml.trainModel(train_df, clf)


# # Evaulation 

scores = ml.evaluate(test_df, clf)
print ("Test:",scores)


# # 10-fold drug-disjoint cross-validation (PREDICT - CV scheme )

disjoint = True
n_fold = 10

if disjoint:
    print ('Disjoint')
    groups = pairs[:,0] # group by drug
    group_kfold = GroupKFold(n_splits=n_fold)
    cv = group_kfold.split(pairs, classes, groups)
else:
    print ('Non-disjoint')
    skf = StratifiedKFold(n_splits=n_fold, shuffle=True, random_state=n_seed)
    cv = skf.split(pairs, classes)

n_seed = 100
cv_results = pd.DataFrame()
clf = linear_model.LogisticRegression(penalty='l2', solver='lbfgs', dual=False, tol=0.0001, C=1.0, random_state=n_seed) 
  
for i, (train, test) in enumerate(cv):
    print ('Fold',i+1)
    start_time = time.time()
    pairs_train = pairs[train]
    classes_train = classes[train] 
    pairs_test = pairs[test]
    classes_test = classes[test]
    knownDrugDisease= pairs_train[classes_train==1]
    
    train_df, test_df = ml.calculateCombinedSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)
    elapsed_time = time.time() - start_time
    print ('Time elapsed to generate features:',time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

    clf = ml.trainModel(train_df, clf)
    
    scores = ml.evaluate(test_df, clf)
    #print ("Scores:",scores)
    cv_results = cv_results.append(scores, ignore_index=True)




print ("Performance Results:")
print (cv_results.mean())

cv_results.to_csv('../data/results/disjoint_lr.csv')


def generateURI(prefix):
    uniqueID= int(round(time.time() * 1000))
    uri = URIRef(prefix+str(uniqueID))
    return uri


DC = Namespace("http://purl.org/dc/terms/")
MLS = Namespace("http://www.w3.org/ns/mls#")
RPC = Namespace("https://w3id.org/reproduceme#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
def addProvanace(g):
    #graphURI = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.output.openpredict.R1')

    runURI = generateURI('http://www.w3.org/ns/mls#Run')
    evalURI = generateURI('http://www.w3.org/ns/mls#ModelEvaluation')
    accURI = generateURI('http://www.w3.org/ns/mls#Accuracy')
    evalSpecURI = generateURI('http://www.w3.org/ns/mls#EvaluationSpecification')
    
    g.add((runURI, RDF['type'], MLS['Run']))
    g.add((runURI, MLS['achieves'], RPC['Pipeline_OpenPREDICT']))
          
    g.add((runURI, MLS['hasOutput'], evalURI))
    g.add((evalURI, RDF['type'], MLS['ModelEvaluation']))
    
    g.add((evalSpecURI, MLS['defines'],  RPC['Pipeline_OpenPREDICT']))
    g.add((evalSpecURI, MLS['hasPart'],  MLS['TenFoldCrossValidation']))
    g.add((MLS['TenFoldCrossValidation'], RDF['type'],  MLS['EvaluationProcedure']))
    g.add((MLS['TenFoldCrossValidation'], RDFS['label'],  Literal('10-fold CV')))
    
    g.add((evalSpecURI, MLS['hasPart'],  MLS['DrugwiseCrossValidation']))
    g.add((MLS['DrugwiseCrossValidation'], RDF['type'],  MLS['EvaluationProcedure']))
    g.add((MLS['DrugwiseCrossValidation'], RDFS['label'],  Literal('Drugwise CrossValidation')))
    g.add((MLS['DrugwiseCrossValidation'], DC['description'],  Literal('Split drugs in 10-fold, remove drugs of each fold in the gold standard and consequently remove all the known indication sassociated with them')))
    
    g.add((evalSpecURI, MLS['hasPart'],  accURI))      
    g.add((evalURI, MLS['specifiedBy'],accURI ))
    g.add((accURI, RDF['type'], MLS['EvaluationMeasure']))  
    g.add((accURI, RDFS['label'],  Literal('Accuracy')))
    g.add((accURI, MLS['hasValue'],  Literal('0.85')))
   
    return g

g =  ConjunctiveGraph(identifier = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.dataset.openpredict.R1')) 
    

g= addProvanace(g)

outfile ='../data/rdf/results_disjoint_lr.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




