import json
from pydantic import BaseModel, ValidationError, HttpUrl
from duckduckgo_search import DDGS

class DuckDuckGoSearchResult(BaseModel):
    """
    A Pydantic model to validate each search result item.
    """
    title: str
    link: HttpUrl

    def to_dict(self):
        """
        Convert the Pydantic model to a dictionary, ensuring `HttpUrl` is serialized as a string.
        """
        return {
            "title": self.title,
            "link": str(self.link)  # Convert HttpUrl to string
        }

class DuckDuckGoSearch:
    """
    A class to perform searches using the DuckDuckGo search engine and return validated results in JSON format.
    """

    def __init__(self, query: str, max_results: int):
        """
        Initialize the search class with a query and maximum number of results.

        :param query: The search query string.
        :param max_results: The maximum number of results to retrieve, provided by the user.
        """
        self.query = query
        self.max_results = max_results

    def perform_search(self) -> str:
        """
        Perform the search using DuckDuckGo and return the validated results as a JSON object.
        Handles any request-related errors gracefully.

        :return: A JSON object containing validated search results with titles and corresponding links.
        """
        try:
            results = DDGS().text(self.query, max_results=self.max_results)
            
            # Extract and validate results using Pydantic
            validated_results = []
            for result in results:
                title = result.get('title', 'No title')
                link = result.get('href', '')
                
                # Validate each result
                try:
                    validated_result = DuckDuckGoSearchResult(title=title, link=link)
                    validated_results.append(validated_result.to_dict())  # Use `to_dict` to serialize correctly
                except ValidationError as ve:
                    print(f"Skipping invalid result: {ve}")

            # Return the results as a JSON object
            return json.dumps(validated_results, indent=4)

        except Exception as e:
            return json.dumps({"error": "An error occurred while performing the search.", "details": str(e)}, indent=4)



# # Example usage
# if __name__ == "__main__":
#     query = "Deepgram G2"
#     max_results = 5
#     ddg_search = DuckDuckGoSearch(query, max_results)
#     search_results = ddg_search.perform_search()
#     print(search_results)
