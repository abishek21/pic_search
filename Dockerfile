# Use an official Python runtime as a parent image
FROM python:3.9.0-slim


ARG BASE=main
ENV ROOT_PATH /pic_search

# Install Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /vol/cache
RUN chmod -R 777 /vol/cache


RUN git clone https://github.com/abishek21/pic_search.git --branch ${BASE} ${ROOT_PATH}


# Set the working directory in the container
WORKDIR /pic_search

# Install necessary packages including specific versions of torch, torchvision, and torchaudio from the CPU-only index
RUN pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/pic_search"
ENV PYTHONUNBUFFERED 1

# Make port 5000 available to the world outside this container
EXPOSE 5000

RUN chmod +x /start.sh

# Run the Flask app
#CMD ["python", "run.py"]
CMD ["/start.sh"]
