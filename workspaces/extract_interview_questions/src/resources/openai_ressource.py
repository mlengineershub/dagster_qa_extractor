from dagster import ConfigurableResource
from pydantic import Field
from openai import OpenAI, OpenAIError
from typing import Any
from src.resources.models import ListEntries
import os
from dotenv import load_dotenv


class OpenAIResource(ConfigurableResource):  # type: ignore
    model_name: str = Field(
        description="The name of the model to use",
    )
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client: OpenAI | None = None

    def _get_client(self, api_key: str | None, base_url: str | None) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url=base_url,
                timeout=self.timeout,
                api_key=api_key,
            )
        return self._client

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model_name: str,
    ) -> ListEntries:
        try:
            load_dotenv()
            api_key = os.getenv("API_KEY")
            base_url = os.getenv("BASE_URL")

            client = self._get_client(api_key=api_key, base_url=base_url)

            response = client.beta.chat.completions.parse(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format=ListEntries,
            )

            parsed = response.choices[0].message.parsed
            if parsed is None or not isinstance(parsed, ListEntries):
                raise ValueError(
                    f"Invalid response. Expected instance of ListEntries, got {type(parsed).__name__ if parsed is not None else 'None'}"
                )

            return parsed

        except OpenAIError as e:
            raise OpenAIError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error during completion generation: {str(e)}"
            )

    def teardown(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
