FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

# Set environment variables and time zone
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/New_York

# Set the time zone, non-interactively
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y wget git libglib2.0-0 libsm6 libxext6 libxrender-dev

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

# Add Conda to PATH
ENV PATH /opt/conda/bin:$PATH

# Create a new Conda environment and install PyTorch and other dependencies
RUN conda create -n myenv python=3.9 -y
RUN echo "source activate myenv" >~/.bashrc
ENV PATH /opt/conda/envs/myenv/bin:$PATH


# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run FastAPI application
CMD ["bash", "-c", "source activate myenv && conda install -y pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch-nightly -c nvidia && uvicorn api:app --host 0.0.0.0 --port 8000"]

