cwlVersion: cwl:v1.0
class: CommandLineTool

requirements:
 - class: InitialWorkDirRequirement
   listing:
     - entry: features
       writable: true

baseCommand: [python]
arguments: [ "$(inputs.abs_path)src/OpenPREDICT_ML.py"]

inputs:

  abs_path:
      type: string
      
  drug_ind:
    type: File
    inputBinding:
      prefix: -g
      
  features:
    type: Directory
    inputBinding:
      prefix: -ff
   
  
outputs:                                                                                                                 
  ml_out:
    type: Directory
    outputBinding:
      glob: "$(runtime.outdir)/results"


