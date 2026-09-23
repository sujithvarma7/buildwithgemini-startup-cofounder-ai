# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import google.auth
from google.cloud import firestore

# Hardcoded project ID as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-03-f53b15124fc6"
COLLECTION_NAME = "business_artifacts"

SEED_DATA = [
    {
        "id": "artifact-persona-01",
        "title": "Ideal Customer Persona - DevTools Founder",
        "artifact_type": "customer_persona",
        "summary": "Technical founder building AI-agent developer tools seeking market validation and GTM guidance.",
        "details": {
            "target_role": "Technical Founder / CTO",
            "company_stage": "Pre-seed / Seed",
            "primary_pain_point": "Lacks business background and marketing playbook",
            "key_goals": ["Validate pricing models", "Identify target enterprise buyer", "Build GTM roadmap"]
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "id": "artifact-pricing-01",
        "title": "SaaS Tiered Pricing Strategy",
        "artifact_type": "pricing_tier",
        "summary": "3-tiered subscription model designed for B2B developer tool platforms.",
        "details": {
            "tier_free": "$0/mo - Up to 1,000 API calls/month, community support",
            "tier_pro": "$49/mo - 50,000 API calls/month, priority support, custom workflows",
            "tier_enterprise": "Custom/mo - Dedicated SLA, VPC deployment, SSO & SOC2"
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "id": "artifact-competitor-01",
        "title": "AI Agent DevTools Competitor Matrix",
        "artifact_type": "competitor_matrix",
        "summary": "Competitive landscape overview comparing developer experience, integrations, and pricing.",
        "details": {
            "direct_competitors": ["AgentFramework A", "ToolSmith AI"],
            "key_differentiators": ["Native Vertex AI integration", "Built-in long-term memory", "Automated GTM templates"],
            "market_positioning": "Premium Enterprise-grade Agent Operations Platform"
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]


def seed_firestore():
    """Seed the Firestore business_artifacts collection with initial data."""
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_DATA:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded document: {doc_id} -> {item['title']}")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
