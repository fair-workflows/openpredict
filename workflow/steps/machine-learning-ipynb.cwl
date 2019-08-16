cwlVersion: cwl:v1.0
class: CommandLineTool

requirements:
 - class: InitialWorkDirRequirement
   listing:
     - entry: features
       writable: true

baseCommand: [papermill]
arguments: [ "$(inputs.abs_path)OpenPREDICT - ML.ipynb", "-p","temp","$(runtime.outdir)", "$(inputs.abs_path)output_ml.ipynb", "-p","abs_path","$(inputs.abs_path)", "-p","drug_ind","$(inputs.drug_ind)", "-p","feature_folder","$(inputs.features)"]

inputs:

  abs_path:
      type: string
      
  drug_ind:
    type: File
      
  features:
    type: Directory
   
  
outputs:                                                                                                                 
  ml_out:
    type: Directory
    outputBinding:
      glob: "$(runtime.outdir)/results"


