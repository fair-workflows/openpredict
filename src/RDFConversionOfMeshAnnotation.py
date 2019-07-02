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
g=  utils.to_rdf(g, mim2mesh_df, column_types, 'http://bio2rdf.org/omim_vocabulary:Phenotype' )

def addProvanace(g, graphURI):
    now = datetime.datetime.now()
    datasetURI= URIRef('https://github.com/fair-workflows/openpredict/data/rdf/omim_mesh_annotations.nq')
    g.add((graphURI, RDF.type, DC.Dataset))
    g.add((graphURI, URIRef('http://www.w3.org/ns/dcat#distribution'), datasetURI))
    sourcedatasetURI =  URIRef('http://www.paccanarolab.org/static_content/disease_similarity/mim2mesh.tsv')
    
    g.add((datasetURI, DC['title'], Literal('Mesh Annotations for OMIM ids')))
    g.add((datasetURI, DC['format'], Literal('application/n-quads')))
    g.add((datasetURI, DC['created'], Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((datasetURI, DC['creator'], Literal('https://github.com/fair-workflows/openpredict/RDFConversionOfMeshAnnotation.ipynb')))

    g.add((datasetURI, DC['homepage'], URIRef('https://github.com/fair-workflows/openpredict/')))
    g.add((datasetURI, DC['license'], URIRef('http://creativecommons.org/licenses/by/3.0/')))
    g.add((datasetURI, DC['rights'], Literal('use-share-modify')))
    g.add((datasetURI, DC['rights'], Literal('by-attribution')))
    g.add((datasetURI, DC['rights'], Literal('restricted-by-source-license')))

    g.add((datasetURI, DC['source'], sourcedatasetURI))
        
    g.add((sourcedatasetURI, DC['title'], Literal('OMIM Mesh Annotations (mim2mesh.tsv)')))
    g.add((sourcedatasetURI, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('http://www.paccanarolab.org/disease_similarity/')))
    g.add((sourcedatasetURI, DC['homepage'], URIRef('https://doi.org/10.1038/srep17658')))
    g.add((sourcedatasetURI, URIRef('http://purl.org/pav/retrievedOn'), Literal(now.strftime("%Y-%m-%d %H:%M:%S"))))
    g.add((sourcedatasetURI, DC['format'], Literal('text/tsv')))
    g.add((sourcedatasetURI, DC['rights'], URIRef('http://creativecommons.org/licenses/by/4.0/')))
    g.add((sourcedatasetURI, DC['publisher'], Literal('http://www.paccanarolab.org/')))
    g.add((sourcedatasetURI, DC['rights'], Literal('use')))
    g.add((sourcedatasetURI, DC['rights'], Literal('no-commercial')))
    
    return g

g= addProvanace(g, graphURI)

outfile ='../data/rdf/omim_mesh_annotations.nq'
g.serialize(outfile, format='nquads')
print('RDF is generated at '+outfile)



