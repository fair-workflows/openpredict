

from sklearn import metrics
import numbers
import pandas as pd
import numpy as np


# # Merge feature matrix
def adjcencydict2matrix(df, name1, name2):
    df1 = df.copy()
    df1= df1.rename(index=str, columns={name1: name2, name2: name1})
    print (len(df))
    df =df.append(df1)
    print (len(df))
    return df.pivot(index=name1, columns=name2)

# merge feature vector into single matrix
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


# Generate positive and negative pairs
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

# Balance negative samples/postives 
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


# # Feature extraction (Best Combined similarity)
def geometricMean(drug, disease, knownDrugDisease, drugDF, diseaseDF):
    #print (drug, disease)
    a  = drugDF.loc[knownDrugDisease[:,0]][drug].values
    b  = diseaseDF.loc[knownDrugDisease[:,1]][disease].values
    #print (a,b)
    c = np.sqrt( np.multiply(a,b) )
    ix2 = (knownDrugDisease == [drug, disease])
    c[ix2[:,1]& ix2[:,0]]=0.0
    return float(np.max(c))


def createFeatureDF(pairs, classes, knownDrugDisease, drugDFs, diseaseDFs):
    totalNumFeatures = len(drugDFs)*len(diseaseDFs)
    #featureMatri x= np.empty((len(classes),totalNumFeatures), float)
    df =pd.DataFrame(list(zip(pairs[:,0], pairs[:,1], classes)), columns =['Drug','Disease','Class'])
    index = 0
    for i,drug_col in enumerate(drugDFs.columns.levels[0]):
        for j,disease_col in enumerate(diseaseDFs.columns.levels[0]):
            drugDF = drugDFs[drug_col]
            diseaseDF = diseaseDFs[disease_col]
            df["Feature_"+str(drug_col)+'_'+str(disease_col)] = df.apply(lambda row: geometricMean( row.Drug, row.Disease, knownDrugDisease, drugDF, diseaseDF), axis=1)
    return df

def calculateCombinedSimilarity(pairs_train, pairs_test, classes_train, classes_test, drug_df, disease_df, knownDrugDisease):
    train_df  = createFeatureDF(pairs_train, classes_train, knownDrugDisease, drug_df, disease_df)
    test_df = createFeatureDF(pairs_test, classes_test, knownDrugDisease, drug_df, disease_df)
    return train_df, test_df


# Model Training
def trainModel(train_df, clf):
    features = list(train_df.columns.difference(['Drug','Disease','Class']))
    X = train_df[features]
    y = train_df['Class']
    print ('fiting classifier...')
    clf.fit(X, y)
    return clf


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
    features = list(test_df.columns.difference(['Drug','Disease','Class']))
    X_test =  test_df[features]
    y_test = test_df['Class']

    scoring = ['precision', 'recall', 'accuracy', 'roc_auc', 'f1', 'average_precision']
    scorers, multimetric = metrics.scorer._check_multimetric_scoring(clf, scoring=scoring)
    scores = multimetric_score(clf, X_test, y_test, scorers)
    return scores


