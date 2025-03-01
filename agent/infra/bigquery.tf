# /Users/jasondavenport/Github/skeeball-agent/infra/bigquery.tf

resource "google_bigquery_dataset" "default" {
  dataset_id                  = "skeeball_agent_dataset"
  project                     = var.project_id
  location                    = var.region
  description                     = "Dataset for data related to the skeeball-agent."

  labels = {
    environment = "dev"  # Customize as needed
    managed_by = "terraform"
  }
}

