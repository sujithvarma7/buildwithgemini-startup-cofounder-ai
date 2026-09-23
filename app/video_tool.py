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

import base64
import uuid
import google.auth
from google.cloud import storage
from google.genai import Client, types
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-f53b15124fc6"
LOCATION = "global"
BUCKET_NAME = "startup-cofounder-ai-assets-qwiklabs-gcp-03-f53b15124fc6"


async def generate_startup_promo_video(prompt: str, tool_context: ToolContext) -> str:
    """Generate a short promotional video for a startup item using Google's
    Omni model (gemini-omni-flash-preview) in the global region, save it as an ADK
    artifact via tool_context, and upload it to Cloud Storage.

    Args:
        prompt: Detailed video prompt describing the promo or teaser video to generate
                (e.g., 'A short promo video teaser for a SaaS AI code review product').

    Returns:
        The public HTTPS Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>)
        of the generated video.
    """
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=credentials)

    res = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=f"Generate a short promo video teaser for startup: {prompt}"
    )

    video_bytes = None
    if hasattr(res, "steps") and res.steps:
        for step in res.steps:
            if getattr(step, "type", None) == "model_output":
                for content in getattr(step, "content", []):
                    raw_data = getattr(content, "data", None)
                    if raw_data:
                        if isinstance(raw_data, bytes):
                            video_bytes = raw_data
                        elif isinstance(raw_data, str):
                            video_bytes = base64.b64decode(raw_data)
                        break

    if not video_bytes:
        return "Error: Could not generate promo video for the prompt."

    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

    # (1) Save video bytes as artifact with tool_context.save_artifact
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    await tool_context.save_artifact(filename, artifact_part)

    # (2) Upload video bytes directly to public GCS bucket
    gcs_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
