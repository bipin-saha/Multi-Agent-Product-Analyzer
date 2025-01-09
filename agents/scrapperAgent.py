import asyncio
import nest_asyncio
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

nest_asyncio.apply()

class WebContentCleaner:
    """
    A class to handle web content crawling, cleaning, and saving to markdown files using the `crawl4ai` library.

    Attributes:
        url (str): The target URL for crawling.
        verbose (bool): Flag to enable verbose logging during crawling.
        fit_markdown_path (str): File path to save the fit markdown content.
    """

    def __init__(self, url, fit_markdown_path, verbose=True):
        """
        Initialize the WebContentCleaner instance with a target URL, file paths, and verbosity.

        Args:
            url (str): The target URL for crawling.
            fit_markdown_path (str): File path to save the fit markdown content.
            verbose (bool): Enables verbose logging if set to True.
        """
        self.url = url
        self.verbose = verbose
        self.fit_markdown_path = fit_markdown_path

    def remove_links(self, markdown_content):
        """
        Remove all links from the markdown content using regular expressions.

        Args:
            markdown_content (str): The markdown content to be processed.

        Returns:
            str: The markdown content with all links removed.
        """
        # Regular expression to match links in markdown (both inline and reference-style)
        link_pattern = re.compile(r'\[.*?\]\(.*?\)|\!\[.*?\]\(.*?\)')
        return re.sub(link_pattern, '', markdown_content)

    async def clean_content(self):
        """
        Perform the web crawling, content cleaning, and save the results as fit markdown file.

        The method uses the `crawl4ai` library's `AsyncWebCrawler` and applies content filtering
        with a custom pruning strategy to generate the fit markdown output.

        Raises:
            Exception: If an error occurs during the crawling process.
        """
        async with AsyncWebCrawler(verbose=self.verbose) as crawler:
            config = CrawlerRunConfig(
                cache_mode=CacheMode.ENABLED,
                excluded_tags=['nav', 'footer', 'aside'],
                remove_overlay_elements=False,
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(
                        threshold=0.48, threshold_type="fixed", min_word_threshold=0
                    ),
                    options={"ignore_links": False}
                ),
            )
            
            try:
                # Perform the crawling process
                result = await crawler.arun(url=self.url, config=config)

                # Check if markdown_v2 is None
                if result.markdown_v2 is None:
                    raise ValueError(f"Failed to crawl and generate markdown for URL: {self.url}")

                # Remove all links from the fit markdown
                fit_markdown = self.remove_links(result.markdown_v2.fit_markdown)

                # Save the fit markdown content (without links) to .md file
                with open(self.fit_markdown_path, "w", encoding="utf-8") as file:
                    file.write(fit_markdown)

                fit_markdown_length = len(fit_markdown)

                print(f"Fit Markdown (without links) saved to {self.fit_markdown_path}")
                print(f"Fit Markdown Length: {fit_markdown_length}")

            except Exception as e:
                print(f"Error during web crawling: {e}")

# if __name__ == "__main__":
#     # Example usage: User provides file path for fit markdown
#     url = "https://www.trustpilot.com/review/www.grammarly.com"
#     fit_markdown_path = input("Enter the file path for fit markdown output: ")

#     # Instantiate the cleaner with the target URL and file path
#     cleaner = WebContentCleaner(url=url, fit_markdown_path=fit_markdown_path)

#     # Run the cleaning process asynchronously
#     asyncio.run(cleaner.clean_content())
