# /Users/jasondavenport/Github/skeeball-agent/infra/outputs.tf

output "pubsub_topic_name" {
  value       = google_pubsub_topic.default.name
  description = "The name of the Pub/Sub topic."
}

output "pubsub_subscription_name" {
  value       = google_pubsub_subscription.default.name
  description = "The name of the Pub/Sub subscription."
}

output "bucket_name" {
    value = google_storage_bucket.default.name
    description = "The name of the storage bucket"
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.default.id
  description = "The ID of the created BigQuery dataset."
}
