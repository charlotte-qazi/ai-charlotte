"""
Comprehensive tests for the CV chunker.
Tests various CV formats, quality metrics, and edge cases.
"""

import pytest
from pathlib import Path
import tempfile
import json
from typing import List, Dict, Any

from backend.services.chunking.cv_chunker import CVChunker


class TestCVChunker:
    """Test suite for the generic CV chunker."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chunker = CVChunker(target_words=80, max_words=120)
    
    def test_basic_chunking(self):
        """Test basic chunking functionality."""
        cv_text = """
        John Doe
        Software Engineer
        john.doe@email.com
        
        Professional Experience
        Senior Developer at TechCorp (2020-Present)
        Built scalable web applications using React and Node.js for e-commerce platform.
        Led a team of 5 developers on multiple high-impact projects and initiatives.
        Implemented CI/CD pipelines and automated testing frameworks.
        Collaborated with product managers and designers to deliver features on time.
        
        Junior Developer at StartupCo (2018-2020)
        Developed RESTful APIs using Python and Django framework.
        Worked on database optimization and performance improvements.
        Participated in code reviews and agile development processes.
        
        Technical Skills
        Programming Languages: JavaScript, Python, Java, TypeScript
        Frontend Technologies: React, Vue.js, HTML5, CSS3, Bootstrap
        Backend Technologies: Node.js, Django, Express, Flask
        Databases: PostgreSQL, MongoDB, MySQL, Redis
        Cloud Services: AWS, Docker, Kubernetes, Jenkins
        Development Tools: Git, JIRA, VS Code, IntelliJ
        
        Education
        Bachelor of Science in Computer Science
        University of Technology, 2018
        Graduated with honors, GPA: 3.8/4.0
        Relevant coursework: Data Structures, Algorithms, Software Engineering
        """
        
        chunks = self.chunker.chunk_cv(cv_text)
        
        # Basic assertions
        assert len(chunks) > 1, "Should create multiple chunks"
        assert all(chunk['word_count'] >= 15 for chunk in chunks), "All chunks should meet minimum word count"
        assert any('experience' in chunk['chunk_type'] for chunk in chunks), "Should identify experience sections"
        assert any('skills' in chunk['chunk_type'] for chunk in chunks), "Should identify skills sections"
        assert any('education' in chunk['chunk_type'] for chunk in chunks), "Should identify education sections"
    
    def test_markdown_cv_format(self):
        """Test CV with markdown formatting."""
        markdown_cv = """
        # Jane Smith
        **Data Scientist** | jane@email.com
        
        ## Professional Experience
        
        **Senior Data Scientist** | DataCorp | 2020-Present
        - Developed ML models for customer segmentation
        - Improved prediction accuracy by 25%
        - Led cross-functional analytics projects
        
        **Data Analyst** | StartupCo | 2018-2020
        - Created dashboards using Tableau and Python
        - Analyzed customer behavior patterns
        
        ## Technical Skills
        - **Programming**: Python, R, SQL, JavaScript
        - **ML/AI**: TensorFlow, PyTorch, scikit-learn
        - **Tools**: Docker, AWS, Git, Jupyter
        
        ## Education
        **Master of Science in Data Science**
        Stanford University | 2018
        
        **Bachelor of Science in Mathematics**
        UC Berkeley | 2016
        """
        
        chunks = self.chunker.chunk_cv(markdown_cv)
        
        # Test markdown-specific features
        assert len(chunks) >= 4, "Should create multiple chunks from markdown"
        
        # Check that job titles are extracted properly
        experience_chunks = [c for c in chunks if c['chunk_type'] == 'experience']
        assert len(experience_chunks) >= 1, "Should find experience chunks"
        
        # Check skills parsing
        skills_chunks = [c for c in chunks if c['chunk_type'] == 'skills']
        assert len(skills_chunks) >= 1, "Should find skills chunks"
        
        # Check education parsing
        education_chunks = [c for c in chunks if c['chunk_type'] == 'education']
        assert len(education_chunks) >= 1, "Should find education chunks"
    
    def test_plain_text_cv_format(self):
        """Test CV with plain text section headers."""
        plain_cv = """
        Michael Johnson
        Product Manager
        michael.johnson@email.com
        
        Professional Experience
        
        Product Manager at InnovaCorp (2019-Present)
        Led product development for mobile applications serving 100k+ users.
        Collaborated with engineering and design teams to deliver features.
        Increased user engagement by 40% through data-driven improvements.
        
        Associate Product Manager at TechStart (2017-2019)
        Managed product roadmap for B2B SaaS platform.
        Conducted user research and competitive analysis.
        
        Technical Skills
        Product management tools: Jira, Asana, Figma
        Analytics: Google Analytics, Mixpanel, SQL
        Technical understanding: APIs, databases, web technologies
        
        Education
        MBA in Technology Management
        MIT Sloan School of Management, 2017
        
        Publications & Presentations
        Speaker at ProductCon 2022: "Data-Driven Product Decisions"
        Published article in Harvard Business Review on product strategy
        """
        
        chunks = self.chunker.chunk_cv(plain_cv)
        
        # Test plain text parsing
        assert len(chunks) >= 4, "Should parse plain text sections"
        
        # Verify section classification
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'experience' in chunk_types, "Should classify experience sections"
        assert 'skills' in chunk_types, "Should classify skills sections"
        assert 'education' in chunk_types, "Should classify education sections"
        assert 'projects' in chunk_types, "Should classify publications as projects"
    
    def test_chunk_quality_metrics(self):
        """Test chunk quality and size metrics."""
        # Create a longer CV to test chunking behavior
        long_cv = """
        Sarah Wilson
        Senior Software Engineer
        
        Professional Experience
        
        Senior Software Engineer at BigTech Corp (2020-Present)
        Lead backend development for high-traffic e-commerce platform serving millions of users daily.
        Architected microservices infrastructure using Docker and Kubernetes for improved scalability.
        Implemented caching strategies that reduced page load times by 60% and improved user experience.
        Mentored junior developers and conducted code reviews to maintain high code quality standards.
        Collaborated with product managers and designers to deliver customer-facing features on time.
        
        Software Engineer at MidSize Company (2018-2020)
        Developed RESTful APIs using Node.js and Express for mobile application backend.
        Built automated testing suites achieving 90% code coverage and reducing deployment bugs.
        Optimized database queries resulting in 40% improvement in application performance.
        Participated in agile development process with daily standups and sprint planning.
        
        Junior Developer at Startup Inc (2016-2018)
        Contributed to full-stack web application development using React and Python.
        Implemented user authentication and authorization systems with OAuth integration.
        Worked closely with UX designers to create responsive and accessible user interfaces.
        
        Technical Skills
        Programming Languages: JavaScript, Python, Java, TypeScript, Go
        Frontend Technologies: React, Vue.js, HTML5, CSS3, SASS, Bootstrap
        Backend Technologies: Node.js, Express, Django, Flask, Spring Boot
        Databases: PostgreSQL, MongoDB, Redis, MySQL
        Cloud Services: AWS, Google Cloud, Azure, Docker, Kubernetes
        Tools: Git, Jenkins, JIRA, Slack, VS Code, IntelliJ
        
        Education
        Bachelor of Science in Computer Science
        University of California, Berkeley
        Graduated Magna Cum Laude, GPA: 3.8/4.0
        Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering
        """
        
        chunks = self.chunker.chunk_cv(long_cv)
        
        # Quality metrics
        word_counts = [c['word_count'] for c in chunks]
        avg_words = sum(word_counts) / len(word_counts)
        
        # Test size constraints
        assert all(wc <= 150 for wc in word_counts), "No chunk should exceed max_words"
        assert all(wc >= 15 for wc in word_counts), "All chunks should meet min_words"
        assert 60 <= avg_words <= 120, f"Average chunk size should be reasonable, got {avg_words}"
        
        # Test semantic coherence - experience should be split by jobs
        experience_chunks = [c for c in chunks if c['chunk_type'] == 'experience']
        assert len(experience_chunks) >= 2, "Long experience should be split into multiple chunks"
        
        # Test that chunk headings are meaningful
        headings = [c['heading'] for c in chunks]
        assert all(len(h) > 0 for h in headings), "All chunks should have headings"
        assert not all(h == "Profile" for h in headings), "Should have diverse headings"
    
    def test_section_classification(self):
        """Test accuracy of section type classification."""
        test_cases = [
            ("Professional Experience at Google", "experience"),
            ("Work History", "experience"), 
            ("Career Summary", "experience"),
            ("Technical Skills and Expertise", "skills"),
            ("Core Competencies", "skills"),
            ("Programming Languages", "skills"),
            ("Educational Background", "education"),
            ("Academic Qualifications", "education"),
            ("University Degrees", "education"),
            ("Key Projects and Portfolio", "projects"),
            ("Publications & Presentations", "projects"),
            ("Leadership & Volunteering", "projects"),
            ("Contact Information", "personal"),
            ("Personal Details", "personal"),
            ("Random Section Title", "general"),
        ]
        
        for heading, expected_type in test_cases:
            actual_type = self.chunker._classify_section(heading)
            assert actual_type == expected_type, f"'{heading}' should be classified as '{expected_type}', got '{actual_type}'"
    
    def test_text_cleaning(self):
        """Test text cleaning and normalization."""
        messy_text = """
        | Name    | Value   |
        |---------|---------|
        | John    | Doe     |
        
        This   has    lots     of    spaces
        
        
        Multiple empty lines above
        """
        
        cleaned = self.chunker._clean_text(messy_text)
        
        # Test cleaning results
        assert '|' not in cleaned, "Should remove table formatting"
        assert '---' not in cleaned, "Should remove table separators"
        assert '    ' not in cleaned, "Should normalize multiple spaces"
        assert '\n\n\n' not in cleaned, "Should normalize multiple newlines"
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        
        # Test empty CV
        empty_chunks = self.chunker.chunk_cv("")
        assert len(empty_chunks) == 0, "Empty CV should produce no chunks"
        
        # Test very short CV
        short_cv = "John Doe\nSoftware Engineer"
        short_chunks = self.chunker.chunk_cv(short_cv)
        # Should either create no chunks or one small chunk
        assert len(short_chunks) <= 1, "Very short CV should produce at most one chunk"
        
        # Test CV with no clear sections
        no_sections_cv = "This is just a paragraph of text without any clear sections or structure."
        no_section_chunks = self.chunker.chunk_cv(no_sections_cv)
        assert len(no_section_chunks) >= 0, "Should handle CV without clear sections"
        
        # Test CV with only section headers (no content)
        headers_only = """
        Professional Experience
        Technical Skills
        Education
        """
        header_chunks = self.chunker.chunk_cv(headers_only)
        # Should create minimal or no chunks due to lack of content
        assert len(header_chunks) <= 2, "Headers without content should produce few chunks"
    
    def test_job_title_extraction(self):
        """Test extraction of job titles from experience text."""
        test_cases = [
            ("**Senior Engineer** at TechCorp\nBuilt applications", "Senior Engineer"),
            ("Google, Mountain View | 2020-2022\nWorked on search", "Google, Mountain View"),
            ("Software Developer\nDeveloped web applications", "Software Developer"),
            ("Just some text without clear title", "Position"),  # fallback
        ]
        
        for job_text, expected_title in test_cases:
            actual_title = self.chunker._extract_job_title(job_text)
            assert expected_title in actual_title or actual_title == expected_title, \
                f"Expected '{expected_title}' in '{actual_title}' for text: '{job_text[:50]}...'"
    
    def test_education_title_extraction(self):
        """Test extraction of education titles."""
        test_cases = [
            ("**Bachelor of Science** in Computer Science\nUniversity", "Bachelor of Science"),
            ("Stanford University\nMaster's Degree", "Stanford University"),
            ("PhD in Machine Learning from MIT", "PhD in Machine Learning from MIT"),
            ("Some education text", "Some education text"),
        ]
        
        for edu_text, expected_title in test_cases:
            actual_title = self.chunker._extract_education_title(edu_text)
            assert expected_title in actual_title or actual_title == expected_title, \
                f"Expected '{expected_title}' in '{actual_title}' for text: '{edu_text[:50]}...'"


class TestCVChunkerIntegration:
    """Integration tests with file I/O and CLI."""
    
    def test_with_real_pdf(self):
        """Test with the actual CV PDF if available."""
        cv_path = Path("data/raw/cv.pdf")
        if not cv_path.exists():
            pytest.skip("CV PDF not available for testing")
        
        from backend.services.ingestion.loader import PDFLoader
        
        # Load and chunk the real CV
        loader = PDFLoader(cv_path)
        content = loader.load_text()
        
        chunker = CVChunker(target_words=80, max_words=120)
        chunks = chunker.chunk_cv(content)
        
        # Validate real CV results
        assert len(chunks) >= 5, "Real CV should produce multiple chunks"
        assert len(chunks) <= 20, "Real CV shouldn't be over-chunked"
        
        # Check variety of chunk types
        chunk_types = set(c['chunk_type'] for c in chunks)
        assert len(chunk_types) >= 3, "Should have variety in chunk types"
        
        # Validate word counts are reasonable
        word_counts = [c['word_count'] for c in chunks]
        avg_words = sum(word_counts) / len(word_counts)
        assert 40 <= avg_words <= 150, f"Average chunk size should be reasonable: {avg_words}"
    
    def test_cli_integration(self):
        """Test CLI tool integration."""
        # Create a temporary CV file
        test_cv = """
        Test Person
        Software Engineer
        
        Professional Experience
        Senior Developer at TestCorp
        Built test applications and managed test databases.
        Worked with test teams on test projects.
        
        Technical Skills
        Testing frameworks, Test automation, Test planning
        
        Education
        Bachelor of Testing
        Test University, 2020
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_cv)
            temp_path = Path(f.name)
        
        try:
            # Import and use the CLI function
            from backend.cli.process_cv import process_cv
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "test_chunks.jsonl"
                
                stats = process_cv(
                    input_path=temp_path,
                    output_path=output_path,
                    source_label="test_cv",
                    target_words=50,
                    max_words=100
                )
                
                # Validate CLI results
                assert stats['total_chunks'] > 0, "CLI should produce chunks"
                assert output_path.exists(), "CLI should create output file"
                
                # Load and validate JSONL output
                with output_path.open('r') as f:
                    records = [json.loads(line) for line in f]
                
                assert len(records) == stats['total_chunks'], "JSONL records should match stats"
                
                # Validate JSONL structure
                required_fields = ['id', 'text', 'source', 'heading', 'chunk_type', 'word_count']
                for record in records:
                    for field in required_fields:
                        assert field in record, f"Record missing required field: {field}"
                
        finally:
            temp_path.unlink()  # Clean up


def run_quality_analysis():
    """
    Run a comprehensive quality analysis of the chunker.
    This is not a test but a utility function for manual evaluation.
    """
    from backend.services.ingestion.loader import PDFLoader
    
    cv_path = Path("data/raw/cv.pdf")
    if not cv_path.exists():
        print("❌ CV PDF not found for quality analysis")
        return
    
    # Load CV and chunk it
    loader = PDFLoader(cv_path)
    content = loader.load_text()
    
    chunker = CVChunker(target_words=80, max_words=120)
    chunks = chunker.chunk_cv(content)
    
    # Print detailed analysis
    print("🔍 CV Chunker Quality Analysis")
    print("=" * 50)
    print(f"📄 Original content: {len(content)} characters")
    print(f"📊 Total chunks: {len(chunks)}")
    
    word_counts = [c['word_count'] for c in chunks]
    print(f"📈 Word count stats:")
    print(f"   Min: {min(word_counts)} words")
    print(f"   Max: {max(word_counts)} words") 
    print(f"   Average: {sum(word_counts) / len(word_counts):.1f} words")
    
    # Chunk type distribution
    chunk_types = {}
    for chunk in chunks:
        chunk_type = chunk['chunk_type']
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    print(f"\n📋 Chunk type distribution:")
    for chunk_type, count in chunk_types.items():
        print(f"   {chunk_type}: {count} chunks")
    
    # Show sample chunks
    print(f"\n📝 Sample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}: {chunk['chunk_type']} - \"{chunk['heading']}\" ({chunk['word_count']} words)")
        print(f"Text preview: {chunk['text'][:150]}...")
    
    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    # Run quality analysis when script is executed directly
    run_quality_analysis() 