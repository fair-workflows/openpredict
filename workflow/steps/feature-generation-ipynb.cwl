cwlVersion: cwl:v1.0
class: CommandLineTool

requirements:
 - class: InitialWorkDirRequirement
   listing:
     - entry: features

baseCommand: [papermill]
arguments: [ "$(inputs.abs_path)FeatureGeneration.ipynb", "$(inputs.abs_path)output_fg.ipynb", "-p", "abs_path","$(inputs.abs_path)",
"-p","temp","$(runtime.outdir)", "-p","drug_target","$(inputs.drug_target)",
"-p","drug_seq","$(inputs.drug_seq)", "-p","drug_smiles","$(inputs.drug_smiles)", "-p","drug_se","$(inputs.drug_se)", "-p","drug_se","$(inputs.drug_se)",
"-p","drug_ind","$(inputs.drug_ind)", "-p","drug_ppi","$(inputs.drug_ppi)",  "-p","drug_goa","$(inputs.drug_goa)",  "-p","disease_mesh","$(inputs.disease_mesh)",
 "-p","disease_hpo","$(inputs.disease_hpo)"]

inputs:

  abs_path:
      type: string
      
  drug_target:
    type: File
      
  drug_seq:
    type: File
      
  drug_smiles:
    type: File
      
  drug_se:
    type: File
      
  drug_ind:
    type: File
      
  drug_ppi:
    type: File
      
  drug_goa:
    type: File
      
  disease_mesh:
    type: File
      
  disease_hpo:
    type: File
   
  
outputs:                                                                                                                 
  features_out:
    type: Directory
    outputBinding:
      glob: "$(runtime.outdir)/features"


