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
from utils import Dataset, DataResource
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
graphURI ='http://fairworkflows.org/openpredict_resource:fairworkflows.dataset.openpredict.predict.R1'
g = ConjunctiveGraph(identifier = URIRef(graphURI))  
g=  utils.to_rdf(g, gold_std_mapped_df, column_types, 'http://bio2rdf.org/drugbank:Drug' )



def addMetaData(g, graphURI):
    #generate dataset
    data_source = Dataset(qname=graphURI, graph = g)
    data_source.setURI(graphURI)
    data_source.setTitle('Supplementary data used in the PREDICT')
    data_source.setDescription('Drug indications gold standard and mappings used in the study of "PREDICT: a method for inferring novel drug indications with application to personalized medicine" ')
    data_source.setPublisher('https://www.embopress.org/journal/17444292')
    data_source.setPublisherName('Molecular Systems Biology')
    data_source.addRight('use-share-modify')
    data_source.addTheme('http://www.wikidata.org/entity/Q56863002')
    data_source.setLicense('https://www.embopress.org/page/journal/17444292/about')
    data_source.setHomepage('https://dx.doi.org/10.1038%2Fmsb.2011.26')
    data_source.setVersion('1.0')


    #generate dataset distribution
    data_dist1 = DataResource(qname=graphURI, graph = data_source.toRDF())
    data_dist1.setURI('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls')
    data_dist1.setTitle('Mapping between OMIM diseases and UMLS concepts used in the PREDICT study (msb201126-s4.xls)')
    data_dist1.setDescription('This file contains the mappings between OMIM diseases and UMLS concepts used in the PREDICT study')
    data_dist1.setLicense('https://creativecommons.org/publicdomain/zero/1.0/')
    data_dist1.setVersion('1.0')
    data_dist1.setFormat('application/vnd.ms-excel')
    data_dist1.setMediaType('application/vnd.ms-excel')
    data_dist1.setPublisher('https://www.embopress.org/journal/17444292')
    data_dist1.addRight('use-share-modify')
    data_dist1.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist1.setDataset(data_source.getURI())
    
    
    #generate dataset distribution
    data_dist2 = DataResource(qname=graphURI, graph = data_dist1.toRDF())
    data_dist2.setURI('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s1.xls')
    data_dist2.setTitle('Drug indications gold standard used in the PREDICT study (msb201126-s1.xls)')
    data_dist2.setDescription('This file contains the gold standard drug indications used in the PREDICT study')
    data_dist2.setLicense('https://creativecommons.org/publicdomain/zero/1.0/')
    data_dist2.setVersion('1.0')
    data_dist2.setFormat('application/vnd.ms-excel')
    data_dist2.setMediaType('application/vnd.ms-excel')
    data_dist2.setPublisher('https://www.embopress.org/journal/17444292')
    data_dist2.addRight('use-share-modify')
    data_dist2.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist2.setDataset(data_source.getURI())
     

    #generate RDF data distrubtion
    rdf_dist = DataResource(qname=graphURI, graph = data_dist2.toRDF() )
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/predict-gold-standard-omim.nq.gz')
    rdf_dist.setTitle('RDF version of PREDICT drug indication gold standard')
    rdf_dist.setDescription('This file is the RDF version of PREDICT drug indication gold standard')
    rdf_dist.setLicense('http://creativecommons.org/licenses/by/3.0/')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/MappingPREDICTGoldstandard.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/known_associations/predict-gold-standard-omim.nq.gz')
    rdf_dist.setDataset(data_dist2.getURI())
    rdf_dist.addSource('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s1.xls')
    rdf_dist.addSource('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159979/bin/msb201126-s4.xls')
      
    return rdf_dist.toRDF()

g= addMetaData(g, graphURI)

outfile ='../data/rdf/predict-gold-standard-omim.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




