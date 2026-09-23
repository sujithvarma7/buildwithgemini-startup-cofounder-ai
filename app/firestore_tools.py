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
import json
import uuid
import google.auth
from google.cloud import firestore

# Hardcoded project ID as required for Agent Platform deployment
PROJECT_ID = "qwiklabs-gcp-03-f53b15124fc6"
COLLECTION_NAME = "business_artifacts"


def _get_firestore_client() -> firestore.Client:
    """Initialize Firestore client using hardcoded GCP project ID."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return firestore.Client(project=PROJECT_ID, credentials=credentials)


def list_business_artifacts(artifact_type: str = "") -> str:
    """Read business artifacts from the Firestore database.

    Args:
        artifact_type: Optional filter by artifact type (e.g. 'customer_persona',
                       'pricing_tier', 'competitor_matrix', 'gtm_milestone').
                       Pass empty string to list all artifacts.

    Returns:
        JSON string containing the list of matching business artifacts.
    """
    db = _get_firestore_client()
    collection_ref = db.collection(COLLECTION_NAME)

    if artifact_type and artifact_type.strip():
        query_ref = collection_ref.where("artifact_type", "==", artifact_type.strip())
        docs = query_ref.stream()
    else:
        docs = collection_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    return json.dumps(results, indent=2)


def save_business_artifact(
    title: str,
    artifact_type: str,
    summary: str,
    details_json: str = "{}"
) -> str:
    """Save or update a business artifact in the Firestore database.

    Args:
        title: Title of the artifact (e.g. 'Enterprise Pricing Model').
        artifact_type: Type of artifact ('customer_persona', 'pricing_tier',
                       'competitor_matrix', 'gtm_milestone').
        summary: Concise summary of what this artifact represents.
        details_json: Optional JSON string of key-value details.

    Returns:
        A confirmation message with the document ID.
    """
    db = _get_firestore_client()
    doc_id = f"artifact-{uuid.uuid4().hex[:8]}"

    try:
        details_dict = json.loads(details_json) if details_json else {}
    except Exception:
        details_dict = {"raw_details": details_json}

    doc_data = {
        "id": doc_id,
        "title": title,
        "artifact_type": artifact_type,
        "summary": summary,
        "details": details_dict,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    db.collection(COLLECTION_NAME).document(doc_id).set(doc_data)
    return f"Successfully saved business artifact '{title}' with ID '{doc_id}'."
