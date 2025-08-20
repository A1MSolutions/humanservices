import warnings
import re
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from .extractor import Extractor
import logging

# Modified by LLM to handle a bunch of special cases

logger = logging.getLogger(__name__)

class MarkupExtractor(Extractor):
    # Expanded file types to include ASP and other common web formats
    file_types = ("html", "xml", "javascript", "js", "asp", "aspx", "php", "erb")

    def _extract(self, file: bytes) -> str:
        # Convert bytes to string for initial inspection
        try:
            content_str = file.decode('utf-8', errors='replace')
        except Exception as e:
            logger.warning(f"Failed to decode file using utf-8: {str(e)}. Falling back to str(file).")
            content_str = str(file)

        # More comprehensive HTML detection - check for any HTML-like content
        html_indicators = [
            "<html", "<body", "<!doctype html", "<div", "<p", "<span",
            "<h1", "<h2", "<h3", "<h4", "<h5", "<h6", "<table", "<ul",
            "<ol", "<li", "<a ", "<img", "<br", "<hr", "<pre", "<code"
        ]

        is_html_like = any(indicator in content_str.lower() for indicator in html_indicators)

        if is_html_like:
            # This is likely HTML content, proceed with HTML parsing
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            try:
                extractor = BeautifulSoup(file, "html.parser")  # Use html.parser to avoid lxml dependency (has M1 issues)
            except Exception as e:
                logger.warning(f"Failed to parse HTML with BeautifulSoup: {str(e)}. Falling back to string processing.")
                return self._clean_extracted_text(content_str)
            warnings.resetwarnings()

            # Remove <script> and <style> inline tags
            for i in extractor(["script", "style"]):
                i.decompose()

            # Primary content extraction strategy - common patterns across gov sites

            # 1. Try to find main content container by ID. docViewer is for uscode.house.gov
            for main_id in ["main-main-content", "DeltaPlaceHolderMain", "mainContent", "main-content", "MainContentDiv", "SpecialContentContainer", "content", "docViewer", "MainContent_Container"]:
                main_content = extractor.find(id=main_id)
                if main_content:
                    # If it contains a "body-content" section, use that
                    body_content = main_content.find(class_="body-content")  # body-content is because OPM.gov puts a huge nav in its <main>
                    if body_content:
                        result = self._clean_extracted_text(body_content.get_text(" "))
                        if result.strip():
                            return result
                    result = self._clean_extracted_text(main_content.get_text(" "))
                    if result.strip():
                        return result

            # 2. Try to find by semantic HTML5 tags
            main_tag = extractor.find("main")
            if main_tag:
                # Remove navigation elements within main
                for nav in main_tag.find_all(["nav"], recursive=True):
                    nav.decompose()
                for side_nav in main_tag.find_all(class_=["SideNavContainer", "usa-sidenav", "navigation", "sidebar"]):
                    side_nav.decompose()
                # Remove breadcrumbs
                for breadcrumb in main_tag.find_all(class_=lambda c: c and "breadcrumb" in str(c).lower()):
                    breadcrumb.decompose()
                result = self._clean_extracted_text(main_tag.get_text(" "))
                if result.strip():
                    return result

            article_tag = extractor.find("article")
            if article_tag:
                result = self._clean_extracted_text(article_tag.get_text(" "))
                if result.strip():
                    return result

            # 3. Try common content container classes
            for content_class in ["body-content", "entry-content", "ContentPlaceHolder", "contentBox", "contentContainer", "main-content", "content", "region-content", "ms-rtestate-field", "umb-block-list"]:
                content_div = extractor.find(class_=lambda c: c and content_class in str(c).lower())
                if content_div:
                    result = self._clean_extracted_text(content_div.get_text(" "))
                    if result.strip():
                        return result

            # Special handling for documents with <pre> tags (like Federal Register)
            pre_tags = extractor.find_all("pre")
            if pre_tags:
                pre_text = " ".join(pre.get_text(" ") for pre in pre_tags)
                if pre_text.strip():
                    result = self._clean_extracted_text(pre_text)
                    if result.strip():
                        return result

            # 4. Fallback to body tag with navigation removed
            body = extractor.find("body")
            if body:
                # Remove common navigation elements
                for element_type in ["header", "nav", "footer", "aside"]:
                    for element in body.find_all(element_type):
                        element.decompose()

                # Remove common navigation classes
                for class_name in ["usa-nav", "usa-footer", "usa-header", "SideNavContainer", "navigation", "menu", "sidebar"]:
                    for element in body.find_all(class_=lambda c: c and class_name in str(c).lower()):
                        element.decompose()

                result = self._clean_extracted_text(body.get_text(" "))
                if result.strip():
                    return result

            # 5. Try to extract paragraphs if we still have no content
            paragraphs = extractor.find_all("p")
            if paragraphs:
                result = self._clean_extracted_text(" ".join(p.get_text(" ") for p in paragraphs))
                if result.strip():
                    return result

            # 6. Try to extract headings
            headings = extractor.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if headings:
                result = self._clean_extracted_text(" ".join(h.get_text(" ") for h in headings))
                if result.strip():
                    return result

            # 7. Final fallback - use the entire document
            extracted_text = extractor.get_text(" ")
            if extracted_text.strip():
                result = self._clean_extracted_text(extracted_text)
                if result.strip():
                    return result

            # Last resort - return the original content if parsing failed
            logger.warning("HTML parsing failed to extract meaningful content, returning original content")
            return self._clean_extracted_text(content_str)

        else:
            # This is not HTML-like content, return cleaned version
            cleaned_content = []
            in_comment_block = False

            for line in content_str.split('\n'):
                # Skip multi-line comment blocks
                if '/*' in line:
                    in_comment_block = True
                if '*/' in line:
                    in_comment_block = False
                    continue
                if in_comment_block:
                    continue

                # Skip single-line comments
                if '//' in line:
                    line = line.split('//', 1)[0]

                # Add non-empty lines
                if line.strip():
                    cleaned_content.append(line)

            result = self._clean_extracted_text(" ".join(cleaned_content))
            if not result.strip():
                # If we still have no content, return the original string
                logger.warning("No meaningful content extracted, returning original content")
                return self._clean_extracted_text(content_str)
            return result

    def _clean_extracted_text(self, text: str) -> str:
        """Clean up the extracted text to remove header/footer patterns and repeated symbols."""
        if not text:
            return ""

        # Replace consecutive === or ___ patterns (common in Federal Register)
        text = re.sub(r'={3,}', ' ', text)
        text = re.sub(r'_{3,}', ' ', text)

        # Clean up extra whitespace from all the replacements
        text = re.sub(r'\s+', ' ', text).strip()

        # Ensure we don't return just whitespace or very short content
        if len(text.strip()) < 3:
            logger.warning(f"Extracted text is too short: '{text}'")

        return text
