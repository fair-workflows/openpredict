#!/usr/bin/env python
# coding: utf-8

"""
RDF generator for the OMIM HPO Annotations (http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/misc/phenotype_annotation_hpoteam.tab)
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


url = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/misc/phenotype_annotation_hpoteam.tab'
hpoannot_df = pd.read_csv(url,sep='\t', header=None)

#save the file
hpoannot_df.to_csv('../data/external/phenotype_annotation_hpoteam.tab', sep='\t', index=False, header=None)

#preprocessing
hpoannot_df.rename(columns={0:'DB',1:'DB_Object_ID',4:'HPO_ID'}, inplace=True)
hpoannot_df = hpoannot_df[['DB','DB_Object_ID','HPO_ID']]
hpoannot_df= hpoannot_df[hpoannot_df.DB =='OMIM']
hpoannot_df.drop(columns=['DB'], inplace=True)

hpoannot_df['DB_Object_ID'] = hpoannot_df['DB_Object_ID'].map(lambda x: 'http://bio2rdf.org/omim:'+str(x))
hpoannot_df['HPO_ID']= hpoannot_df['HPO_ID'].map(lambda x: 'http://bio2rdf.org/hpo:'+str(x[3:]))
hpoannot_df = hpoannot_df.set_index('DB_Object_ID', drop=True)
hpoannot_df.rename(columns={'HPO_ID':'http://semanticscience.org/resource/SIO_000255'},inplace=True)

column_types ={'http://semanticscience.org/resource/SIO_000255':'URI'}
graphURI = URIRef('http://fairworkflows.org/openpredict_resource:fairworkflows.dataset.openpredict.hpoannot.R1')
g = ConjunctiveGraph(identifier = graphURI)     

g=  utils.to_rdf(g, hpoannot_df, column_types, 'http://bio2rdf.org/omim_vocabulary:Phenotype' )

def addProvanace(g, graphURI):
    now = datetime.datetime.now()
    
    datasetURI= URIRef('https://github.com/fair-workflows/openpredict/data/rdf/hpo_annotations.nq')
    g.add((graphURI, RDF.type, DC.Dataset))
    g.add((graphURI, URIRef('http://www.w3.org/ns/dcat#distribution'), datasetURI))
    sourcedatasetURI =  URIRef('https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt')
    
    g.add((datasetURI, DC['title'], Literal('RDF Version of OMIM HPO Annotations')))
    g.add((datasetURI, DC['format'], Literal('application/n-quads')))
    g.add((datasetURI, DC['created'], Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((datasetURI, DC['creator'], Literal('https://github.com/fair-workflows/openpredict/OMIMHpoAnnotations.ipynb')))

    g.add((datasetURI, DC['homepage'], URIRef('https://github.com/fair-workflows/openpredict/')))
    g.add((datasetURI, DC['license'], URIRef('http://creativecommons.org/licenses/by/3.0/')))
    g.add((datasetURI, DC['rights'], Literal('use-share-modify')))
    g.add((datasetURI, DC['rights'], Literal('by-attribution')))
    g.add((datasetURI, DC['rights'], Literal('restricted-by-source-license')))

    g.add((datasetURI, DC['source'], sourcedatasetURI))
        
    g.add((sourcedatasetURI, DC['title'], Literal('Phenote-annotated by HPO-team (http://phenotype_annotation_hpoteam.tab)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://hpo.jax.org/app/download/annotation')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('text/tsv')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('https://hpo.jax.org/app/license')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('https://hpo.jax.org/app/download/annotation')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('citation-required')))
    
    return g

g=addProvanace(g, graphURI)
outfile ='../data/rdf/hpo_annotations.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)


