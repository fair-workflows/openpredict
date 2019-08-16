FROM dclong/jupyterlab-spark:latest

USER root

WORKDIR /tmp

COPY requirements.txt .

RUN pip install --upgrade pip && \
  pip3 install -r requirements.txt
  
RUN conda install -c oddt oddt && \
    conda install -c openbabel openbabel && \
    conda install -c bioconda cwltool
