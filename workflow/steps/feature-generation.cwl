cwlVersion: cwl:v1.0
class: CommandLineTool

requirements:
 - class: InitialWorkDirRequirement
   listing:
     - entry: features
       writable: true

baseCommand: [python]
arguments: [ "$(inputs.abs_path)src/FeatureGeneration.py","-t","$(runtime.outdir)", "-a","$(inputs.abs_path)"]

inputs:

  abs_path:
      type: string
      
  drug_target:
    type: File
    inputBinding:
      prefix: -dt
      
  drug_seq:
    type: File
    inputBinding:
      prefix: -tseq
      
  drug_smiles:
    type: File
    inputBinding:
      prefix: -ds
      
  drug_se:
    type: File
    inputBinding:
      prefix: -se
      
  drug_ind:
    type: File
    inputBinding:
      prefix: -di
      
  drug_ppi:
    type: File
    inputBinding:
      prefix: -ppi
      
  drug_goa:
    type: File
    inputBinding:
      prefix: -goa
      
  disease_mesh:
    type: File
    inputBinding:
      prefix: -mesh
      
  disease_hpo:
    type: File
    inputBinding:
      prefix: -hpo
   
  
outputs:                                                                                                                 
  features_out:
    type: Directory
    outputBinding:
      glob: "$(runtime.outdir)/features"


