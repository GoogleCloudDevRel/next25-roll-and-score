# /Users/jasondavenport/Github/skeeball-agent/infra/storage.tf

resource "google_storage_bucket" "default" {
  project                     = var.project_id
  name                        = "skeeball-agent-bucket-${random_id.bucket_suffix.hex}"
  location                    = var.region
  public_access_prevention    = "enforced"
  force_destroy               = true # Change to true if you want to delete non-empty buckets
  uniform_bucket_level_access = true
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
