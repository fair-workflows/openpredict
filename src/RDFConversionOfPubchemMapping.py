#!/usr/bin/env python
# coding: utf-8
"""
RDF generator for the mappings from Pubchem ids to Drugbank ids (https://raw.githubusercontent.com/dhimmel/drugbank/3e87872db5fca5ac427ce27464ab945c0ceb4ec6/data/mapping/pubchem.tsv)
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


url = 'https://raw.githubusercontent.com/dhimmel/drugbank/3e87872db5fca5ac427ce27464ab945c0ceb4ec6/data/mapping/pubchem.tsv'
drugbank_map_df = pd.read_csv(url, sep='\t')

#save the original file
drugbank_map_df.to_csv('../data/external/pubchem.tsv', sep='\t', index=False)


drugbank_map_df['drugbank_id'] = drugbank_map_df['drugbank_id'].map(lambda x: 'http://bio2rdf.org/drugbank:'+str(x))
drugbank_map_df['pubchem_id'] = drugbank_map_df['pubchem_id'].map(lambda x: 'http://bio2rdf.org/pubchem.compound:'+str(x))
drugbank_map_df = drugbank_map_df.set_index('drugbank_id', drop=True)
drugbank_map_df.rename(columns={'pubchem_id':'http://bio2rdf.org/openpredict_vocabulary:x-pubchemcompound'},inplace=True)

column_types ={'http://bio2rdf.org/openpredict_vocabulary:x-pubchemcompound':'URI'}
graphURI = URIRef('http://fairworkflows.org/openpredict_resource:fairworkflows.dataset.openpredict.pubchem.R1')
g = ConjunctiveGraph(identifier = graphURI)     

g = utils.to_rdf(g, drugbank_map_df, column_types, 'http://bio2rdf.org/drugbank:Drug' )


def addProvanace(g, graphURI):
    now = datetime.datetime.now()
    
    datasetURI= URIRef('https://github.com/fair-workflows/openpredict/data/rdf/pubchem_mapping.nq')
    g.add((graphURI, RDF.type, DC.Dataset))
    g.add((graphURI, URIRef('http://www.w3.org/ns/dcat#distribution'), datasetURI))
    sourcedatasetURI =  URIRef('https://raw.githubusercontent.com/dhimmel/drugbank/3e87872db5fca5ac427ce27464ab945c0ceb4ec6/data/mapping/pubchem.tsv')
    
    g.add((datasetURI, DC['title'], Literal('Pubchem mapping for Drugbank ids')))
    g.add((datasetURI, DC['format'], Literal('application/n-quads')))
    g.add((datasetURI, DC['created'], Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((datasetURI, DC['creator'], Literal('https://github.com/fair-workflows/openpredict/RDFConversionOfPubchemMapping.ipynb')))

    g.add((datasetURI, DC['homepage'], URIRef('https://github.com/fair-workflows/openpredict/')))
    g.add((datasetURI, DC['license'], URIRef('http://creativecommons.org/licenses/by/3.0/')))
    g.add((datasetURI, DC['rights'], Literal('use-share-modify')))
    g.add((datasetURI, DC['rights'], Literal('by-attribution')))
    g.add((datasetURI, DC['rights'], Literal('restricted-by-source-license')))

    g.add((datasetURI, DC['source'], sourcedatasetURI))
        
    g.add((sourcedatasetURI, DC['title'], Literal('Mapping From Drugbank to Pubchem  (pubchem.tsv)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://github.com/dhimmel/drugbank')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('text/tsv')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('https://creativecommons.org/licenses/by-nc/4.0/')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('https://github.com/dhimmel/drugbank')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('no-commercial')))
    
    return g


g=addProvanace(g, graphURI)

outfile ='../data/rdf/pubchem_mapping.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




