
# Base images. Built on latest ubuntu version. Requires python.
FROM python:3.8-slim-buster
RUN apt-get update

MAINTAINER i.dudurych@rug.nl

# Install dicom to nifty conversion tools.
RUN apt-get install -y dcm2niix
RUN apt-get install -y dcmtk

# Copy the required source files to the image.
# TODO choose which model to include, the pre-trained model in the repo or a custom model. 
WORKDIR /app
COPY ./src/ ./src/
COPY ./model_to_dockerise/ ./models/
# COPY ./models/ ./models/
COPY requirements.txt requirements.txt
COPY test_environment.py test_environment.py

# Install the requirements and test.
# RUN pip3 install -r requirements.txt
RUN python test_environment.py

# Set up the file structure for CT scan processing.
ENV PYTHONPATH "./src"
RUN ls ${PYTHONPATH}
RUN ln -s ./src Code
RUN mkdir ./scan
RUN ln -s ./scan BaseData

# Create the folders where scan files will go.
RUN mkdir ./scan/Images
RUN mkdir ./scan/CoarseAirways
RUN mkdir ./scan/Lungs
