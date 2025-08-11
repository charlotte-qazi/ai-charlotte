"""
Test the CV chunker with different CV formats and structures.
Ensures the chunker works generically across various CV styles.
"""

import pytest
from backend.services.chunking.cv_chunker import CVChunker


class TestCVFormats:
    """Test CV chunker with different CV formats and styles."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chunker = CVChunker(target_words=60, max_words=100)
    
    def test_academic_cv_format(self):
        """Test with academic/research CV format."""
        academic_cv = """
        Dr. Emily Research
        Assistant Professor of Computer Science
        emily.research@university.edu
        
        Education
        Ph.D. in Computer Science, MIT, 2018
        Dissertation: "Machine Learning Applications in Natural Language Processing"
        Advisor: Prof. John Smith
        
        M.S. in Computer Science, Stanford University, 2014
        B.S. in Mathematics, UC Berkeley, 2012, Summa Cum Laude
        
        Academic Experience
        Assistant Professor, University of Excellence, 2018-Present
        Teaching courses in machine learning, algorithms, and data structures
        Leading research group of 8 PhD students and 4 postdocs
        
        Postdoctoral Researcher, Google Research, 2018-2019
        Worked on large-scale language models and neural architecture search
        
        Publications
        "Attention Mechanisms in Neural Networks" - NeurIPS 2021 (200+ citations)
        "Transfer Learning for Low-Resource Languages" - ACL 2020 (150+ citations)
        "Deep Learning for Code Generation" - ICML 2019 (300+ citations)
        
        Grants and Awards
        NSF CAREER Award, $500,000, 2021-2026
        Google Faculty Research Award, $50,000, 2020
        Outstanding Teaching Award, University of Excellence, 2019
        """
        
        chunks = self.chunker.chunk_cv(academic_cv)
        
        # Validate academic CV parsing
        assert len(chunks) >= 4, "Academic CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'education' in chunk_types, "Should identify education section"
        assert 'experience' in chunk_types, "Should identify academic experience"
        assert 'projects' in chunk_types, "Should classify publications as projects"
        
        # Check that academic titles are preserved
        headings = [c['heading'] for c in chunks]
        academic_terms = ['Education', 'Academic', 'Publications', 'Awards', 'Grants']
        assert any(any(term in heading for term in academic_terms) for heading in headings), \
            "Should preserve academic section headings"
    
    def test_creative_cv_format(self):
        """Test with creative/design CV format."""
        creative_cv = """
        ALEX CREATIVE
        Senior UI/UX Designer & Creative Director
        Portfolio: alexcreative.com | Behance: /alexcreative
        
        CREATIVE EXPERIENCE
        
        Senior UI/UX Designer | DesignStudio Inc | 2020-Present
        ▪ Lead design for mobile apps with 1M+ downloads
        ▪ Created design systems used across 15+ products
        ▪ Mentored junior designers and interns
        
        UI Designer | StartupCo | 2018-2020
        ▪ Designed user interfaces for B2B SaaS platform
        ▪ Conducted user research and usability testing
        
        DESIGN SKILLS
        Design Tools: Figma, Sketch, Adobe Creative Suite, InVision
        Prototyping: Principle, Framer, After Effects
        User Research: User interviews, A/B testing, Analytics
        
        CREATIVE PROJECTS
        "Sustainable Living App" - Winner of Design Challenge 2021
        "City Navigation Redesign" - Featured in Design Weekly
        "Brand Identity for Local Nonprofit" - Pro bono work
        
        EDUCATION & CERTIFICATIONS
        Bachelor of Fine Arts in Graphic Design
        Art Institute of Design, 2018
        
        Google UX Design Certificate, 2019
        Adobe Certified Expert in Photoshop, 2020
        """
        
        chunks = self.chunker.chunk_cv(creative_cv)
        
        # Validate creative CV parsing
        assert len(chunks) >= 4, "Creative CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'experience' in chunk_types, "Should identify creative experience"
        assert 'skills' in chunk_types, "Should identify design skills"
        assert 'projects' in chunk_types, "Should identify creative projects"
        assert 'education' in chunk_types, "Should identify education/certifications"
        
        # Check that creative terminology is handled
        headings = ' '.join([c['heading'] for c in chunks]).lower()
        creative_terms = ['creative', 'design', 'ui', 'ux']
        assert any(term in headings for term in creative_terms), \
            "Should handle creative industry terminology"
    
    def test_executive_cv_format(self):
        """Test with executive/senior leadership CV format."""
        executive_cv = """
        ROBERT EXECUTIVE
        Chief Technology Officer & VP of Engineering
        robert.exec@company.com | LinkedIn: /in/robertexec
        
        EXECUTIVE SUMMARY
        Seasoned technology executive with 15+ years leading engineering teams
        at Fortune 500 companies. Proven track record of scaling organizations
        from 20 to 200+ engineers while delivering $50M+ in revenue impact.
        
        LEADERSHIP EXPERIENCE
        
        Chief Technology Officer | TechCorp Inc | 2019-Present
        • Lead technology strategy for $100M+ revenue company
        • Built engineering organization from 50 to 150 engineers
        • Drove digital transformation initiative reducing costs by 30%
        • Board member responsible for technology roadmap and budget
        
        VP of Engineering | GrowthCo | 2016-2019
        • Scaled engineering team 5x while maintaining code quality
        • Led migration to microservices architecture
        • Implemented DevOps practices reducing deployment time by 80%
        
        BOARD POSITIONS & ADVISORY ROLES
        Board Member | TechStartup Inc | 2020-Present
        Technical Advisor | VentureCapital Partners | 2018-Present
        Advisory Board | University Engineering Program | 2017-Present
        
        EDUCATION & EXECUTIVE DEVELOPMENT
        Executive MBA | Wharton School | 2015
        M.S. Computer Science | Stanford University | 2005
        Leadership Development Program | Harvard Business School | 2018
        """
        
        chunks = self.chunker.chunk_cv(executive_cv)
        
        # Validate executive CV parsing
        assert len(chunks) >= 3, "Executive CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'experience' in chunk_types, "Should identify leadership experience"
        assert 'projects' in chunk_types or 'general' in chunk_types, "Should handle board positions"
        assert 'education' in chunk_types, "Should identify executive education"
        
        # Check that executive language is preserved
        all_text = ' '.join([c['text'] for c in chunks]).lower()
        exec_terms = ['executive', 'leadership', 'cto', 'vp', 'board', 'strategy']
        assert any(term in all_text for term in exec_terms), \
            "Should preserve executive terminology"
    
    def test_international_cv_format(self):
        """Test with international/European CV format."""
        international_cv = """
        MARIA INTERNATIONAL
        Software Development Engineer
        Date of Birth: 15/03/1990 | Nationality: Spanish
        Address: 123 Tech Street, Berlin, Germany
        Mobile: +49 123 456 7890 | Email: maria@email.de
        
        PROFESSIONAL PROFILE
        Experienced software engineer with expertise in distributed systems
        and cloud technologies. Fluent in English, German, and Spanish.
        
        WORK EXPERIENCE
        
        Senior Software Engineer | 01/2020 - Present
        TechBerlin GmbH, Berlin, Germany
        - Developed microservices using Java and Spring Boot
        - Implemented CI/CD pipelines with Jenkins and Docker
        - Led team of 4 developers on cloud migration project
        
        Software Engineer | 06/2018 - 12/2019
        StartupMadrid S.L., Madrid, Spain
        - Built RESTful APIs for mobile applications
        - Worked with React frontend and Node.js backend
        
        TECHNICAL COMPETENCIES
        Programming: Java, JavaScript, Python, Go
        Frameworks: Spring Boot, React, Node.js, Express
        Cloud: AWS, Docker, Kubernetes, Jenkins
        Databases: PostgreSQL, MongoDB, Redis
        
        LANGUAGES
        Spanish: Native
        English: Fluent (C2 level)
        German: Advanced (B2 level)
        French: Basic (A2 level)
        
        EDUCATION
        Master in Computer Science | 2016-2018
        Universidad Politécnica de Madrid, Spain
        Grade: 8.5/10 (Distinction)
        
        Bachelor in Software Engineering | 2012-2016
        Universidad de Barcelona, Spain
        Grade: 7.8/10 (Good)
        """
        
        chunks = self.chunker.chunk_cv(international_cv)
        
        # Validate international CV parsing
        assert len(chunks) >= 4, "International CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'experience' in chunk_types, "Should identify work experience"
        assert 'skills' in chunk_types, "Should identify technical competencies"
        assert 'education' in chunk_types, "Should identify education"
        
        # Should handle different date formats and international elements
        all_text = ' '.join([c['text'] for c in chunks])
        international_elements = ['GmbH', 'S.L.', 'Universidad', 'C2 level', 'B2 level']
        found_elements = [elem for elem in international_elements if elem in all_text]
        assert len(found_elements) >= 2, f"Should preserve international elements, found: {found_elements}"
    
    def test_entry_level_cv_format(self):
        """Test with entry-level/recent graduate CV format."""
        entry_level_cv = """
        Jessica NewGrad
        Recent Computer Science Graduate
        jessica.newgrad@email.com | (555) 123-4567
        
        OBJECTIVE
        Recent computer science graduate seeking entry-level software
        development position to apply programming skills and contribute
        to innovative technology solutions.
        
        EDUCATION
        Bachelor of Science in Computer Science | May 2023
        State University | GPA: 3.7/4.0
        Relevant Coursework: Data Structures, Algorithms, Database Systems,
        Software Engineering, Web Development, Machine Learning
        
        PROJECTS
        
        E-Commerce Web Application | Spring 2023
        Built full-stack web app using React, Node.js, and MongoDB
        Implemented user authentication and payment processing
        Deployed on AWS with CI/CD pipeline
        
        Movie Recommendation System | Fall 2022
        Developed ML model using Python and scikit-learn
        Achieved 85% accuracy in predicting user preferences
        Created web interface for user interaction
        
        TECHNICAL SKILLS
        Languages: Java, Python, JavaScript, C++, SQL
        Web Technologies: React, HTML/CSS, Node.js, Express
        Tools: Git, Docker, AWS, MongoDB, MySQL
        
        EXPERIENCE
        
        Software Development Intern | Summer 2022
        TechInternship Co. | Remote
        - Contributed to mobile app development using React Native
        - Fixed bugs and implemented new features
        - Participated in code reviews and agile development
        
        ACTIVITIES & LEADERSHIP
        President, Computer Science Club | 2022-2023
        Volunteer, Code for Good Hackathon | 2021-2022
        Tutor, University Math Learning Center | 2021-2023
        """
        
        chunks = self.chunker.chunk_cv(entry_level_cv)
        
        # Validate entry-level CV parsing
        assert len(chunks) >= 4, "Entry-level CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'education' in chunk_types, "Should identify education section"
        assert 'projects' in chunk_types, "Should identify projects section"
        assert 'skills' in chunk_types, "Should identify technical skills"
        assert 'experience' in chunk_types or 'general' in chunk_types, "Should handle internship experience"
        
        # Should handle entry-level specific content
        all_text = ' '.join([c['text'] for c in chunks]).lower()
        entry_terms = ['intern', 'graduate', 'gpa', 'coursework', 'project', 'hackathon']
        found_terms = [term for term in entry_terms if term in all_text]
        assert len(found_terms) >= 3, f"Should handle entry-level terminology, found: {found_terms}"
    
    def test_freelancer_cv_format(self):
        """Test with freelancer/consultant CV format."""
        freelancer_cv = """
        DAVID FREELANCER
        Full-Stack Developer & Technical Consultant
        Freelance since 2018 | Available for new projects
        
        EXPERTISE
        Specialized in building custom web applications and providing
        technical consulting for small to medium businesses.
        5+ years of freelance experience with 50+ satisfied clients.
        
        CLIENT WORK & PROJECTS
        
        E-Learning Platform Development | 2023
        Client: EducationCorp | Duration: 6 months | $45,000
        Built custom LMS using Django and React
        Integrated payment processing and video streaming
        Delivered on time and 15% under budget
        
        Restaurant Management System | 2022
        Client: Local Restaurant Chain | Duration: 4 months | $30,000
        Developed POS system and inventory management
        Reduced order processing time by 40%
        
        Startup MVP Development | 2021-2022
        Client: TechStartup | Duration: 8 months | $60,000
        Built mobile app MVP using React Native
        Helped secure $500K in seed funding
        
        TECHNICAL EXPERTISE
        Frontend: React, Vue.js, Angular, TypeScript
        Backend: Node.js, Python, Django, Express
        Mobile: React Native, Flutter
        Cloud: AWS, Google Cloud, Digital Ocean
        
        BUSINESS SKILLS
        Client Communication & Project Management
        Requirement Analysis & Technical Consulting
        Agile Development & Iterative Delivery
        Cost Estimation & Budget Management
        
        RATES & AVAILABILITY
        Hourly Rate: $75-100/hour
        Project Rate: $5,000-50,000 depending on scope
        Currently Available: 20-30 hours/week
        """
        
        chunks = self.chunker.chunk_cv(freelancer_cv)
        
        # Validate freelancer CV parsing
        assert len(chunks) >= 3, "Freelancer CV should produce multiple chunks"
        
        chunk_types = [c['chunk_type'] for c in chunks]
        assert 'projects' in chunk_types or 'experience' in chunk_types, "Should handle client work"
        assert 'skills' in chunk_types, "Should identify technical expertise"
        
        # Should handle freelancer-specific content
        all_text = ' '.join([c['text'] for c in chunks]).lower()
        freelancer_terms = ['client', 'freelance', 'project', 'consultant', 'rate', 'budget']
        found_terms = [term for term in freelancer_terms if term in all_text]
        assert len(found_terms) >= 3, f"Should handle freelancer terminology, found: {found_terms}"


class TestCVEdgeCases:
    """Test edge cases and unusual CV formats."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chunker = CVChunker(target_words=50, max_words=100)
    
    def test_mixed_language_cv(self):
        """Test CV with mixed languages."""
        mixed_cv = """
        PIERRE MULTILINGUAL
        Développeur Full-Stack / Full-Stack Developer
        
        EXPÉRIENCE PROFESSIONNELLE / PROFESSIONAL EXPERIENCE
        
        Senior Developer | TechParis SARL | 2020-Présent
        Développement d'applications web avec React et Node.js
        Leading development team of 5 engineers
        
        COMPÉTENCES TECHNIQUES / TECHNICAL SKILLS
        Langages: JavaScript, Python, Java
        Frameworks: React, Django, Spring
        Outils: Git, Docker, AWS
        
        FORMATION / EDUCATION
        Master en Informatique | Université de Paris | 2018
        Computer Science Degree with focus on web technologies
        """
        
        chunks = self.chunker.chunk_cv(mixed_cv)
        
        # Should handle mixed languages gracefully
        assert len(chunks) >= 2, "Should parse mixed language CV"
        
        # Should preserve both language versions
        all_text = ' '.join([c['text'] for c in chunks])
        assert 'Développeur' in all_text and 'Developer' in all_text, \
            "Should preserve mixed language content"
    
    def test_minimal_cv_format(self):
        """Test very minimal CV format."""
        minimal_cv = """
        John Simple
        Developer
        john@email.com
        
        Experience: 3 years at TechCo
        Skills: Python, JavaScript
        Education: CS Degree, 2020
        """
        
        chunks = self.chunker.chunk_cv(minimal_cv)
        
        # Should handle minimal CV appropriately
        assert len(chunks) <= 3, "Minimal CV should produce few chunks"
        if chunks:  # If any chunks are produced
            assert all(chunk['word_count'] >= 5 for chunk in chunks), \
                "Minimal chunks should still have some content"
    
    def test_unconventional_section_names(self):
        """Test CV with unconventional section names."""
        unconventional_cv = """
        CREATIVE PERSON
        Designer & Artist
        
        MY JOURNEY
        Started as junior designer at ArtCorp in 2020
        Became senior designer in 2022
        Now leading creative projects
        
        WHAT I'M GOOD AT
        Adobe Creative Suite, Figma, Sketch
        User interface design, branding
        Creative problem solving
        
        WHERE I LEARNED
        Art School Graduate, 2019
        Online courses in UX design
        Self-taught in many areas
        
        COOL STUFF I'VE MADE
        Award-winning poster design for music festival
        Mobile app UI that increased user engagement
        Brand identity for sustainable fashion company
        """
        
        chunks = self.chunker.chunk_cv(unconventional_cv)
        
        # Should handle unconventional section names
        assert len(chunks) >= 3, "Should parse unconventional sections"
        
        # Should still classify sections appropriately
        chunk_types = [c['chunk_type'] for c in chunks]
        expected_types = {'experience', 'skills', 'education', 'projects', 'general'}
        found_types = set(chunk_types)
        assert found_types.issubset(expected_types), \
            f"Should classify unconventional sections appropriately, got: {found_types}"


def test_chunker_consistency():
    """Test that the chunker produces consistent results."""
    cv_text = """
    Test Person
    Software Engineer
    
    Professional Experience
    Senior Developer at TestCorp for 3 years
    Built applications and managed databases
    Led team of developers on projects
    
    Technical Skills
    Python, JavaScript, React, Node.js
    AWS, Docker, Git, PostgreSQL
    
    Education
    Computer Science Degree from Test University
    """
    
    chunker = CVChunker(target_words=60, max_words=100)
    
    # Run chunking multiple times
    results = []
    for _ in range(3):
        chunks = chunker.chunk_cv(cv_text)
        results.append(len(chunks))
    
    # Results should be consistent
    assert all(r == results[0] for r in results), \
        f"Chunker should produce consistent results, got: {results}" 