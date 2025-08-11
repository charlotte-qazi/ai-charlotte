"""
Current CV Integration Test
Automatically tests whatever CV is present in data/raw/ directory.
This test adapts to any CV format and validates the complete pipeline.
"""

import pytest
import os
import glob
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import json
import requests
import time

from backend.services.chunking.cv_chunker import CVChunker


class TestCurrentCV:
    """Test the complete pipeline with whatever CV is currently in data/raw/."""
    
    @pytest.fixture(scope="class")
    def current_cv_path(self) -> Optional[str]:
        """Find the current CV in data/raw directory."""
        raw_data_dir = Path("data/raw")
        
        # Look for common CV file patterns
        cv_patterns = [
            "cv.*", "CV.*", "resume.*", "Resume.*",
            "*cv.*", "*CV.*", "*resume.*", "*Resume.*"
        ]
        
        found_files = []
        for pattern in cv_patterns:
            found_files.extend(glob.glob(str(raw_data_dir / pattern)))
        
        # Filter for supported formats
        supported_extensions = ['.pdf', '.md', '.markdown']
        cv_files = [f for f in found_files 
                   if any(f.lower().endswith(ext) for ext in supported_extensions)]
        
        if not cv_files:
            pytest.skip("No CV found in data/raw/ directory. Please add a CV file (PDF or Markdown).")
        
        # Return the first found CV
        return cv_files[0]
    
    @pytest.fixture(scope="class")
    def cv_metadata(self, current_cv_path: str) -> Dict[str, Any]:
        """Extract metadata about the current CV."""
        cv_path = Path(current_cv_path)
        
        return {
            'filename': cv_path.name,
            'extension': cv_path.suffix.lower(),
            'size_bytes': cv_path.stat().st_size,
            'format': 'pdf' if cv_path.suffix.lower() == '.pdf' else 'markdown'
        }
    
    def test_cv_exists_and_accessible(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test that the CV file exists and is accessible."""
        cv_path = Path(current_cv_path)
        
        assert cv_path.exists(), f"CV file not found: {current_cv_path}"
        assert cv_path.is_file(), f"CV path is not a file: {current_cv_path}"
        assert cv_metadata['size_bytes'] > 0, f"CV file is empty: {current_cv_path}"
        
        print(f"✅ Found CV: {cv_metadata['filename']}")
        print(f"   Format: {cv_metadata['format']}")
        print(f"   Size: {cv_metadata['size_bytes']:,} bytes")
    
    def test_cv_chunking_quality(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test that the current CV can be chunked effectively."""
        chunker = CVChunker()
        
        # Load the CV content
        if cv_metadata['format'] == 'pdf':
            from backend.services.document_loader import load_pdf
            text = load_pdf(current_cv_path)
        else:
            with open(current_cv_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        assert len(text.strip()) > 0, "CV text extraction failed - no content found"
        
        # Chunk the CV
        chunks = chunker.chunk_cv(text)
        
        # Basic chunk validation
        assert len(chunks) > 0, "No chunks generated from CV"
        assert len(chunks) >= 2, f"Too few chunks generated: {len(chunks)} (expected at least 2)"
        
        # Quality metrics
        total_words = sum(chunk['word_count'] for chunk in chunks)
        avg_words = total_words / len(chunks)
        
        # Validate chunk quality
        assert avg_words >= 20, f"Average chunk size too small: {avg_words} words"
        assert avg_words <= 200, f"Average chunk size too large: {avg_words} words"
        
        # Check for variety in chunk types
        chunk_types = set(chunk['chunk_type'] for chunk in chunks)
        assert len(chunk_types) >= 2, f"Insufficient chunk type variety: {chunk_types}"
        
        # Validate headings are meaningful
        headings = [chunk['heading'] for chunk in chunks if chunk['heading']]
        assert len(headings) > 0, "No meaningful headings found in chunks"
        
        print(f"✅ CV chunking successful:")
        print(f"   Chunks: {len(chunks)}")
        print(f"   Average words: {avg_words:.1f}")
        print(f"   Chunk types: {chunk_types}")
        print(f"   Sample headings: {headings[:3]}")
    
    def test_cv_processing_cli(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test that the CV can be processed using the CLI tool."""
        # Ensure processed directory exists
        processed_dir = Path("data/processed")
        processed_dir.mkdir(exist_ok=True)
        
        # Run the CLI processing command
        cmd = ["python", "-m", "backend.cli.process_cv", current_cv_path]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                cwd=Path.cwd()
            )
            
            assert result.returncode == 0, f"CLI processing failed: {result.stderr}"
            
            # Check that output file was created
            cv_name = Path(current_cv_path).stem
            expected_output = processed_dir / f"{cv_name}_chunks.jsonl"
            
            assert expected_output.exists(), f"Expected output file not found: {expected_output}"
            
            # Validate output file content
            with open(expected_output, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) > 0, "Output file is empty"
            
            # Parse and validate first chunk
            first_chunk = json.loads(lines[0])
            required_fields = ['id', 'text', 'source', 'heading', 'chunk_type', 'word_count']
            
            for field in required_fields:
                assert field in first_chunk, f"Missing required field: {field}"
            
            print(f"✅ CLI processing successful:")
            print(f"   Output: {expected_output}")
            print(f"   Chunks: {len(lines)}")
            print(f"   Sample chunk: {first_chunk['heading']} ({first_chunk['word_count']} words)")
            
        except subprocess.TimeoutExpired:
            pytest.fail("CLI processing timed out after 60 seconds")
        except Exception as e:
            pytest.fail(f"CLI processing error: {e}")
    
    def test_cv_content_coverage(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test that the CV contains expected professional content."""
        # Load CV content
        if cv_metadata['format'] == 'pdf':
            from backend.services.document_loader import load_pdf
            text = load_pdf(current_cv_path).lower()
        else:
            with open(current_cv_path, 'r', encoding='utf-8') as f:
                text = f.read().lower()
        
        # Check for common CV sections/content
        expected_indicators = {
            'experience': ['experience', 'work', 'employment', 'job', 'position', 'role'],
            'skills': ['skills', 'technologies', 'programming', 'technical', 'tools'],
            'education': ['education', 'degree', 'university', 'college', 'school'],
            'contact': ['email', '@', 'phone', 'linkedin', 'github', 'contact']
        }
        
        found_sections = {}
        for section, keywords in expected_indicators.items():
            found_keywords = [kw for kw in keywords if kw in text]
            found_sections[section] = found_keywords
        
        # Validate professional content
        assert len(found_sections['experience']) > 0, "No work experience indicators found"
        assert len(found_sections['skills']) > 0, "No skills/technical content found"
        
        # At least 2 out of 4 section types should be present
        sections_with_content = [s for s, kw in found_sections.items() if kw]
        assert len(sections_with_content) >= 2, f"Insufficient CV sections found: {sections_with_content}"
        
        print(f"✅ CV content coverage:")
        for section, keywords in found_sections.items():
            if keywords:
                print(f"   {section.title()}: {keywords[:3]}")
    
    @pytest.mark.integration
    def test_end_to_end_rag_with_current_cv(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test the complete RAG pipeline with the current CV."""
        # This test requires the API server to be running
        api_base_url = "http://127.0.0.1:8000/api"
        
        try:
            # Test API health
            health_response = requests.get(f"{api_base_url}/health", timeout=5)
            if health_response.status_code != 200:
                pytest.skip("API server not running. Start with: uvicorn backend.main:app --reload")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running. Start with: uvicorn backend.main:app --reload")
        
        # Generate generic questions based on CV content
        generic_questions = [
            "What professional experience is mentioned?",
            "What skills and technologies are listed?",
            "What is the educational background?",
            "What are the key achievements or projects?"
        ]
        
        successful_responses = 0
        total_questions = len(generic_questions)
        
        for question in generic_questions:
            try:
                response = requests.post(
                    f"{api_base_url}/chat",
                    json={"message": question},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '')
                    
                    # Check if we got a meaningful response (not fallback)
                    if len(answer) > 50 and "don't have enough information" not in answer.lower():
                        successful_responses += 1
                        print(f"✅ '{question}' - {len(answer)} chars")
                    else:
                        print(f"⚠️ '{question}' - fallback response")
                else:
                    print(f"❌ '{question}' - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ '{question}' - Error: {e}")
        
        # Validate RAG performance
        success_rate = successful_responses / total_questions
        assert success_rate >= 0.5, f"RAG success rate too low: {success_rate:.1%} ({successful_responses}/{total_questions})"
        
        print(f"✅ End-to-end RAG test:")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   CV: {cv_metadata['filename']}")
    
    def test_cv_embeddings_compatibility(self, current_cv_path: str, cv_metadata: Dict[str, Any]):
        """Test that CV chunks are suitable for embedding generation."""
        chunker = CVChunker()
        
        # Load and chunk the CV
        if cv_metadata['format'] == 'pdf':
            from backend.services.document_loader import load_pdf
            text = load_pdf(current_cv_path)
        else:
            with open(current_cv_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        chunks = chunker.chunk_cv(text)
        
        # Test embedding suitability
        for i, chunk in enumerate(chunks[:5]):  # Test first 5 chunks
            chunk_text = chunk['text']
            
            # Check text length (OpenAI embedding limits)
            assert len(chunk_text) < 8000, f"Chunk {i} too long for embeddings: {len(chunk_text)} chars"
            
            # Check for meaningful content (not just whitespace/formatting)
            word_count = len(chunk_text.split())
            assert word_count >= 5, f"Chunk {i} too short: {word_count} words"
            
            # Check for reasonable text/noise ratio
            alpha_chars = sum(c.isalpha() for c in chunk_text)
            text_ratio = alpha_chars / len(chunk_text) if chunk_text else 0
            assert text_ratio >= 0.5, f"Chunk {i} has low text ratio: {text_ratio:.2f}"
        
        print(f"✅ Embedding compatibility:")
        print(f"   Tested {min(5, len(chunks))} chunks")
        print(f"   All chunks suitable for embedding generation")


class TestCVDiscovery:
    """Additional tests for CV discovery and validation."""
    
    def test_data_directory_structure(self):
        """Test that required data directories exist."""
        raw_dir = Path("data/raw")
        processed_dir = Path("data/processed")
        
        assert raw_dir.exists(), "data/raw directory not found"
        assert raw_dir.is_dir(), "data/raw is not a directory"
        
        # Create processed dir if it doesn't exist (for CI/testing)
        processed_dir.mkdir(exist_ok=True)
        
        print(f"✅ Data directories:")
        print(f"   Raw: {raw_dir} ({'exists' if raw_dir.exists() else 'missing'})")
        print(f"   Processed: {processed_dir} ({'exists' if processed_dir.exists() else 'missing'})")
    
    def test_find_all_documents(self):
        """Test discovery of all documents in data/raw."""
        raw_dir = Path("data/raw")
        
        if not raw_dir.exists():
            pytest.skip("data/raw directory not found")
        
        # Find all potential documents
        all_files = list(raw_dir.glob("*"))
        document_files = [f for f in all_files if f.suffix.lower() in ['.pdf', '.md', '.markdown', '.txt']]
        
        print(f"✅ Document discovery:")
        print(f"   Total files in data/raw: {len(all_files)}")
        print(f"   Document files: {len(document_files)}")
        
        if document_files:
            for doc in document_files:
                print(f"   - {doc.name} ({doc.suffix}, {doc.stat().st_size:,} bytes)")
        else:
            print(f"   ⚠️ No documents found in data/raw")
            print(f"   Add a CV file (PDF or Markdown) to test the complete pipeline")


if __name__ == "__main__":
    # Quick discovery test when run directly
    test_discovery = TestCVDiscovery()
    test_discovery.test_data_directory_structure()
    test_discovery.test_find_all_documents()
    
    # Try to find and test current CV
    try:
        test_cv = TestCurrentCV()
        cv_path = test_cv.current_cv_path()
        if cv_path:
            print(f"\n🔍 Found CV for testing: {cv_path}")
            print("Run 'pytest tests/test_current_cv.py -v -s' for full test suite")
        else:
            print("\n⚠️ No CV found in data/raw/")
            print("Add a CV file to test the complete pipeline")
    except Exception as e:
        print(f"\n❌ Error during CV discovery: {e}") 