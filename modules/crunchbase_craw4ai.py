import asyncio
import crawl4ai
print(crawl4ai.__version__)

import asyncio
import nest_asyncio
nest_asyncio.apply()

from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def clean_content():
    async with AsyncWebCrawler(verbose=True) as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            excluded_tags=['nav', 'footer', 'aside'],
            remove_overlay_elements=False,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0),
                options={
                    "ignore_links": False
                }
            ),
        )
        result = await crawler.arun(
            url="https://www.crunchbase.com/organization/zepto-29b1/company_financials",
            config=config,
        )

        # Save the markdown content to .md files
        full_markdown_path = "full_output_finance.md"
        fit_markdown_path = "fit_output_finance.md"

        with open(full_markdown_path, "w", encoding="utf-8") as file:
            file.write(result.markdown_v2.raw_markdown)

        with open(fit_markdown_path, "w", encoding="utf-8") as file:
            file.write(result.markdown_v2.fit_markdown)

        print(f"Full Markdown saved to {full_markdown_path}")
        print(f"Fit Markdown saved to {fit_markdown_path}")

        full_markdown_length = len(result.markdown_v2.raw_markdown)
        fit_markdown_length = len(result.markdown_v2.fit_markdown)
        print(f"Full Markdown Length: {full_markdown_length}")
        print(f"Fit Markdown Length: {fit_markdown_length}")

asyncio.run(clean_content())