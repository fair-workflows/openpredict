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
from utils import Dataset, DataResource
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


def addMetaData(g, graphURI):
    #generate dataset
    data_source = Dataset(qname=graphURI, graph = g)
    data_source.setURI(graphURI)
    data_source.setTitle('Pubchem mappings for Drugbank drugs')
    data_source.setDescription('DrugBank to PubChem mapping using InChI strings created by Daniel Himmelstein.')
    data_source.setPublisher('https://github.com/dhimmel')
    data_source.setPublisherName('Daniel Himmelstein')
    data_source.addRight('use-share-modify')
    data_source.addTheme('http://www.wikidata.org/entity/Q278487')
    data_source.addTheme('http://www.wikidata.org/entity/Q1122544')
    data_source.setLicense('http://creativecommons.org/licenses/by/4.0/')
    data_source.setHomepage('https://github.com/dhimmel/drugbank/blob/gh-pages/pubchem-map.ipynb')
    data_source.setVersion('1.0')


    #generate dataset distribution
    data_dist = DataResource(qname=graphURI, graph = data_source.toRDF())
    data_dist.setURI('https://raw.githubusercontent.com/dhimmel/drugbank/3e87872db5fca5ac427ce27464ab945c0ceb4ec6/data/mapping/pubchem.tsv')
    data_dist.setTitle('Pubchem mappings for Drugbank drugs (pubchem.tsv)')
    data_dist.setLicense('http://creativecommons.org/licenses/by/4.0/')
    data_dist.setVersion('1.0')
    data_dist.setFormat('text/tab-separated-value')
    data_dist.setMediaType('text/tab-separated-value')
    data_dist.setPublisher('https://github.com/dhimmel')
    data_dist.addRight('use-share-modify')
    data_dist.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist.setDataset(data_source.getURI())

    #generate RDF data distrubtion
    rdf_dist = DataResource(qname=graphURI, graph = data_dist.toRDF() )
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/pubchem_mapping.nq.gz')
    rdf_dist.setTitle('RDF Version of the Pubchem mappings for Drugbank drugs')
    rdf_dist.setLicense('http://creativecommons.org/licenses/by/3.0/')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/RDFConversionOfPubchemMapping.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/pubchem_mapping.nq.gz')
    rdf_dist.setDataset(data_dist.getURI())
      
    return rdf_dist.toRDF()


g = addMetaData(g, graphURI)

outfile ='../data/rdf/pubchem_mapping.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




