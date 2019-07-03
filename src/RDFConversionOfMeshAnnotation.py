#!/usr/bin/env python
# coding: utf-8
"""
RDF generator for the PREDICT drug indication gold standard (http://www.paccanarolab.org/static_content/disease_similarity/mim2mesh.tsv)
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


url = 'http://www.paccanarolab.org/static_content/disease_similarity/mim2mesh.tsv'
df = pd.read_csv(url,header=None)
#save the original file
df.to_csv('../data/external/mim2mesh.tsv', sep=',', index=False, header=None)


omim_annots =[]
with open('../data/external/mim2mesh.tsv','r') as mim2mesh_file:
    for row in mim2mesh_file:
        line = row.strip().split('\t')
        omim =line[0]
        for i in range(1,len(line)):
            omim_annots.append([omim,line[i]])

mim2mesh_df = pd.DataFrame(omim_annots, columns=['disease','annotation'])

mim2mesh_df['disease'] = mim2mesh_df['disease'].map(lambda x: 'http://bio2rdf.org/omim:'+str(x))
mim2mesh_df['annotation'] = mim2mesh_df['annotation'].map(lambda x: 'http://bio2rdf.org/mesh:'+str(x))
mim2mesh_df = mim2mesh_df.set_index('disease', drop=True)
mim2mesh_df.rename(columns={'annotation':'http://semanticscience.org/resource/SIO_000255'},inplace=True)
column_types ={'http://semanticscience.org/resource/SIO_000255':'URI'}
graphURI = URIRef('http://fairworkflows.org/openpredict_resource:fairworkflows.dataset.openpredict.meshannot.R1')
    
g = ConjunctiveGraph(identifier = graphURI )     
g =  utils.to_rdf(g, mim2mesh_df, column_types, 'http://bio2rdf.org/omim_vocabulary:Phenotype' )

def addMetaData(g, graphURI):
    #generate dataset
    data_source = Dataset(qname=graphURI, graph = g)
    data_source.setURI(graphURI)
    data_source.setTitle('Mesh Annotations for OMIM diseases')
    data_source.setDescription('This dataset contains the MeSH terms associated with the publications referenced in OMIM. This dataset is used in  " https://doi.org/10.1038/srep17658"')
    data_source.setPublisher('http://www.paccanarolab.org')
    data_source.setPublisherName('the Paccanaro Lab')
    data_source.addRight('use-share-modify')
    data_source.addTheme('http://www.wikidata.org/entity/Q199897')
    data_source.addTheme('http://www.wikidata.org/entity/Q857525')
    data_source.setLicense('http://creativecommons.org/licenses/by/4.0/')
    data_source.setHomepage('http://www.paccanarolab.org/disease_similarity/')
    data_source.setVersion('1.0')


    #generate dataset distribution
    data_dist = DataResource(qname=graphURI, graph = data_source.toRDF())
    data_dist.setURI('http://www.paccanarolab.org/static_content/disease_similarity/mim2mesh.tsv')
    data_dist.setTitle('Mesh Annotations by the Paccanaro Lab(mim2mesh.tsv)')
    data_dist.setLicense('http://creativecommons.org/licenses/by/4.0/')
    data_dist.setVersion('1.0')
    data_dist.setFormat('text/tab-separated-value')
    data_dist.setMediaType('text/tab-separated-value')
    data_dist.setPublisher('http://www.paccanarolab.org')
    data_dist.addRight('use-share-modify')
    data_dist.setRetrievedDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_dist.setDataset(data_source.getURI())

    #generate RDF data distrubtion
    rdf_dist = DataResource(qname=graphURI, graph = data_dist.toRDF() )
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/omim_mesh_annotations.nq.gz')
    rdf_dist.setTitle('RDF Version of the MESH Annotations for OMIM diseases')
    rdf_dist.setLicense('http://creativecommons.org/licenses/by/3.0/')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/RDFConversionOfMeshAnnotation.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/omim_mesh_annotations.nq.gz')
    rdf_dist.setDataset(data_dist.getURI())
      
    return rdf_dist.toRDF()


g= addMetaData(g, graphURI)

outfile ='../data/rdf/omim_mesh_annotations.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)



