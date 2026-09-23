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

import uuid
import google.auth
from google.cloud import storage
from google.genai import Client, types
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-f53b15124fc6"
LOCATION = "global"
BUCKET_NAME = "startup-cofounder-ai-assets-qwiklabs-gcp-03-f53b15124fc6"


def generate_startup_image(prompt: str) -> str:
    """Generate a visual asset (logo, branding graphic, marketing banner, diagram)
    for the startup using AI image generation and upload it to Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the image to generate
                (e.g., 'A modern minimalist logo for Novalab AI').

    Returns:
        A string containing the public HTTPS URL of the generated image.
    """
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=credentials)
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"Generate an image: {prompt}",
        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
    )

    image_bytes = None
    if res.candidates and res.candidates[0].content and res.candidates[0].content.parts:
        for part in res.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break

    if not image_bytes:
        return "Error: Could not generate image for the prompt."

    filename = f"asset_{uuid.uuid4().hex[:8]}.png"
    gcs_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Successfully generated startup image. Public URL: {public_url}"


async def generate_startup_artifact_image(prompt: str, tool_context: ToolContext) -> str:
    """Generate a visual branding asset or logo for the startup using gemini-3.1-flash-lite-image
    in the global region, save it as an ADK artifact via tool_context, and upload it to Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the image to generate
                (e.g., 'A sleek tech startup logo for Novalab AI').

    Returns:
        The public HTTPS Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>)
        of the generated image.
    """
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=credentials)

    res = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"Generate an image for startup: {prompt}",
        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
    )

    image_bytes = None
    if res.candidates and res.candidates[0].content and res.candidates[0].content.parts:
        for part in res.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break

    if not image_bytes:
        return "Error: Could not generate image for the prompt."

    filename = f"artifact_{uuid.uuid4().hex[:8]}.png"

    # (1) Save with tool_context.save_artifact
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    await tool_context.save_artifact(filename, artifact_part)

    # (2) Upload to public Cloud Storage bucket
    gcs_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
