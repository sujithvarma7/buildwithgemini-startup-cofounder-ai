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
import urllib.parse
import urllib.request


def search_startup_market_trends(query: str) -> str:
    """Search live tech community discussions, Show HN launches, and feedback
    on a given topic, market niche, or product concept.

    Args:
        query: Topic or industry keyword to search for (e.g. 'AI developer tools',
               'SaaS pricing', 'open source agent').

    Returns:
        JSON string containing relevant community discussions, points, comment counts, and URLs.
    """
    api_key = os.environ.get("HN_ALGOLIA_API_KEY", "")
    encoded_query = urllib.parse.quote(query)
    url = f"https://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story&hitsPerPage=5"

    headers = {"User-Agent": "StartupCoFounderAI/1.0"}
    if api_key:
        headers["X-Algolia-API-Key"] = api_key

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for hit in data.get("hits", []):
                results.append({
                    "title": hit.get("title"),
                    "points": hit.get("points"),
                    "comments": hit.get("num_comments"),
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "created_at": hit.get("created_at"),
                })
            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error querying market trends API: {str(e)}"
