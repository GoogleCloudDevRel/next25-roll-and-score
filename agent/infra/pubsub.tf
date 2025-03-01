# /Users/jasondavenport/Github/skeeball-agent/infra/main.tf

# Create a Pub/Sub topic
resource "google_pubsub_topic" "default" {
  project = var.project_id
  name    = "skeeball-agent-topic"
}

# Create a Pub/Sub subscription
resource "google_pubsub_subscription" "default" {
  project = var.project_id
  name    = "skeeball-agent-subscription"
  topic   = google_pubsub_topic.default.name
  ack_deadline_seconds = 20
}
