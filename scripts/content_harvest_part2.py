#!/usr/bin/env python3
"""
NotebookLM Content Harvesting Script
Extracts and processes content from NotebookLM for bilingual digital products
Part 2 of 4: Extraction Functions
"""

import re


def _extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\s]+)',
        r'youtube\.com/embed/([^\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def _get_youtube_transcript(video_id: str) -> str:
    """Get transcript from YouTube - mock implementation"""
    return f"[Mock transcript for video {video_id} - AI self-education techniques, methodology, practical applications]"


def extract_notebooklm_content(notebook_url: str) -> "NotebookContent":
    """
    Extract content from a NotebookLM notebook.
    This is a mock implementation for demonstration purposes.
    In production, this would use CDP / Playwright to authenticate and extract.
    """
    content = NotebookContent()
    content.title = "Como auto educarse con IA. El método Dan Martell"
    
    # Add mock sources
    sources_data = [
        {
            "type": "youtube",
            "url": "https://www.youtube.com/watch?v=8G00aT2m4oU",
            "title": "Dan Martell - How to learn AI in 2025",
            "transcript": "[Dan Martell explains AI self-education methodology...]",
            "duration": 1200,
            "language": "en"
        },
        {
            "type": "article",
            "url": "https://danmartell.com/articles/self-education-ai",
            "title": "The Dan Martell Framework for Learning",
            "content": "[Detailed article about Dan Martell's self-education approach...]",
            "word_count": 3000,
            "language": "en"
        },
        {
            "type": "youtube",
            "url": "https://www.youtube.com/watch?v=example-es",
            "title": "Cómo aprender IA por ti mismo",
            "transcript": "[Spanish transcript about AI self-education...]",
            "duration": 1800,
            "language": "es"
        }
    ]
    
    for source_data in sources_data:
        source = NotebookSource(source_data)
        content.sources.append(source)
    
    content.key_points = [
        "Start with foundational concepts",
        "Build practical projects early",
        "Learn by teaching others",
        "Use iterative improvement",
        "Leverage AI tools effectively",
        "Create structured learning paths"
    ]
    
    content.tags = ["AI education", "learning methods", "productivity", "skills"]
    content.difficulty_level = "intermediate"
    content.estimated_time = 20
    content.target_audience = ["beginners", "intermediate", "professionals"]
    
    return content


def extract_transcripts(content: NotebookContent) -> Dict[str, Any]:
    """Extract transcripts from YouTube videos in content"""
    transcripts = {}
    
    for source in content.sources:
        if source.type == "youtube":
            try:
                video_id = _extract_video_id(source.url)
                transcript_text = _get_youtube_transcript(video_id)
                transcripts[video_id] = {
                    "video_id": video_id,
                    "title": source.title,
                    "transcript": transcript_text,
                    "language": source.language,
                    "duration": source.duration
                }
            except Exception as e:
                print(f"Warning: Failed to get transcript for {source.url}: {e}")
                transcripts[video_id if 'video_id' in dir() else "unknown"] = {
                    "video_id": "unknown",
                    "title": source.title,
                    "transcript": f"[Transcript not available - {e}]",
                    "language": source.language,
                    "duration": source.duration
                }
    
    return transcripts


print(f"✅ Part 2 loaded: Extraction Functions")