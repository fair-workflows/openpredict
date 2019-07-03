#!/usr/bin/env python
# coding: utf-8

"""
RDF generator for the Human Interactome (https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt)
@version 1.0
@author Remzi Celebi
"""

import pandas as pd
import utils
from utils import Dataset, DataResource

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

def addMetaData(g, graphURI):
    #generate dataset
    data_source = Dataset(qname=graphURI, graph = g)
    data_source.setURI(graphURI)
    data_source.setTitle('The Human Interactome Dataset')
    data_source.setDescription('Human Interactome data used in "Uncovering Disease-Disease Relationships Through The Human Interactome" study')
    data_source.setPublisher('https://science.sciencemag.org/')
    data_source.setPublisherName('American Association for the Advancement of Science')
    data_source.addRight('no-commercial')
    data_source.addRight('use')
    data_source.addTheme('http://www.wikidata.org/entity/Q896177')
    data_source.addTheme('http://www.wikidata.org/entity/Q25113323')
    data_source.setLicense('https://www.sciencemag.org/about/terms-service')
    data_source.setHomepage('https://dx.doi.org/10.1126%2Fscience.1257601')
    data_source.setVersion('1.0')


    #generate dataset distribution
    data_dist = DataResource(qname=graphURI, graph = data_source.toRDF())
    data_dist.setURI('https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt')
    data_dist.setTitle('The Human Interactome Dataset (srep35241-s3.txt)')
    data_dist.setLicense('https://www.sciencemag.org/about/terms-service')
    data_dist.setVersion('1.0')
    data_dist.setFormat('text/tab-separated-value')
    data_dist.setMediaType('text/tab-separated-value')
    data_dist.setPublisher('https://science.sciencemag.org/')
    data_dist.addRight('no-commercial')
    data_dist.addRight('use')
    data_dist.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist.setDataset(data_source.getURI())

    #generate RDF data distrubtion
    rdf_dist = DataResource(qname=graphURI, graph = data_dist.toRDF() )
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/human_interactome.nq.gz')
    rdf_dist.setTitle('RDF Version of the Human Interactome')
    rdf_dist.setLicense('http://creativecommons.org/licenses/by/3.0/')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/HumanInteractome.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/human_interactome.nq.gz')
    rdf_dist.setDataset(data_dist.getURI())
      
    return rdf_dist.toRDF()

g = addMetaData(g, graphURI)


outfile ='../data/rdf/human_interactome.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)




