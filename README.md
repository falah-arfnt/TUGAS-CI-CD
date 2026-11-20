# Sales Data CI/CD Pipeline

## Project Description

This project implements a CI/CD pipeline for sales data ingestion
using Python, GitHub Actions, and Microsoft Azure Blob Storage.

## Dataset

The project uses dummy sales transaction data from April to September 2026.

## Technologies

- Python
- Git
- GitHub
- GitHub Actions
- Microsoft Azure Blob Storage

## Pipeline Workflow

1. Dataset is stored in the GitHub repository.
2. Python validates and processes the dataset.
3. GitHub Actions automatically executes the pipeline.
4. Processed data is uploaded to Azure Blob Storage.

## Automation

The pipeline is triggered by:
- Push events to the main branch
- Scheduled execution every 6 hours
- Manual workflow execution