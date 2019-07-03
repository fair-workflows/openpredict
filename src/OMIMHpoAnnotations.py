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
from utils import Dataset, DataResource
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

def addMetaData(g, graphURI):
    #generate dataset
    data_source = Dataset(qname=graphURI, graph = g)
    data_source.setURI(graphURI)
    data_source.setTitle('Phenotype annotatations by the HPO-team')
    data_source.setDescription('This dataset contains manual and semi-automated annotations created by the HPO-team. These are annotations of OMIM-, Orphanet-, and DECIPHER-entries')
    data_source.setPublisher('https://monarchinitiative.org/')
    data_source.setPublisherName('Monarch Initiative')
    data_source.addRight('use')
    data_source.addTheme('http://www.wikidata.org/entity/Q17027854')
    data_source.addTheme('http://www.wikidata.org/entity/Q45314346')
    data_source.setLicense('https://hpo.jax.org/app/license')
    data_source.setHomepage('https://hpo.jax.org/app/download/annotation')
    data_source.setVersion('1.0')


    #generate dataset distribution
    data_dist = DataResource(qname=graphURI, graph = data_source.toRDF())
    data_dist.setURI('http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab')
    data_dist.setTitle('Phenotypes annotated by the HPO-team (phenotype_annotation_hpoteam.tab)')
    data_dist.setLicense('https://hpo.jax.org/app/license')
    data_dist.setVersion('1.0')
    data_dist.setFormat('text/tab-separated-value')
    data_dist.setMediaType('text/tab-separated-value')
    data_dist.setPublisher('https://monarchinitiative.org/')
    data_dist.addRight('use')
    data_dist.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist.setDataset(data_source.getURI())

    #generate RDF data distrubtion
    rdf_dist = DataResource(qname=graphURI, graph = data_dist.toRDF() )
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/hpo_annotations.nq.gz')
    rdf_dist.setTitle('RDF Version of the OMIM HPO Annotations')
    rdf_dist.setLicense('http://creativecommons.org/licenses/by/3.0/')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/OMIMHpoAnnotations.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/hpo_annotations.nq.gz')
    rdf_dist.setDataset(data_dist.getURI())
      
    return rdf_dist.toRDF()

g = addMetaData(g, graphURI)
outfile ='../data/rdf/hpo_annotations.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)


