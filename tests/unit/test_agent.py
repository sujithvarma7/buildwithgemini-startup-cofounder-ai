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

import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from app.agent import root_agent, get_weather, get_current_time
from app.a2ui_utils import a2ui_callback
from app.firestore_tools import list_business_artifacts, save_business_artifact
from app.image_tool import generate_startup_artifact_image, generate_startup_image
from app.maps_tools import find_nearby_places, geocode_address
from app.public_api_tool import search_startup_market_trends


class TestAgent(unittest.IsolatedAsyncioTestCase):

    def test_agent_initialization(self) -> None:
        """Test root_agent name, tools, code executor, and A2UI callback."""
        self.assertEqual(root_agent.name, "root_agent")
        self.assertEqual(len(root_agent.tools), 10)
        self.assertIsInstance(root_agent.code_executor, AgentEngineSandboxCodeExecutor)
        self.assertIn("projects/qwiklabs-gcp-03-f53b15124fc6", root_agent.code_executor.agent_engine_resource_name)
        self.assertEqual(root_agent.after_model_callback, a2ui_callback)

    def test_get_weather_sf(self) -> None:
        """Test get_weather tool for San Francisco."""
        res = get_weather("San Francisco")
        self.assertIn("60 degrees and foggy", res)

    def test_get_current_time_sf(self) -> None:
        """Test get_current_time tool for San Francisco."""
        res = get_current_time("San Francisco")
        self.assertTrue("PDT" in res or "PST" in res or "202" in res)

    def test_list_business_artifacts(self) -> None:
        """Test reading business artifacts from Firestore."""
        res = list_business_artifacts()
        parsed = json.loads(res)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)

    def test_save_business_artifact(self) -> None:
        """Test saving a new business artifact to Firestore."""
        res = save_business_artifact(
            title="Unit Test Milestone",
            artifact_type="gtm_milestone",
            summary="Unit test GTM milestone artifact",
            details_json='{"quarter": "Q4"}'
        )
        self.assertIn("Successfully saved business artifact", res)

    def test_generate_startup_image(self) -> None:
        """Test generating an image and uploading to GCS."""
        res = generate_startup_image("A minimalist tech logo for Novalab AI")
        self.assertIn("Successfully generated startup image. Public URL: https://storage.googleapis.com/", res)

    async def test_generate_startup_artifact_image(self) -> None:
        """Test generating an image, saving as ADK artifact, and uploading to GCS."""
        mock_tool_context = MagicMock()
        mock_tool_context.save_artifact = AsyncMock()

        res = await generate_startup_artifact_image("A high tech logo for Novalab AI", mock_tool_context)
        self.assertTrue(res.startswith("https://storage.googleapis.com/startup-cofounder-ai-assets-qwiklabs-gcp-03-f53b15124fc6/"))
        mock_tool_context.save_artifact.assert_called_once()

    def test_search_startup_market_trends(self) -> None:
        """Test searching live market trends via public API."""
        res = search_startup_market_trends("AI agent")
        parsed = json.loads(res)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)

    def test_geocode_address_missing_key(self) -> None:
        """Test geocode_address when GOOGLE_MAPS_API_KEY is unset."""
        orig = os.environ.get("GOOGLE_MAPS_API_KEY")
        if "GOOGLE_MAPS_API_KEY" in os.environ:
            del os.environ["GOOGLE_MAPS_API_KEY"]
        res = geocode_address("1600 Amphitheatre Pkwy, Mountain View, CA")
        self.assertIn("GOOGLE_MAPS_API_KEY environment variable is not set", res)
        if orig:
            os.environ["GOOGLE_MAPS_API_KEY"] = orig

    def test_find_nearby_places_missing_key(self) -> None:
        """Test find_nearby_places when GOOGLE_MAPS_API_KEY is unset."""
        orig = os.environ.get("GOOGLE_MAPS_API_KEY")
        if "GOOGLE_MAPS_API_KEY" in os.environ:
            del os.environ["GOOGLE_MAPS_API_KEY"]
        res = find_nearby_places("cafe", 37.422, -122.084)
        self.assertIn("GOOGLE_MAPS_API_KEY environment variable is not set", res)
        if orig:
            os.environ["GOOGLE_MAPS_API_KEY"] = orig


if __name__ == "__main__":
    unittest.main()
