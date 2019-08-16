#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow

inputs:
    
  sparql_ep:
     type: string
       
  dt_sparql_path:
      type: string
  
  dt_download_path:
     type: string
     
  ds_sparql_path:
      type: string
  
  ds_download_path:
     type: string
     
  goa_sparql_path:
      type: string
  
  goa_download_path:
     type: string
     
  di_sparql_path:
      type: string
  
  di_download_path:
     type: string
     
  ppi_sparql_path:
      type: string
  
  ppi_download_path:
     type: string
     
  tseq_sparql_path:
      type: string
  
  tseq_download_path:
     type: string
  
  se_sparql_path:
      type: string
  
  se_download_path:
     type: string
    

  mesh_sparql_path:
      type: string
  
  mesh_download_path:
     type: string
     
  hpo_sparql_path:
      type: string
  
  hpo_download_path:
     type: string

  ab_path:
     type: string
     
#  se_output:
#    type: string
    
# seq_sim_output:
#    type: string
 

outputs:
        
    drug_target:
        type: File
        outputSource:  download-and-save-drug-targets/downloaded_file
    
    drug_target_seq:
        type: File
        outputSource:  download-and-save-drug-target-seq/downloaded_file
        
    drug_smiles:
        type: File
        outputSource:  download-and-save-drug-smiles/downloaded_file
        
    drug_target_goa:
        type: File
        outputSource:  download-and-save-drug-goa/downloaded_file
        
    drug_se:
        type: File
        outputSource:  download-and-save-side-effects/downloaded_file
        
    drug_ind:
        type: File
        outputSource:  download-and-save-openpredict-drug-ind/downloaded_file
        
    drug_ppi:
        type: File
        outputSource:   download-and-save-human-interactome/downloaded_file
        
    disease_mesh:
        type: File
        outputSource:   download-and-save-omim-disease-mesh/downloaded_file
        
    disease_hpo:
        type: File
        outputSource:   download-and-save-omim-disease-hpo/downloaded_file

    features_dir:
        type: Directory
        outputSource:   feature-generation/features_out
        
    results_dir:
        type: Directory
        outputSource:   machine-learning/ml_out

steps:

    download-and-save-drug-targets:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : dt_sparql_path
          output : dt_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-drug-smiles:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : ds_sparql_path
          output : ds_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-drug-goa:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : goa_sparql_path
          output : goa_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-side-effects:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : se_sparql_path
          output : se_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-openpredict-drug-ind:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : di_sparql_path
          output : di_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-human-interactome:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : ppi_sparql_path
          output : ppi_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-drug-target-seq:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : tseq_sparql_path
          output : tseq_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-omim-disease-mesh:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : mesh_sparql_path
          output : mesh_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    download-and-save-omim-disease-hpo:
      run: steps/download-and-save.cwl
      in :
          abs_path : ab_path
          input : hpo_sparql_path
          output : hpo_download_path
          sparql_endpoint : sparql_ep
      out : 
          [downloaded_file]
          
    feature-generation:
      run: steps/feature-generation.cwl
      in:
          drug_target:  download-and-save-drug-targets/downloaded_file
          drug_seq:  download-and-save-drug-target-seq/downloaded_file
          drug_smiles:   download-and-save-drug-smiles/downloaded_file
          drug_se:  download-and-save-side-effects/downloaded_file
          drug_ind:  download-and-save-openpredict-drug-ind/downloaded_file
          drug_goa:  download-and-save-drug-goa/downloaded_file
          drug_ppi:  download-and-save-human-interactome/downloaded_file
          disease_mesh:  download-and-save-omim-disease-mesh/downloaded_file
          disease_hpo:  download-and-save-omim-disease-hpo/downloaded_file
          abs_path : ab_path
      out:
          [features_out]
   
    
    machine-learning:
        run:  steps/machine-learning.cwl
        in:
            drug_ind:  download-and-save-openpredict-drug-ind/downloaded_file
            features: feature-generation/features_out
            abs_path : ab_path
        out:
            [ml_out]

            

      
    
