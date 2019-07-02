#!/usr/bin/env python
# coding: utf-8

"""
RDF generator for the PREDICT drug indication gold standard (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls)
@version 1.0
@author Remzi Celebi
"""


import pandas as pd
from csv import reader
import utils
from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph
from rdflib import Namespace
import datetime


DC = Namespace("http://purl.org/dc/terms/")

mapping_df = pd.read_excel('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls')
#save the original file
mapping_df.to_csv('../data/external/msb201126-s4.csv', index=False)


mapping_df['OMIM disease name'].replace({'Neuropathy, Hereditary Sensory And Autonomic, Type I, With Cough And':
                                         'Neuropathy, Hereditary Sensory And Autonomic, Type I, With Cough And Gastroesophageal Reflux'}, inplace=True)

goldstd_df = pd.read_excel('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s1.xls')
# save the file
goldstd_df.to_csv('../data/external/msb201126-s1.csv', sep='\t', index=False)

goldstd_df['Drug name'].replace({'Divalproex Sodium':'Valproic Acid',
                                 'Bismuth':'Bismuth subsalicylate',
                                'Clobetasol':'Clobetasol propionate',
                               'Guanadrel Sulfate':'Guanadrel',
                                 'Marinol':'Dronabinol',
                               'Medroxyprogesterone':'Medroxyprogesterone acetate',
                                'Megestrol':'Megestrol acetate',
                                'Propoxyphene':'Dextropropoxyphene',
                                 'Salicyclic Acid':'Salicylic acid',
                                'Ipratropium':'Ipratropiumbromid',
                                'Adenosine Monophosphate':'Adenosine monophosphate',
                                'Arsenic Trioxide':'Arsenic trioxide',
                                'Ethacrynic Acid':'Ethacrynic acid',
                                'Fondaparinux Sodium':'Fondaparinux sodium',
                                 'Meclofenamic Acid':'Meclofenamic acid',
                                'Methyl Aminolevulinate':'Methyl aminolevulinate'},inplace=True)




merged_df = goldstd_df.merge(mapping_df, left_on='Disease name', right_on='OMIM disease name')


drug_synonym_df = pd.read_csv('../data/input/drugbank-drug-synonym.csv')
merged_df = merged_df.merge(drug_synonym_df, left_on='Drug name', right_on='name')

print ('# of drug-disease associations',len(merged_df[['drugid','OMIM ID']].drop_duplicates()))


gold_std_mapped_df = merged_df[['drugid','OMIM ID']].drop_duplicates()
gold_std_mapped_df['drugid'] = gold_std_mapped_df['drugid'].map(lambda x: 'http://bio2rdf.org/drugbank:'+str(x))
gold_std_mapped_df['OMIM ID'] = gold_std_mapped_df['OMIM ID'].map(lambda x: 'http://bio2rdf.org/omim:'+str(x))
gold_std_mapped_df.rename(columns={'OMIM ID':'http://bio2rdf.org/openpredict_vocabulary:indication'},inplace=True)
gold_std_mapped_df= gold_std_mapped_df.set_index('drugid', drop=True)

column_types ={'http://bio2rdf.org/openpredict_vocabulary:indication':'URI'}
g = ConjunctiveGraph(identifier = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.dataset.openpredict.R1'))     
g=  utils.to_rdf(g, gold_std_mapped_df, column_types, 'http://bio2rdf.org/drugbank:Drug' )


def addProvanace(g):
    now = datetime.datetime.now()
    graphURI = URIRef('http://bio2rdf.org/openpredict_resource:bio2rdf.dataset.openpredict.R1')
    datasetURI= URIRef('https://github.com/fair-workflows/openpredict/known_associations/predict-gold-standard-omim.nq')
    g.add((graphURI, RDF.type, DC.Dataset))
    g.add((graphURI, URIRef('http://www.w3.org/ns/dcat#distribution'), datasetURI))
   
    
    g.add((datasetURI, DC['title'], Literal('RDF version of PREDICT drug indication gold standard')))
    g.add((datasetURI, DC['format'], Literal('application/n-quads')))
    g.add((datasetURI, DC['created'], Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((datasetURI, DC['creator'], Literal('https://github.com/fair-workflows/openpredict/MappingPREDICTGoldstandard.ipynb')))
    g.add((datasetURI, DC['source'], URIRef('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s1.xls')))
    g.add((datasetURI, DC['source'], URIRef('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls')))

    g.add((datasetURI, DC['homepage'], URIRef('https://github.com/fair-workflows/openpredict/')))
    g.add((datasetURI, DC['license'], URIRef('http://creativecommons.org/licenses/by/3.0/')))
    g.add((datasetURI, DC['rights'], Literal('use-share-modify')))
    g.add((datasetURI, DC['rights'], Literal('by-attribution')))
    g.add((datasetURI, DC['rights'], Literal('restricted-by-source-license')))
        
    sourcedatasetURI = URIRef('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s1.xls')
    g.add((sourcedatasetURI, DC['title'], Literal('Drug indications gold standard used in the PREDICT study (msb201126-s1.xls)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://dx.doi.org/10.1038%2Fmsb.2011.26')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('application/xls')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('https://creativecommons.org/licenses/by-nc-sa/3.0/us/')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('Molecular Systems Biology')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('no-commercial')))
          

    sourcedatasetURI = URIRef('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls')
    g.add((sourcedatasetURI, DC['title'], Literal('Mapping between OMIM diseases and UMLS concepts used in the PREDICT study (msb201126-s4.xls)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://dx.doi.org/10.1038%2Fmsb.2011.26')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('application/xls')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('https://creativecommons.org/licenses/by-nc-sa/3.0/us/')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('Molecular Systems Biology')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('no-commercial')))
    
    return g

g= addProvanace(g)

outfile ='../data/rdf/predict-gold-standard-omim.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




