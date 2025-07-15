from abc import ABC, abstractmethod
from typing import List, Optional
import re

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    BeautifulSoup = None
    NavigableString = None


class IChunker(ABC):
    """Interface for content chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, html: Optional[str] = None) -> List[str]:
        pass


class ISummarizer(ABC):
    """Interface for content summarization strategies."""

    @abstractmethod
    def summarize(self, chunk: str) -> str:
        pass


class IFilter(ABC):
    """Interface for content filtering strategies."""

    @abstractmethod
    def filter(self, chunks: List[str]) -> List[str]:
        pass


class HTMLSectionChunker(IChunker):
    """Cleans HTML content by removing unwanted tags and returns the text."""

    def chunk(self, text: str, html: Optional[str] = None) -> List[str]:
        if not html or BeautifulSoup is None:
            return [text]

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()

        # Chunk based on semantic tags
        chunks = []
        for element in soup.find_all(["h1", "h2", "h3", "p", "li", "div"]):
            # Get text and strip leading/trailing whitespace
            text_chunk = element.get_text(separator=" ", strip=True)
            if text_chunk:
                chunks.append(text_chunk)

        if not chunks:
            # Fallback to the original text if no chunks are found
            return [soup.get_text(separator=" ", strip=True)]

        return chunks


class LangChainSummarizer(ISummarizer):
    """Stub for a summarizer using LangChain."""

    def summarize(self, chunk: str) -> str:
        return chunk


class BoilerplateFilter(IFilter):
    """Filters out common boilerplate text from a list of chunks."""

    def filter(self, chunks: List[str]) -> List[str]:
        filtered_chunks = []
        for chunk in chunks:
            # Example boilerplate patterns (customize as needed)
            if not re.search(
                r"(Copyright ©|All rights reserved|Privacy Policy|Terms of Service)",
                chunk,
                re.IGNORECASE,
            ):
                filtered_chunks.append(chunk)
        return filtered_chunks


class LengthFilter(IFilter):
    """Filters out chunks that are too short or too long."""

    def __init__(self, min_len: int = 20, max_len: int = 2000):
        self.min_len = min_len
        self.max_len = max_len

    def filter(self, chunks: List[str]) -> List[str]:
        return [chunk for chunk in chunks if self.min_len <= len(chunk) <= self.max_len]


class CompositeFilter(IFilter):
    """Combines multiple filters into a single pipeline."""

    def __init__(self, filters: List[IFilter]):
        self.filters = filters

    def filter(self, chunks: List[str]) -> List[str]:
        for f in self.filters:
            chunks = f.filter(chunks)
        return chunks


class ContentPreprocessingPipeline:
    """Pipeline that composes chunking, summarization, and filtering for website content."""

    def __init__(self, chunker: IChunker, summarizer: ISummarizer, filter_: IFilter):
        self.chunker = chunker
        self.summarizer = summarizer
        self.filter = filter_

    def process(self, text: str, html: Optional[str] = None) -> List[str]:
        cleaned_text = self.chunker.chunk(text, html)
        summarized = [self.summarizer.summarize(chunk) for chunk in cleaned_text]
        filtered = self.filter.filter(summarized)
        return filtered
