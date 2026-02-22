from typing import Optional
from dataclasses import dataclass, field
import logging
import traceback

from email_exporter.inbox import InboxItem
from email_exporter.parsers import ParserSelector
from email_exporter.parsers.emitter_parser import EmitterParser
from email_exporter.parsers.content_item import ContentItemABC
from email_exporter.voice_provider import VoiceProvider


@dataclass
class ContentSection:
    """A single content section with its HTML, SSML, and description."""
    index: int
    content_type: str  # e.g., "generic.Paragraph", "substack.Header"
    original_html: str
    ssml_tags: list[str]  # List of SSML tag strings
    description_html: str
    description_content_type: str  # e.g., "text", "image", "embed"
    is_removed: bool = False
    removal_reason: Optional[str] = None
    debug_info: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "index": self.index,
            "contentType": self.content_type,
            "originalHtml": self.original_html,
            "ssmlTags": self.ssml_tags,
            "descriptionHtml": self.description_html,
            "descriptionContentType": self.description_content_type,
            "isRemoved": self.is_removed,
            "removalReason": self.removal_reason,
            "debugInfo": self.debug_info
        }


@dataclass
class SsmlChunk:
    """An SSML chunk ready for audio generation."""
    index: int
    ssml: str
    section_indices: list[int]  # Which content sections are in this chunk

    def to_dict(self):
        return {
            "index": self.index,
            "ssml": self.ssml,
            "sectionIndices": self.section_indices
        }


@dataclass
class ParseResult:
    """Complete result of parsing an email."""
    success: bool
    email_info: dict
    parser_name: str
    voice: str
    voice_reason: str
    sections: list[ContentSection]
    ssml_chunks: list[SsmlChunk]
    error: Optional[str] = None
    error_traceback: Optional[str] = None

    def to_dict(self):
        return {
            "success": self.success,
            "emailInfo": self.email_info,
            "parserName": self.parser_name,
            "voice": self.voice,
            "voiceReason": self.voice_reason,
            "sections": [s.to_dict() for s in self.sections],
            "ssmlChunks": [c.to_dict() for c in self.ssml_chunks],
            "error": self.error,
            "errorTraceback": self.error_traceback
        }


class ParserService:
    """Service for parsing emails with debug information."""

    def __init__(
        self,
        logger: logging.Logger,
        parser_selector: ParserSelector,
        voice_provider: VoiceProvider
    ):
        self._logger = logger
        self._parser_selector = parser_selector
        self._voice_provider = voice_provider

    def _get_content_item_html(self, content_item: ContentItemABC) -> str:
        """Extract HTML from a content item."""
        try:
            component = content_item._component
            if hasattr(component, '__str__'):
                return str(component)
            return repr(component)
        except Exception:
            return ""

    def _get_ssml_tag_strings(self, content_item: ContentItemABC) -> list[str]:
        """Get SSML tags as strings from a content item."""
        try:
            ssml_tags = list(content_item.get_ssml())
            return [tag.to_string() if hasattr(tag, 'to_string') else str(tag) for tag in ssml_tags]
        except Exception as e:
            return [f"Error: {e}"]

    def _get_description_html(self, content_item: ContentItemABC) -> tuple[str, str]:
        """Get description HTML and content type from a content item."""
        try:
            descriptions = list(content_item.get_description())
            if not descriptions:
                return "", "empty"

            html_parts = []
            content_type = "mixed"
            for desc in descriptions:
                html_parts.append(desc.to_text())
                content_type = desc.content_type

            return "\n".join(html_parts), content_type
        except Exception as e:
            return f"Error: {e}", "error"

    def _create_ssml_chunks(self, sections: list[ContentSection], speech_limit: int = 4500) -> list[SsmlChunk]:
        """Create SSML chunks from content sections, matching production logic."""
        from ssml import SpeechBuilder

        chunks = []
        current_tags = []
        current_section_indices = []

        def build_ssml(_tags):
            speech = SpeechBuilder()
            for tag_str in _tags:
                # For now, just use raw text - in production this would use actual tags
                speech.add_text(tag_str)
            return speech.speak().to_string()

        for section in sections:
            if section.is_removed:
                continue

            for tag_str in section.ssml_tags:
                test_tags = current_tags + [tag_str]
                test_ssml = build_ssml(test_tags)

                if len(test_ssml) > speech_limit and current_tags:
                    # Save current chunk
                    chunks.append(SsmlChunk(
                        index=len(chunks),
                        ssml=build_ssml(current_tags),
                        section_indices=list(current_section_indices)
                    ))
                    current_tags = [tag_str]
                    current_section_indices = [section.index]
                else:
                    current_tags.append(tag_str)
                    if section.index not in current_section_indices:
                        current_section_indices.append(section.index)

        # Don't forget the last chunk
        if current_tags:
            chunks.append(SsmlChunk(
                index=len(chunks),
                ssml=build_ssml(current_tags),
                section_indices=list(current_section_indices)
            ))

        return chunks

    def _get_voice_with_reason(self, inbox_item: InboxItem) -> tuple[str, str]:
        """Get voice and the reason for selection."""
        try:
            voice = self._voice_provider.get_voice(inbox_item)
            # Try to determine reason
            reason = f"Selected based on sender: {inbox_item.sender}"
            return voice, reason
        except Exception as e:
            return "en-US-Wavenet-A", f"Default (error: {e})"

    def parse_email(self, inbox_item: InboxItem) -> ParseResult:
        """Parse an email and return detailed results."""
        email_info = {
            "subject": inbox_item.title,
            "sender": inbox_item.sender,
            "recipient": inbox_item.owner,
            "date": inbox_item.date
        }

        try:
            # Get parser
            parser = self._parser_selector.get_parser(inbox_item)
            
            # Get parser name - for EmitterParser, use the emitter's class name
            if isinstance(parser, EmitterParser):
                emitter = parser._emitter
                parser_name = type(emitter).__name__.replace("ItemEmitter", "Parser").replace("Emitter", "Parser")
            else:
                parser_name = type(parser).__name__

            # Get voice
            voice, voice_reason = self._get_voice_with_reason(inbox_item)

            sections = []

            # For EmitterParser, we can get individual content items
            if isinstance(parser, EmitterParser):
                emitter = parser._emitter
                items = list(emitter.get_items(inbox_item))

                for i, item in enumerate(items):
                    original_html = self._get_content_item_html(item)
                    ssml_tags = self._get_ssml_tag_strings(item)
                    desc_html, desc_type = self._get_description_html(item)

                    section = ContentSection(
                        index=i,
                        content_type=item._get_repr_name(),
                        original_html=original_html,
                        ssml_tags=ssml_tags,
                        description_html=desc_html,
                        description_content_type=desc_type,
                        debug_info={
                            "componentName": getattr(item._component, 'name', 'unknown'),
                            "textPreview": item._get_text_content()[:100] if item._get_text_content() else ""
                        }
                    )
                    sections.append(section)

                # Create SSML chunks
                ssml_chunks = self._create_ssml_chunks(sections)

            else:
                # For GeneralParser, we get the full parsed result
                parsed = parser.parse(inbox_item)

                # Create a single section with all content
                section = ContentSection(
                    index=0,
                    content_type="general",
                    original_html=inbox_item.html,
                    ssml_tags=parsed.ssml if hasattr(parsed, 'ssml') else [],
                    description_html=parsed.combined_description if hasattr(parsed, 'combined_description') else "",
                    description_content_type="text"
                )
                sections.append(section)

                ssml_chunks = [
                    SsmlChunk(index=i, ssml=ssml, section_indices=[0])
                    for i, ssml in enumerate(parsed.ssml if hasattr(parsed, 'ssml') else [])
                ]

            return ParseResult(
                success=True,
                email_info=email_info,
                parser_name=parser_name,
                voice=voice,
                voice_reason=voice_reason,
                sections=sections,
                ssml_chunks=ssml_chunks
            )

        except Exception as e:
            return ParseResult(
                success=False,
                email_info=email_info,
                parser_name="Unknown",
                voice="",
                voice_reason="",
                sections=[],
                ssml_chunks=[],
                error=str(e),
                error_traceback=traceback.format_exc()
            )
