# skeeball-agent Infrastructure Deployment

This directory (`infra`) contains the Terraform configuration to deploy the infrastructure for the skeeball-agent project. It provisions a Google Cloud Pub/Sub topic and subscription.

## Prerequisites

1.  **Google Cloud Account:** You need an active Google Cloud account with appropriate permissions to create Pub/Sub resources.
2.  **Google Cloud Credentials:** Your Google Cloud credentials need to be configured. This is typically done by setting up Application Default Credentials (ADC) or using a service account key file.
3.  **Terraform:** Terraform must be installed on your system. You can download it from the official Terraform website: [https://www.terraform.io/downloads.html](https://www.terraform.io/downloads.html)
4. **Git:** Make sure you have git installed as well.
5. **Project ID and Region:** You will need to know your project ID and choose a region. You will need to edit a tfvars file to select the project ID and region.

## Deployment Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd skeeball-agent/infra
    ```
    Replace `<repository_url>` with the actual URL of your repository.

2.  **Initialize Terraform:**
    ```bash
    terraform init
    ```
    This command initializes your Terraform working directory and downloads the necessary Google provider plugins.

3. **Create a tfvars file:**
Create a file named something like `dev.auto.tfvars`. For example, create a new file `dev.auto.tfvars` in the same directory, and add the following:
