import itertools
import math
import numpy as np
import pandas as pd
import argparse
import os


from oddt import toolkit
from oddt import fingerprints

import pandas as pd
import numpy as np
import itertools


def fasta2seq(lines):
    lines = lines[lines.index('\n')+1:]
    lines =lines.replace('\n','')
    return lines


if __name__ =="__main__":
    
    parser =argparse.ArgumentParser()
    parser.add_argument('-di', required=True, dest='drug_indication', help='enter path to temp path ')
    parser.add_argument('-dt', required=True, dest='drug_target', help='enter path to temp path ')
    parser.add_argument('-se', required=True, dest='side_effects', help='enter path to temp path ')
    parser.add_argument('-tseq', required=True, dest='target_sequence', help='enter path to temp path ')
    parser.add_argument('-ppi', required=True, dest='protein_interactions', help='enter path to temp path ')
    parser.add_argument('-ds', required=True, dest='drug_smiles', help='enter path to temp path ')
    parser.add_argument('-goa', required=True, dest='gene_ontology', help='enter path to temp path ')
    parser.add_argument('-mesh', required=True, dest='mesh_annotation', help='enter path to temp path ')
    parser.add_argument('-hpo', required=True, dest='hpo_annotation', help='enter path to temp path ')

    
    parser.add_argument('-t', required=True, dest='temp', help='enter path to temp folder')
    parser.add_argument('-a', required=True, dest='absolute', help='enter path to temp folder')

    args= parser.parse_args()
    
    temp_folder = args.temp
    abs_path = args.absolute
   
    

    os.mkdir(os.path.join(temp_folder,'features'))
    os.mkdir(os.path.join(temp_folder,'intermediate'))
    
    

    drug_target = pd.read_csv(os.path.join(temp_folder, args.drug_target))
    target_seq = pd.read_csv(os.path.join(temp_folder, args.target_sequence))
    drug_goa = pd.read_csv(os.path.join(temp_folder, args.gene_ontology))
    drug_smiles = pd.read_csv(os.path.join(temp_folder, args.drug_smiles))
    drug_se = pd.read_csv(os.path.join(temp_folder, args.side_effects))
    drug_smiles.head()
    
        # In[139]:


    predict_df = pd.read_csv(os.path.join(temp_folder, args.drug_indication))
    predict_df.head()
    
    
    # reading the hpo annotation file taken from compbio.charite.de/jennkins/jobs/hpo.annotations/
    disease_hpo = pd.read_csv(os.path.join(temp_folder, args.hpo_annotation))
    disease_hpo.head()
    
    



    # ## Get the drug data

    # In[4]:


    print ("%d drugs have all Target feature "%len(  drug_target.drugid.unique()))
    print ("%d drugs have Target GOA feature "%len( drug_goa.drugid.unique()))
    print ("%d drugs have Fingerprint feature "%len(  drug_smiles.drugid.unique()))
    print ("%d drugs have Sideeffect feature "%len( drug_se.drugid.unique()))


    # In[5]:


    drug_target_seq = drug_target.merge(target_seq, on= ['geneid'])
    print ("%d drugs have Target SEQ feature "%len( drug_target_seq.drugid.unique()))


    # In[6]:


    a=drug_goa['drugid'].unique()
    b=drug_target['drugid'].unique()
    c=drug_smiles['drugid'].unique()
    d=drug_se['drugid'].unique()
    commonDrugs= set(a).intersection(b).intersection(c).intersection(d)
    print (len(a),len(b),len(c),len(d))
    print (len(commonDrugs))


    # In[7]:


    drug_se.head()


    # ## Drug side effect similarity¶
    # ## calculating Jaccard coefficient based on drug sideefects

    # In[8]:

    print ('calculating Jaccard coefficient based on drug sideefects')
    drugSEDict = {k: g["umlsid"].tolist() for k,g in drug_se.groupby("drugid")}
    scores = []

    for comb in itertools.combinations(commonDrugs,2):
        drug1 =comb[0]
        drug2 =comb[1]

        sideeffects1 = drugSEDict[drug1]
        sideeffects2 = drugSEDict[drug2]
        c = set(sideeffects1).intersection(sideeffects2)
        u = set(sideeffects1).union(sideeffects2)
        score = len(c)/float(len(u))
        scores.append([drug1, drug2, score])


    # In[9]:


    drug_se_df = pd.DataFrame(scores, columns =['Drug1','Drug2','SE-SIM'])


    # In[10]:


    drug_se_df.head()


    # In[11]:

    drug_se_df.to_csv('features/drugs-se-sim.csv', index=False)
    print ("Drug side effect similarity --- done")

   

    # ## Drug fingerprint similarity
    # ### calculating MACS based fingerprint (substructure) similarity

    # In[ ]:


    # install following packages oddt and openbabel using conda
    #!conda install -c oddt oddt
    #!conda install -c openbabel openbabel


    # In[133]:


    # In[130]:


    drug_smiles = drug_smiles[drug_smiles.drugid.isin(commonDrugs)]
    drug_smiles.head()


    # In[131]:


    drug_smiles.head()


    # In[134]:

    print ("Drug chemical similarity")
    #Create a dictionary of chemicals to be compared:
    input_dict = dict()
    for index,line in drug_smiles.iterrows():
        id = line['drugid']

        smiles = line['smiles']
        mol = toolkit.readstring(format='smiles',string=smiles)
        fp =mol.calcfp(fptype='MACCS').raw
        input_dict[id] = fp


    # In[135]:


    def tanimoto_score(fp1, fp2):
        return np.sum(fp1 &  fp2) / np.sum(fp1 | fp2)


    # In[136]:


    sim_values=[]
    for chemical1, chemical2 in itertools.combinations(input_dict.keys(),2):
        TC= tanimoto_score(input_dict[chemical1], input_dict[chemical2])
        if chemical1 != chemical2:
            sim_values.append([chemical1, chemical2, TC])


    # In[137]:


    chem_sim_df = pd.DataFrame(sim_values, columns=['Drug1','Drug2','TC'])
    chem_sim_df.head()


    # In[138]:


    chem_sim_df.to_csv('features/drugs-fingerprint-sim.csv', index=False)
    print ("Drug chemical similarity -- done")

    # ## Drug target sequence similarity
    # ### Calculation of SmithWaterman sequence alignment scores

    # In[112]:
    
    print ("Drug target sequence similarity")
    def fasta2seq(lines):
        lines = lines[lines.index('\n')+1:]
        lines =lines.replace('\n','')
        return lines

    target_seq.seq =target_seq.seq.map(fasta2seq)
    target_seq = target_seq[target_seq.geneid.isin(drug_target.geneid)]


    # In[113]:


    target_seq.head()


    # In[114]:


    target_seq_file= os.path.join(abs_path, "data/intermediate/drugbank-target-seq-trimmed.tab")
    target_seq.to_csv(target_seq_file,'\t',index=False,header=None)


    # In[ ]:
    
    target_seq_sim_file=os.path.join(abs_path, "data/intermediate/target-target-seq-sim-biojava.tab")


    os.chdir(abs_path)
    os.system('java -cp .:lib/smithwaterman.jar:lib/biojava-alignment-4.0.0.jar:lib/biojava-core-4.0.0.jar:lib/slf4j-api-1.7.10.jar biojava.targetseq.CalcLocalAlign {0} > {1}'.format(target_seq_file, target_seq_sim_file))

    # In[123]:


    targetSeqSim=dict()
    with open(target_seq_sim_file) as tarSimfile:
        for row in tarSimfile:
            row = row.strip().split("\t")
            t1 =row[0]
            t2 = row[1]
            sim = float(row[2])
            targetSeqSim[(t1,t2)]=sim
            targetSeqSim[(t2,t1)]=sim 


    # In[124]:



    drug_targetlist = {k: g["geneid"].tolist() for k,g in drug_target_seq.groupby("drugid")}
    values = []

    for comb in itertools.combinations(commonDrugs,2) :
        drug1 = comb[0]
        drug2 = comb[1]
        if not(drug1 in drug_targetlist and drug2 in drug_targetlist) : continue
        targetList1 = drug_targetlist[drug1]
        targetList2 = drug_targetlist[drug2]
        allscores =[]
        for target1 in sorted(targetList1):
            genescores = []
            for target2 in sorted(targetList2):
                target1 =str(target1)
                target2 =str(target2)    
                if target1 == target2:
                    score=1.0
                else:
                    score = targetSeqSim[(target1,target2)] / (math.sqrt(targetSeqSim[(target1,target1)]) * math.sqrt(targetSeqSim[(target2,target2)]))
                genescores.append(score)
        # add maximal values between the two lists of associated genes 
        allscores.append(max(genescores))
        if len(allscores) ==0: continue
        #average the maximal scores 
        maxScore =np.mean(allscores)
        values.append([drug1, drug2, maxScore])


    # In[126]:


    drug_seq_df = pd.DataFrame(values, columns =['Drug1','Drug2','TARGETSEQ-SIM'])


    # In[127]:


    drug_seq_df.head()


    # In[151]:

    
    os.chdir(temp_folder)
    drug_seq_df.to_csv('features/drugs-target-seq-sim.csv', index=False)
    print ("Drug target sequence similarity  -- done")

    # ## GO based drug-drug similarity

    # In[45]:

    print ("GO based drug-drug similarity")
    drug_goa.drugid = drug_goa.drugid.map(lambda d: 'http://purl.obolibrary.org/obo/'+d)
    #drug_goa.to_csv('intermediate/drug_goa.txt',sep='\t', header=False, index=False)


    # In[37]:


    #cleaning GO annotations
    rows = []
    for comb in itertools.combinations(commonDrugs,2):
        t1=comb[0]
        t2=comb[1]
        rows.append(['http://purl.obolibrary.org/obo/'+str(t1),'http://purl.obolibrary.org/obo/'+str(t2)])


    # In[46]:


    drug_query_df = pd.DataFrame(rows, columns =['Drug1','Drug2'])
    drug_query_df.to_csv(os.path.join(abs_path, 'data/intermediate/drug.gene.go.query'),sep='\t', header=False, index=False)


    # In[47]:


    ### run the semantic relatedness library with given query and anotation file it will produce a file named: gene.go.sim.out
    os.chdir(abs_path)
    os.system('java -jar lib/sml-toolkit-0.9.jar -t sm -xmlconf data/conf/sml.gene.go.conf')
    os.chdir(temp_folder)

    # In[108]:


    go_sim_df = pd.read_csv(os.path.join(abs_path, 'data/intermediate/drug.gene.go.sim.out'),sep='\t')
    go_sim_df.head()


    # In[109]:


    go_sim_df.rename(columns={'e1':'Drug1','e2':'Drug2','bma':'GO-SIM'}, inplace=True)


    # In[110]:


    go_sim_df.Drug1 = go_sim_df.Drug1.str.replace('http://purl.obolibrary.org/obo/','')
    go_sim_df.Drug2 = go_sim_df.Drug2.str.replace('http://purl.obolibrary.org/obo/','')
    go_sim_df.head()


    # In[111]:


    go_sim_df.to_csv(os.path.join(temp_folder, 'features/drugs-target-go-sim.csv'))
    print ("GO based drug-drug similarity  --  done")

 


    # In[140]:

    
     # ## PPI based drug-drug similarity
    # ###  calculate distance between drugs on protein-protein interaction network

    # In[47]:


    #!pip install -q networkx==1.11


    # In[30]:

    print ("PPI based drug-drug similarity")
    # calcuate pairwise distance between proteins in the human PPI network
    import networkx as nx
    G= nx.Graph()
    with open(os.path.join(temp_folder, args.protein_interactions)) as ppiFile: # human PPI network
        next(ppiFile) # skip first line
        drugs=set()
        for line in ppiFile:
            line=line.replace("'","").strip().split(',')
            G.add_edge(line[0],line[1])


    # In[31]:


    ppi=nx.shortest_path_length(G)


    # In[32]:



    def grapDistance(ppi, target1, target2):
        """
        return the shortest path between two proteins in the PPI network
        ppi : dictonary that contains distance of PPI 
        target1 : first protein name
        target2 : second protein name
        """
        maxValue = 9999
        if target1 not in ppi:
            return maxValue
        else:
            if target2 not in ppi[target1]:
                return maxValue
            else:
                return ppi[target1][target2]

    drug_targetlist = {k: g["geneid"].tolist() for k,g in drug_target.groupby("drugid")}
    values = []

    # calculate PPI-based pairwise drug similarity (Closeness)
    # First distances between proteins were transformed to similarity values using the formula described in Perlman et al (2011)
    # A, b were chosen according to Perlman et al (2011) to be 0.9 × e and 1, respectively.
    # Self similarity was assigned a value of 1.

    # For drugs similarities, maximal values between the two lists of associated genes were averaged 
    # (taking into account both sides for symmetry).

    A = 0.9
    b = 1
    for comb in itertools.combinations(commonDrugs,2) :
        drug1 = comb[0]
        drug2 = comb[1]
        targetList1 = drug_targetlist[drug1]
        targetList2 = drug_targetlist[drug2]
        allscores =[]
        for target1 in sorted(targetList1):
            genescores = []
            for target2 in sorted(targetList2):
                target1 =str(target1)
                target2 =str(target2)    
                if target1 == target2:
                    score=1.0
                else:
                    score = A*math.exp(-b* grapDistance(ppi, target1, target2))
                genescores.append(score)
        # add maximal values between the two lists of associated genes 
        allscores.append(max(genescores))
        if len(allscores) ==0: continue
        #average the maximal scores 
        maxScore =np.mean(allscores)
        if maxScore >= 0:
            values.append([drug1, drug2, maxScore])


    # In[33]:


    drug_ppi_df = pd.DataFrame(values, columns =['Drug1','Drug2','PPI-SIM'])


    # In[34]:


    drug_ppi_df.head()


    # In[35]:

    
    drug_ppi_df.to_csv(os.path.join(temp_folder, 'features/drugs-ppi-sim.csv'), index=False)
    print ("PPI based drug-drug similarity --  done")
    
    
    # In[142]:
    
    predict_df.rename(columns={'drugid':'Drug','omimid':'Disease'}, inplace=True)


    # In[141]:


    gold_diseases = set( predict_df.Disease.unique())
    print ('Gold std. diseases',len(gold_diseases))

    # ## Disease Phenotype Similarity
    # ### MESH term based Similarity
    print ("MESH term based Similarity")

    mesh_ann = {}
    allmeshterm = []
    with open(os.path.join(temp_folder, args.mesh_annotation)) as meshfile:
        next(meshfile)
        for line in meshfile:
            line = line.strip().split(',')
            if len(line) != 2: continue
            di = line[0]
            mesh = line[1].split(',')
            mesh_ann[di]=mesh
            allmeshterm.extend(mesh)


    # In[143]:


    vocabulary = list(set(allmeshterm))
    len(vocabulary)


    # In[144]:


    # create a co-occurrence matrix
    co_mat = np.zeros((len(mesh_ann),len(vocabulary)))


    # In[145]:


    commonDiseases = mesh_ann.keys()
    mesh2id= { di:i for i,di in enumerate(mesh_ann.keys())}
    # fill in the co-occurrence matrix
    for key in mesh_ann:
        annotations = mesh_ann[key]
        col_index = [vocabulary.index(a) for a in annotations]
        co_mat[mesh2id[key],col_index] =1


    # In[146]:


    def cosine_similarity(a,b):
        return  np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))


    # In[147]:


    values = []
    # calculate cosine similarity between diseases using mesh annotation vector
    for comb in itertools.combinations(commonDiseases,2) :
        disease1 = comb[0]
        disease2 = comb[1]
        sim = cosine_similarity(co_mat[mesh2id[disease1],:], co_mat[mesh2id[disease2],:])
        values.append([disease1, disease2, sim])


    # In[148]:


    disease_pheno_df = pd.DataFrame(values, columns =['Disease1','Disease2','PHENO-SIM'])


    # In[149]:


    disease_pheno_df.head()


    # In[150]:


    disease_pheno_df.to_csv(os.path.join(temp_folder,'features/diseases-pheno-sim.csv'),index=False)
    print ("MESH term based Similarity --  done")

    # ## HPO based disease-disease similarity

    # In[69]:


    # reading the hpo annotation file taken from compbio.charite.de/jennkins/jobs/hpo.annotations/
    #disease_hpo = pd.read_csv('data/input/omim-disease-hpo.csv')
    #disease_hpo.head()


    # In[70]:

    print ("HPO term based Similarity")
    disease_hpo.rename(columns={'diseaseid':'Disease','hpoid':'HPO'}, inplace=True)
    disease_hpo.HPO= disease_hpo.HPO.str.replace('hpo','hp')


    # In[71]:


    disease_hpo.head()


    # In[72]:


    diseasesWithFeatures= set(disease_hpo.Disease.unique()).intersection( gold_diseases )
    print (len(diseasesWithFeatures))
    rows = []
    for comb in itertools.combinations(diseasesWithFeatures,2):
        t1=comb[0]
        t2=comb[1]
        rows.append(['omim:'+str(t1),'omim:'+str(t2)])


    # In[73]:


    disease_hpo["Disease"]=disease_hpo["Disease"].map(lambda d: 'omim:'+str(d))
    disease_hpo.to_csv(os.path.join(abs_path, 'data/intermediate/disease_hpo.txt'),sep='\t', header=False, index=False)


    # In[74]:


    disease_query_df = pd.DataFrame(rows, columns =['Disease1','Disease2'])
    disease_query_df.to_csv(os.path.join(abs_path, 'data/intermediate/hpo.sml.omim.query'),sep='\t', header=False, index=False)


    # In[77]:
    
    os.chdir(abs_path)
    ### run the semantic relatedness library with given query and anotation file it will produce a file named: hpo.sim.out
    os.system('java -jar lib/sml-toolkit-0.9.jar -t sm -xmlconf data/conf/sml.omim.hpo.conf')
    os.chdir(temp_folder)

    # In[101]:


    hpo_sim_df = pd.read_csv(os.path.join(abs_path,'data/intermediate/omim.hpo.sim.out'),sep='\t')


    # In[102]:


    hpo_sim_df.head()


    # In[104]:


    hpo_sim_df.rename(columns={'e1':'Disease1','e2':'Disease2','bma':'HPO-SIM'}, inplace=True)


    # In[106]:


    hpo_sim_df.Disease1 = hpo_sim_df.Disease1.str.replace('omim:','')
    hpo_sim_df.Disease2 = hpo_sim_df.Disease2.str.replace('omim:','')
    hpo_sim_df.head()


    # In[107]:


    hpo_sim_df.to_csv(os.path.join(temp_folder,'features/diseases-hpo-sim.csv'), index=False)
    print ("HPO term based Similarity --  done")

    # In[ ]:




