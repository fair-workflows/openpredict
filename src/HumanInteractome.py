#!/usr/bin/env python
# coding: utf-8

"""
RDF generator for the Human Interactome (https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt)
@version 1.0
@author Remzi Celebi
"""

import pandas as pd
import utils

from rdflib import Namespace
from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph
import datetime

DC = Namespace("http://purl.org/dc/terms/")


def download():
    url = 'https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt'
    return pd.read_csv(url,skiprows=25,sep='\t')


interactome_df = download()

interactome_df.rename(columns={'# gene_ID_1':'gene_id_1',' gene_ID_2':'gene_id_2','data_source(s)':'source'}, inplace=True)

# save the file
interactome_df.to_csv('../data/external/human_interactome.tsv', sep='\t', index=False)


interactome_df.index =interactome_df.apply(lambda row: 'http://bio2rdf.org/openpredict_resource:'+str(row['gene_id_1'])+'_'+str(row['gene_id_2']), axis=1)

interactome_df['gene_id_1'] = interactome_df['gene_id_1'].map(lambda x: 'http://bio2rdf.org/ncbigene:'+str(x))
interactome_df['gene_id_2'] = interactome_df['gene_id_2'].map(lambda x: 'http://bio2rdf.org/ncbigene:'+str(x))
interactome_df.rename(columns={'gene_id_1':'http://bio2rdf.org/irefindex_vocabulary:interactor_a'},inplace=True)

interactome_df.rename(columns={'gene_id_2':'http://bio2rdf.org/irefindex_vocabulary:interactor_b'},inplace=True)
interactome_df.rename(columns={'source':'http://bio2rdf.org/irefindex_vocabulary:source'},inplace=True)


column_types ={'http://bio2rdf.org/irefindex_vocabulary:interactor_a':'URI','http://bio2rdf.org/irefindex_vocabulary:interactor_b':'URI','http://bio2rdf.org/irefindex_vocabulary:source':'Literal'}
graphURI = URIRef('http://fairworkflows.org/openpredict_resource:fairworkflows.dataset.openpredict.interactome.R1')
g =  ConjunctiveGraph(identifier = graphURI)     
g=  utils.to_rdf(g, interactome_df, column_types, 'http://edamontology.org/topic_0128' )



def addProvanace(g, graphURI):
    now = datetime.datetime.now()
    
    datasetURI= URIRef('https://github.com/fair-workflows/openpredict/data/rdf/human_interactome.nq')
    g.add((graphURI, RDF.type, DC.Dataset))
    g.add((graphURI, URIRef('http://www.w3.org/ns/dcat#distribution'), datasetURI))
    sourcedatasetURI =  URIRef('https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt')
    
    g.add((datasetURI, DC['title'], Literal('RDF Version of the Human Interactome')))
    g.add((datasetURI, DC['format'], Literal('application/n-quads')))
    g.add((datasetURI, DC['created'], Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((datasetURI, DC['creator'], Literal('https://github.com/fair-workflows/openpredict/HumanInteractome.ipynb')))

    g.add((datasetURI, DC['homepage'], URIRef('https://github.com/fair-workflows/openpredict/')))
    g.add((datasetURI, DC['license'], URIRef('http://creativecommons.org/licenses/by/3.0/')))
    g.add((datasetURI, DC['rights'], Literal('use-share-modify')))
    g.add((datasetURI, DC['rights'], Literal('by-attribution')))
    g.add((datasetURI, DC['rights'], Literal('restricted-by-source-license')))

    g.add((datasetURI, DC['source'], sourcedatasetURI))
        
    g.add((sourcedatasetURI, DC['title'], Literal('The Human Interactome used in Uncovering Disease-Disease Relationships Through The Human Interactome  (srep35241-s3.txt)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://dx.doi.org/10.1126%2Fscience.1257601')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('text')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('https://creativecommons.org/publicdomain/mark/1.0/')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('https://science.sciencemag.org/')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('allow-commercial-purposes')))
    
    return g

#g=addProvanace(g, graphURI)


outfile ='../data/rdf/human_interactome.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




