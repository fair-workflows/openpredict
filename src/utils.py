#!/usr/bin/env python
# coding: utf-8
"""
Utility functions and classes
@version 1.0
@author Remzi Celebi
"""


import pandas as pd
from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph, Namespace
DC = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
PAV = Namespace("http://purl.org/pav/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/name")


class DataResource:
    def __init__(self, qname):
        self.setQName(qname)
        self.graph =  ConjunctiveGraph(identifier = self.getQName()) 
        
    def setRDFGraph(self, graph): self.graph = graph
    def getRDFGraph(self): return self.graph
        
    def setURI(self, uri): self.uri = uri
    def getURI(self): return self.uri
        
    def setQName(self, qname): self.qname = qname
    def getQName(self): return self.qname
        
    def setTitle(self, title): self.title = title
    def getTitle(self): return self.title
        
    def setDescription(self, description): self.description = description
    def getDescription(self): return self.description
        
    def setPublisher(self, publisher): self.publisher = publisher
    def getPublisher(self): return self.publisher
        
    def setHomepage(self, homepage): self.homepage = homepage
    def getHomepage(self): return self.homepage
        
    def setSources(self, sources): self.sources = sources
    def getSources(self): return self.sources
    
    def setCreator(self, creator): self.creator = creator
    def getCreator(self): return self.creator
    
    def setCreateDate(self, create_date): self.create_date = create_date
    def getCreateDate(self): return self.create_date
    
    def setRetrievedDate(self, retrieved_date): self.retrieved_date = retrieved_date
    def getRetrievedDate(self): return self.retrieved_date
    
    def setIssuedDate(self, issued_date): self.issued_date = issued_date
    def getIssuedDate(self): return self.issued_date
    
    def setVersion(self, version): self.version = version
    def getVersion(self): return self.version
    
    def setFormat(self, format): self.format = format
    def getFormat(self): return self.format
    
    def setMediaType(self, media_type): self.media_type = media_type
    def getMediaType(self): return self.media_type
    
    def setLicense(self, license): self.license = license
    def getLicense(self): return self.license
        
    def setRights(self, rights): self.rights = rights
    def getRights(self): return self.rights
    
    def addRight(self, right):
        if self.rights == None: self.rights =[]
        self.rights.append(right)
    
    def setLocation(self, location): self.location = location
    def getLocation(self): return self.location
    
    def setDataset(self, dataset): self.dataset = dataset
    def getDataset(self): return self.dataset
    
    def setDownloadURL(self, download_url): self.download_url = download_url
    def getDownloadURL(self): return self.download_url
    
    def toRDF(self):
        
        label = ''
        if self.getTitle() != None and self.getTitle() != '':
            label = self.getTitle()
        
        if self.getCreateDate():
            label +=" generated at "+self.getCreateDate()
        
        dataset_uri = self.getURI()
        
        graph = self.getRDFGraph()
        
        graph.add((dataset_uri, RDF['type'], URIRef('http://www.w3.org/ns/dcat#Distribution')))
        graph.add((dataset_uri, RDFS['label'], Literal(label)))
        
        if self.getTitle() != None:
            graph.add((dataset_uri, DC['title'], Literal( self.getTitle() )))
            
        if self.getDescription() != None:
             graph.add((dataset_uri, DC['description'], Literal( self.getDescription() )))
                
        if self.getCreateDate() != None:
             graph.add((dataset_uri, DC['created'], Literal( self.getCreateDate() )))
                
        if self.getIssuedDate() != None:
             graph.add((dataset_uri, DC['issued'], Literal( self.getIssuedDate() )))
            
        if self.getRetrievedDate() != None:
             graph.add((dataset_uri, PAV['retrievedOn'], Literal( self.getRetrievedDate() )))
                
        if self.getIssuedDate() != None:
             graph.add((dataset_uri, DC['issued'], Literal( self.getIssuedDate() )))
                
        for source in self.getSources() :
            if source != None :
                graph.add((datasetURI, DC['source'], URIRef( source )))
            
        if self.getCreator() != None:
            graph.add((dataset_uri, DC['creator'], URIRef( self.getCreator() )))
            
        if self.getPublisher() != None:
            graph.add((dataset_uri, DC['publisher'], URIRef( self.getPublisher() )))
            
        if self.getHomepage() != None:
            graph.add((dataset_uri, FOAF['page'], URIRef( self.getHomepage() )))
            
        if self.getDownloadURL() != None:
            graph.add((dataset_uri, DCAT['downloadURL'], URIRef( self.getDownloadURL() )))
            
        if self.getVersion() != None:
            graph.add((dataset_uri, DC['hasVersion'], Literal( self.getVersion() )))
            
        if self.getMediaType() != None:
            graph.add((dataset_uri, DCAT['mediaType'], Literal( self.getMediaType() ))) 
            
        if self.getFormat() != None:
            graph.add((dataset_uri, DC['format'], Literal( self.getFormat() ))) 
            
        if self.getDataset() != None:
            graph.add((dataset_uri, DC['source'], URIRef( self.getDataset() )))
            
        if self.getLicense() != None:
            graph.add((dataset_uri, DC['license'], URIRef( self.getLicense() )))
            
        for right in self.getRights() :
            if right != None :
                graph.add((dataset_uri, DC['rights'], Literal( right )))
        
        return graph
        

class Dataset:
    def __init__(self, qname):
        self.setQName(qname)
        self.graph =  ConjunctiveGraph(identifier = self.getQName()) 
        
    def setRDFGraph(self, graph): self.graph = graph
    def getRDFGraph(self): return self.graph
        
    def setURI(self, uri): self.uri = uri
    def getURI(self): return self.uri
    
    def setVersion(self, version): self.version = version
    def getVersion(self): return self.version
    
    def setThemes(self, themes): self.themes = themes
    def getTheme(self): return self.themes
    
     def addTheme(self, theme):
        if self.themes == None: self.themes =[]
        self.themes.append(theme)
        
    def setRights(self, rights): self.rights = rights
    def getRights(self): return self.rights
    
    def addRight(self, right):
        if self.rights == None: self.rights =[]
        self.rights.append(right)
        
    def setCatalog(self, catalog): self.catalog = catalog
    def getCatalog(self): return self.catalog
        
    def setTitle(self, title): self.title = title
    def getTitle(self): return self.title
        
    def setDescription(self, description): self.description = description
    def getDescription(self): return self.description
        
    def setPublisher(self, publisher): self.publisher = publisher
    def getPublisher(self): return self.publisher
    
    def setPublisherName(self, publisher_name): self.publisher_name = publisher_name
    def getPublisherName(self): return self.publisher_name
        
    def setHomepage(self, homepage): self.homepage = homepage
    def getHomepage(self): return self.homepage
        
        
    def setRDFFile(self, rdf_file): self.rdf_file = rdf_file
    def getRDFFile(self): return self.rdf_file
    
    def toRDF(self):
        
        dataset_uri = self.getURI()
        
        graph = self.getRDFGraph()
        graph.add((dataset_uri, RDF['type'], DC['Dataset'] ))
        
        if self.getTitle() != None:
            graph.add((dataset_uri, DC['title'], Literal( self.getTitle() )))
            
        if self.getDescription() != None:
             graph.add((dataset_uri, DC['description'], Literal( self.getDescription() )))
            
        if self.getVersion() != None:
            graph.add((dataset_uri, DC['hasVersion'], Literal( self.getVersion() )))
            
        if self.getPublisher() != None:
            publisher_uri = URIRef( self.getPublisher() )
            graph.add((dataset_uri, DC['publisher'], publisher_uri))
            if self.getPublisherName() != None:
                graph.add((publisher_uri, RDF.type, FOAF['Organization'] ))
                graph.add((publisher_uri, FOAF['name'], URIRef( self.getPublisherName() )))
            
        if self.getHomepage() != None:
            graph.add((dataset_uri, FOAF['page'], URIRef( self.getHomepage() )))
        
            
        if self.getLicense() != None:
            graph.add((dataset_uri, DC['license'], URIRef( self.getLicense() )))
            
        for right in self.getRights() :
            if right != None :
                graph.add((dataset_uri, DC['rights'], Literal( right )))
        
        for theme in self.getThemes() :
            if theme != None :
                graph.add((dataset_uri, DCAT['theme'], URIRef( theme )))
        
        return graph

def to_rdf(g, df, column_types, row_uri):
    """
    Parameters
    ----------
    g : input rdflib.Graph  
    df: DataFrame to be converted into RDF Graph
    column_types: dictonary of column and its type, type can be URI or Literal
    row_uri: rdf:type value for row index, should be URI
    Returns
    -------
    g: rdflib.Graph generated from DataFrame object
    """
    
    for (index, series) in df.iterrows():
        g.add((URIRef(index), RDF.type, URIRef(row_uri)) )
        for (column, value) in series.iteritems():
            if column_types[column] == 'URI':
                g.add((URIRef(index), URIRef(column), URIRef(value)))
            else:
                g.add((URIRef(index), URIRef(column), Literal(value)))
                
    return g


def test():   
    #generate dataset
    data_source = utils.Dataset()
    data_source.setURI('https://w3id.org/fairworkflows/human_interactome')
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
    data_dist = utils.DataResource()
    data_dist.setURI('https://media.nature.com/full/nature-assets/srep/2016/161017/srep35241/extref/srep35241-s3.txt')
    data_dist.setTitle('The Human Interactome Dataset (srep35241-s3.txt)')
    data_dist.setDescription('This file contains the Human Interactome used in "Uncovering Disease-Disease Relationships Through The Human Interactome" study')
    data_dist.setLicense('https://www.sciencemag.org/about/terms-service')
    data_dist.setVersion('1.0')
    data_dist.setFormat('text/tab-separated-value')
    data_dist.setMediaType('text/tab-separated-value')
    data_dist.setPublisher('https://science.sciencemag.org/')
    data_dist.addRight('no-commercial')
    data_dist.addRight('use')
    data_dist.setRetrievedDate(now.strftime("%Y-%m-%d %H:%M:%S"))
    data_dist.setDataset(data_source.getURI())

    #generate RDF data distrubtion
    rdf_dist = utils.DataResource()
    rdf_dist.setURI('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/human_interactome.nq.gz')
    rdf_dist.setTitle('DF Version of the Human Interactome')
    rdf_dist.setDescription('This file contains the Human Interactome used in "Uncovering Disease-Disease Relationships Through The Human Interactome" study')
    rdf_dist.setLicense('https://www.sciencemag.org/about/terms-service')
    rdf_dist.setVersion('1.0')
    rdf_dist.setFormat('application/n-quads')
    rdf_dist.setMediaType('application/n-quads')
    rdf_dist.addRight('use-share-modify')
    rdf_dist.addRight('by-attribution')
    rdf_dist.addRight('restricted-by-source-license')
    rdf_dist.setCreateDate(now.strftime("%Y-%m-%d %H:%M:%S"))
    rdf_dist.setCreator('https://github.com/fair-workflows/openpredict/src/HumanInteractome.py')
    rdf_dist.setDownloadURL('https://github.com/fair-workflows/openpredict/blob/master/data/rdf/human_interactome.nq.gz')
    rdf_dist.setDataset(data_dist.getURI())
