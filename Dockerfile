# Use an official Python runtime as a parent image
FROM python:3.9-slim


ARG BASE=master
ENV ROOT_PATH /pic_search
RUN mkdir -p /vol/cache
RUN chmod -R 777 /vol/cache


RUN git clone https://github.com/abishek21/pic_search.git --branch ${BASE} ${ROOT_PATH}


# Set the working directory in the container
WORKDIR /pic_search

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
