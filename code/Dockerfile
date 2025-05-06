FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    git \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Miniconda (with Python 3.10)
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_24.1.2-0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    conda clean -afy

WORKDIR /app

RUN conda install -y -c conda-forge yarp
RUN pip install openai pillow 

RUN curl -fsSL https://ollama.com/install.sh | sh
ENV PATH="/root/.ollama/bin:$PATH"

RUN pip install --no-input git+https://github.com/huggingface/transformers
RUN pip install --no-input qwen-vl-utils[decord]==0.0.8

RUN git clone https://github.com/CarmelaCalabrese/LLM4planning.git