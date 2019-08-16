#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

label: Remzi Celebl (IDS)

baseCommand: [curl]

arguments: [ "-H", "Accept: text/csv","--data-urlencode", "query@$(inputs.abs_path)data/sparql/$(inputs.input)" , "$(inputs.sparql_endpoint)", "-o", "$(runtime.outdir)/$(inputs.output)"]

inputs:
    
    abs_path :
        type: string
        
    sparql_endpoint : 
        type : string
    
    input:
        type: string
        
    output:
        type: string

outputs:
     
    downloaded_file:
        type: File
        outputBinding:
          glob: $(inputs.output)