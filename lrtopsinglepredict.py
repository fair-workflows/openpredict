import random
import numpy as np
from sklearn import model_selection
from sklearn.model_selection import GroupKFold
import pandas as pd
import math
import time
import os
#from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph, Namespace
drugfeatfiles = ['drugs-fingerprint-sim.csv','drugs-se-sim.csv', 
                     'drugs-ppi-sim.csv', 'drugs-target-go-sim.csv','drugs-target-seq-sim.csv']
diseasefeatfiles =['diseases-hpo-sim.csv',  'diseases-pheno-sim.csv' ]
feature_folder ="data/features"

drugfeatfiles = [ os.path.join(feature_folder, fn) for fn in drugfeatfiles]
diseasefeatfiles = [ os.path.join(feature_folder, fn) for fn in diseasefeatfiles]

drug_ind="data/input/openpredict-omim-drug.csv"


drugDiseaseKnown = pd.read_csv(drug_ind,delimiter=',') 
drugDiseaseKnown.head()

drugDiseaseKnown.rename(columns={'drugid':'Drug','omimid':'Disease'}, inplace=True)
drugDiseaseKnown.Disease = drugDiseaseKnown.Disease.astype(str)
drugDiseaseKnown.head()

def adjcencydict2matrix(df, name1, name2):
    df1 = df.copy()
    df1= df1.rename(index=str, columns={name1: name2, name2: name1})
    print (len(df))
    df =df.append(df1)
    print (len(df))
    return df.pivot(index=name1, columns=name2)

def mergeFeatureMatrix(drugfeatfiles, diseasefeatfiles):
    for i,featureFilename in enumerate(drugfeatfiles):
        print (featureFilename)
        df = pd.read_csv(featureFilename, delimiter=',')
        cond = df.Drug1 > df.Drug2
        df.loc[cond, ['Drug1', 'Drug2']] = df.loc[cond, ['Drug2', 'Drug1']].values
        if i != 0:
            drug_df=drug_df.merge(df,on=['Drug1','Drug2'],how='inner')
            #drug_df=drug_df.merge(temp,how='outer',on='Drug')
        else:
            drug_df =df
    drug_df.fillna(0, inplace=True)
    
    drug_df = adjcencydict2matrix(drug_df, 'Drug1', 'Drug2')
    drug_df = drug_df.fillna(1.0)

    
    for i,featureFilename in enumerate(diseasefeatfiles):
        print (featureFilename)
        df=pd.read_csv(featureFilename, delimiter=',')
        cond = df.Disease1 > df.Disease2
        df.loc[cond, ['Disease1','Disease2']] = df.loc[cond, ['Disease2','Disease1']].values
        if i != 0:
            disease_df = disease_df.merge(df,on=['Disease1','Disease2'], how='inner')
            #drug_df=drug_df.merge(temp,how='outer',on='Drug')
        else:
            disease_df = df
    disease_df.fillna(0, inplace=True)
    disease_df.Disease1 = disease_df.Disease1.astype(str)
    disease_df.Disease2 = disease_df.Disease2.astype(str)
    
    disease_df = adjcencydict2matrix(disease_df, 'Disease1', 'Disease2')
    disease_df = disease_df.fillna(1.0)
    
    return drug_df, disease_df

drug_df, disease_df = mergeFeatureMatrix(drugfeatfiles, diseasefeatfiles)



def generatePairs(drug_df, disease_df, drugDiseaseKnown):
    drugwithfeatures = set(drug_df.columns.levels[1])
    diseaseswithfeatures = set(disease_df.columns.levels[1])
    
    drugDiseaseDict  = set([tuple(x) for x in  drugDiseaseKnown[['Drug','Disease']].values])

    commonDrugs= drugwithfeatures.intersection( drugDiseaseKnown.Drug.unique())
    commonDiseases=  diseaseswithfeatures.intersection(drugDiseaseKnown.Disease.unique() )
    print ("commonDrugs: %d commonDiseases : %d"%(len(commonDrugs),len(commonDiseases)))

    #abridged_drug_disease = [(dr,di)  for  (dr,di)  in drugDiseaseDict if dr in drugwithfeatures and di in diseaseswithfeatures ]

    #commonDrugs = set( [ dr  for dr,di in  abridged_drug_disease])
    #commonDiseases  =set([ di  for dr,di in  abridged_drug_disease])

    print ("Gold standard, associations: %d drugs: %d diseases: %d"%(len(drugDiseaseKnown),len(drugDiseaseKnown.Drug.unique()),len(drugDiseaseKnown.Disease.unique())))
    print ("Drugs with features: %d Diseases with features: %d"%(len(drugwithfeatures),len(diseaseswithfeatures)))
    print ("commonDrugs: %d commonDiseases : %d"%(len(commonDrugs),len(commonDiseases)))

    pairs=[]
    classes=[]
    for dr in commonDrugs:
        for di in commonDiseases:
            cls = (1 if (dr,di) in drugDiseaseDict else 0)
            pairs.append((dr,di))
            classes.append(cls)
            
    return pairs, classes

pairs, classes = generatePairs(drug_df, disease_df, drugDiseaseKnown)

from sklearn.model_selection import GroupKFold
from sklearn.model_selection import StratifiedKFold
def balance_data(pairs, classes, n_proportion):
    classes = np.array(classes)
    pairs = np.array(pairs)
    
    indices_true = np.where(classes == 1)[0]
    indices_false = np.where(classes == 0)[0]

    np.random.shuffle(indices_false)
    indices = indices_false[:(n_proportion*indices_true.shape[0])]
    print ("+/-:", len(indices_true), len(indices), len(indices_false))
    pairs = np.concatenate((pairs[indices_true], pairs[indices]), axis=0)
    classes = np.concatenate((classes[indices_true], classes[indices]), axis=0) 
    
 
    return pairs, classes

n_proportion = 2
pairs, classes= balance_data(pairs, classes, n_proportion)

pairs_train, pairs_test, classes_train, classes_test = model_selection.train_test_split(pairs, classes, stratify=classes, test_size=0.2, shuffle=True)

len(pairs_train), len(pairs_test)
def calculateDrugMaxMean(drug, disease, knownDrugDisease, drugDF):
    #print (drug, disease)
    
    # get only diseases related to this drug
    filteredDrugs=knownDrugDisease[knownDrugDisease[:,1]==disease,0]
    similarities  = drugDF.loc[filteredDrugs][drug].values
    similarities2= np.where(similarities==1.0,0.0,similarities)
    #knownDrugDisease[knownDrugDisease[:,1]==disease,0]
    #c=np.where(a==1.0,0.0,a)
    try:
        maxSimilarity=float(np.max(similarities2))
    except :
        maxSimilarity=0.0         
        
    return maxSimilarity

#not used , we use best similar disease instead of diseases filtered wrt drugs
def calculateDiseaseMaxMeanFiltered(drug, disease, knownDrugDisease, diseaseDF):
    #print (drug, disease)
    
    # get only diseases related to this drug
    filteredDiseases=knownDrugDisease[knownDrugDisease[:,0]==drug,1]
    similarities  = diseaseDF.loc[filteredDiseases][disease].values
    similarities2= np.where(similarities==1.0,0.0,similarities)
    #knownDrugDisease[knownDrugDisease[:,1]==disease,0]
    #c=np.where(a==1.0,0.0,a)
    try:
        maxSimilarity=float(np.max(similarities2))
    except :
        maxSimilarity=0.0         
        
    return maxSimilarity


def calculateDiseaseMaxMean(drug, disease, knownDrugDisease, diseaseDF):
    #print (drug, disease)
    b  = diseaseDF.loc[knownDrugDisease[:,1]][disease].values
    #b= np.sqrt( np.multiply(b,b) ) #remove negative values
    
    c=np.where(b==1.0,0.0,b)
    return float(np.max(c))
 


def createSingleFeatureDF(pairs, classes, knownDrugDisease, drugDFs, diseaseDFs):
    totalNumFeatures = len(drugDFs)*len(diseaseDFs)
    #featureMatri x= np.empty((len(classes),totalNumFeatures), float)
    df =pd.DataFrame(list(zip(pairs[:,0], pairs[:,1], classes)), columns =['Drug','Disease','Class'])
    index = 0
    for i,drug_col in enumerate(drugDFs.columns.levels[0]):
        drugDF = drugDFs[drug_col]
        df["Feature_"+str(drug_col)] = df.apply(lambda row: calculateDrugMaxMean( row.Drug, row.Disease, knownDrugDisease, drugDF), axis=1)
        
    for j,disease_col in enumerate(diseaseDFs.columns.levels[0]):
        diseaseDF = diseaseDFs[disease_col]
        df["Feature_"+str(disease_col)] = df.apply(lambda row: calculateDiseaseMaxMean( row.Drug, row.Disease, knownDrugDisease, diseaseDF), axis=1)
    return df

def calculateSingleSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease):
    train_df  = createSingleFeatureDF(pairs_train, classes_train, knownDrugDisease, drug_df, disease_df)
    test_df = createSingleFeatureDF(pairs_test, classes_test, knownDrugDisease, drug_df, disease_df)
    return train_df, test_df


knownDrugDisease= pairs_train[classes_train==1]

train_df, test_df = calculateSingleSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)



from sklearn import tree, ensemble
from sklearn import svm, linear_model, neighbors



features= ['Feature_GO-SIM_HPO-SIM',
 'Feature_GO-SIM_PHENO-SIM',
 'Feature_PPI-SIM_HPO-SIM',
 'Feature_PPI-SIM_PHENO-SIM',
 'Feature_SE-SIM_HPO-SIM',
 'Feature_SE-SIM_PHENO-SIM',
 'Feature_TARGETSEQ-SIM_HPO-SIM',
 'Feature_TARGETSEQ-SIM_PHENO-SIM',
 'Feature_TC_HPO-SIM',
 'Feature_TC_PHENO-SIM']

features= ['Feature_GO-SIM',
    'Feature_PPI-SIM',
    'Feature_SE-SIM',
    'Feature_TARGETSEQ-SIM',
    'Feature_TC',
    'Feature_HPO-SIM',
    'Feature_PHENO-SIM']


def trainModel(train_df, clf):
    #features = list(train_df.columns.difference(['Drug','Disease','Class']))
    X = train_df[features]
    y = train_df['Class']
    X.head()
    print ('fiting classifier...')
    clf.fit(X, y)
    return clf


def trainSingleModel(train_df, clf):
    #features = list(train_df.columns.difference(['Drug','Disease','Class']))
    features= ['Feature_GO-SIM',
    'Feature_PPI-SIM',
    'Feature_SE-SIM',
    'Feature_TARGETSEQ-SIM',
    'Feature_TC',
    'Feature_HPO-SIM',
    'Feature_PHENO-SIM']
    X = train_df[features]
    y = train_df['Class']
    print(X.head())
    print ('fitting classifier...')
    clf.fit(X, y)
    return clf


features= ['Feature_GO-SIM',
    'Feature_PPI-SIM',
    'Feature_SE-SIM',
    'Feature_TARGETSEQ-SIM',
    'Feature_TC',
    'Feature_HPO-SIM',
    'Feature_PHENO-SIM']
X = train_df[features]
y = train_df['Class']

train_df[features].to_csv("Xdatasinglesim.csv")
train_df['Class'].to_csv("ydatasinglesim.csv")

test_df[features].to_csv("Xdatasinglesimtest.csv")
test_df['Class'].to_csv("ydatasinglesimtest.csv")

features

dataset_df=pd.concat([train_df,test_df])
dataset_df.to_csv("singlefeatures_deepdrug_repurposingpredictiondataset.csv")
dataset_df.to_csv("singlefeatures_deepdrug_repurposingpredictiondatasetDiseaseFiltered.csv")
n_seed = 100
clfx= linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.0001, C=1.0, random_state=n_seed) 
#clf = trainModel(train_df, clfx)
trainSingleModel(train_df, clfx)

from sklearn import metrics
import numbers
def multimetric_score(estimator, X_test, y_test, scorers):
    """Return a dict of score for multimetric scoring"""
    scores = {}
    for name, scorer in scorers.items():
        if y_test is None:
            score = scorer(estimator, X_test)
        else:
            
            score = scorer(estimator, X_test, y_test)

        if hasattr(score, 'item'):
            try:
                # e.g. unwrap memmapped scalars
                score = score.item()
            except ValueError:
                # non-scalar?
                pass
        scores[name] = score

        if not isinstance(score, numbers.Number):
            raise ValueError("scoring must return a number, got %s (%s) "
                             "instead. (scorer=%s)"
                             % (str(score), type(score), name))
    return scores

def evaluate(test_df, clf):
    #
    # features = list(train_df.columns.difference(['Drug','Disease','Class']))
    X_test =  test_df[features]
    y_test = test_df['Class']

    scoring = ['precision', 'recall', 'accuracy', 'roc_auc', 'f1', 'average_precision']
    #scorers, multimetric = metrics.scorer._check_multimetric_scoring(clf, scoring=scoring)
    scorers = {}
    for scorer in scoring:
        scorers[scorer] = metrics.get_scorer(scorer)

    scores = multimetric_score(clf, X_test, y_test, scorers)
    return scores

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
    
    #train_df, test_df = calculateSingleSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)
    train_df, test_df = calculateSingleSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease)


    elapsed_time = time.time() - start_time
    print ('Time elapsed to generate features:',time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

    clf = trainSingleModel(train_df, clf)
  
    scores = evaluate(test_df, clf)
    #print ("Scores:",scores)
    cv_results = cv_results.append(scores, ignore_index=True)

cv_results.mean()
resfolder='resultslrsingleDrugFiltered'
os.mkdir(resfolder)
cv_results.to_csv(resfolder+'/disjoint_lr.csv')

cv_results.head()

import time
def generateURI(prefix):
    uniqueID= int(round(time.time() * 1000))
    uri = URIRef(prefix+str(uniqueID))
    return uri

DC = Namespace("http://purl.org/dc/terms/")
MLS = Namespace("http://www.w3.org/ns/mls#")
RPC = Namespace("https://w3id.org/reproduceme#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

g =  ConjunctiveGraph(identifier = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.dataset.openpredict.R1')) 

#graphURI = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.output.openpredict.R1')
runURI = generateURI('http://www.w3.org/ns/mls#Run')
evalURI = generateURI('http://www.w3.org/ns/mls#ModelEvaluation')
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

for index, value in cv_results.mean().items():
    measureURI = generateURI('http://www.w3.org/ns/mls#Measure_'+index)
    g.add((evalSpecURI, MLS['hasPart'],  measureURI))      
    g.add((evalURI, MLS['specifiedBy'],measureURI ))
    g.add((measureURI, RDF['type'], MLS['EvaluationMeasure']))
    g.add((measureURI, RDFS['label'],  Literal(index)))
    g.add((measureURI, MLS['hasValue'],  Literal(value)))


outfile ='results/results_disjoint_lr.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)



