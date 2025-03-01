# skeeball-agent Infrastructure Deployment

This directory (`infra`) contains the Terraform configuration to deploy the infrastructure for the skeeball-agent project. It provisions a Google Cloud Pub/Sub topic, subscription, and a Google Cloud Storage bucket with public access prevention enabled.

## Prerequisites

1.  **Google Cloud Account:** You need an active Google Cloud account with appropriate permissions to create Pub/Sub resources and GCS buckets.
2.  **Google Cloud Credentials:** Your Google Cloud credentials need to be configured. This is typically done by setting up Application Default Credentials (ADC) or using a service account key file.
3.  **Terraform:** Terraform must be installed on your system. You can download it from the official Terraform website: [https://www.terraform.io/downloads.html](https://www.terraform.io/downloads.html)
4.  **Git:** Make sure you have git installed as well.
5.  **Project ID and Region:** You will need to know your project ID and choose a region. You will need to edit a tfvars file to select the project ID and region.

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

3.  **Set your Project ID and Region:**
    Ensure you have created a `*.auto.tfvars` file, (for example `dev.auto.tfvars`) and have added your google project ID and region to it. For example:
    ```
    project_id = "my-project"
    region = "us-central1"
    ```
4.  **Plan the Deployment:**
    ```bash
    terraform plan
    ```
    This command shows you a preview of the resources that Terraform will create, modify, or destroy. Review the plan carefully to ensure it matches your expectations.

5.  **Apply the Configuration:**
    ```bash
    terraform apply
    ```
    This command applies the Terraform configuration and creates the resources in your Google Cloud account. You will be prompted to confirm the action by typing `yes`.

6.  **Accessing the Resources:**
    After the deployment is complete, Terraform will output the name of the Pub/Sub topic, subscription, and the storage bucket. You can find it in the command line output under the heading `Outputs`.
    ```
    Outputs:
    bucket_name = "skeeball-agent-bucket-abcd"
    pubsub_subscription_name = "skeeball-agent-subscription"
    pubsub_topic_name = "skeeball-agent-topic"
    ```

## Destroying the Infrastructure

To destroy the infrastructure you created:

```bash
terraform destroy
