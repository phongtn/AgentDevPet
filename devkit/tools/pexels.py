import os
from typing import Optional, Union

import httpx
from agno.agent import Agent
from agno.media import Image
from agno.team.team import Team
from agno.tools import Toolkit
from agno.tools.function import ToolResult
from agno.utils.log import logger


class PexelsTools(Toolkit):
    def __init__(
            self,
            api_key: Optional[str] = None,
            **kwargs,
    ):
        super().__init__(name="pexels_tools", **kwargs)

        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            logger.error("No Pexels API key provided")
        self.register(self.search_photos)

    def search_photos(self, agent: Union[Agent, Team], query: str, max_results: int = 3, orientation: str = "landscape", color: Optional[str] = None) -> ToolResult:
        """
        Search for high-quality photos on Pexels matching a given text description.

        This function connects to the Pexels API to find relevant photos based on the provided query.
        When photos are found, they are automatically added to the agent's context as ImageArtifact
        objects, making them available for the agent to use in responses or further processing.

        Parameters:
            agent (Union[Agent, Team]): The agent or team instance that will receive the image artifacts.
                                        This is required for storing the found images in the agent's context.

            query (str): A text description of the photos to search for. This can be:
                         - General concepts (e.g., "nature", "city", "people")
                         - Specific scenarios (e.g., "group of people working", "sunset over mountains")
                         - Objects or subjects (e.g., "red apple", "smiling woman")
                         The more specific the query, the more targeted the results will be.

            max_results (int): The maximum number of photos to retrieve from Pexels.
                               This controls how many photos will be added to the agent.
                               Higher values provide more options but increase API usage.
            orientation (str): Desired photo orientation. The current supported orientations are:
                        - landscape
                        - portrait
                        - square
            color: Optional[str]: Desired photo color.Supported colors:
                    red, orange, yellow, green, turquoise, blue, violet, pink, brown, black, gray, white, or any hexadecimal color code (e.g., #ffffff).

        Returns:
            ToolResult: Containing the URLs of the found photos, or "No photo found" if the search
                 failed or no photos matched the query.

        Image Behavior:
            - Each photo is added to the agent as an ImageArtifact with:
              - ID: The original Pexels photo ID
              - URL: The URL to the original size image
              - Alt text: The alternative text description from Pexels
              - Revised prompt: The original search query

            - Images are retrieved in landscape orientation by default

        Error Handling:
            - HTTP errors (e.g., API limit exceeded, authentication failures) are logged and result in "No photo found"
            - General exceptions during processing are caught, logged, and result in "No photo found"

        Example:
            >> result = pexels_tools.search_photos(agent, "beach sunset", 3, "landscape", "white")
            >> print(result)
            "These are the found photos ['https://images.pexels.com/photos/1234/sunset-beach.jpg', ...]"

        Note:
            This function requires a valid Pexels API key to be set either during toolkit initialization
            or via the PEXELS_API_KEY environment variable.
        """

        base_url = "https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": max_results,
            "color": color
        }
        image_artifacts = []

        ## orientation Desired photo orientation. The current supported orientations are: landscape, portrait or square.
        try:
            response = httpx.get(base_url, params=params, headers={"Authorization": self.api_key})
            response.raise_for_status()

            data = response.json()
            photo_urls = []
            for photo in data.get("photos", []):
                media_id = str(photo.get("id"))
                images = photo.get("src", {})
                original_image = images["original"]

                alt_text = photo["alt"]
                photo_urls.append(original_image)
                image_artifact = Image(id=media_id, url=original_image, alt_text=alt_text, revised_prompt=query)
                image_artifacts.append(image_artifact)

            if image_artifacts:
                return ToolResult(content=f"Found {len(photo_urls)} Photo(s): {photo_urls}", images=image_artifacts)
            else:
                return ToolResult(content="No photo found")



        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return ToolResult(content=f"HTTP error occurred: {e.response.status_code}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return ToolResult(content=f"An error occurred: {e}")
