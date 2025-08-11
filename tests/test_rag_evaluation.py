"""
RAG System Evaluation Tests
Tests the complete RAG pipeline with realistic chatbot questions about Charlotte's CV.
"""

import pytest
import requests
import time
from typing import List, Dict, Any


class TestRAGEvaluation:
    """Comprehensive RAG system evaluation using realistic chatbot questions."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Base URL for API testing."""
        return "http://127.0.0.1:8000/api"
    
    @pytest.fixture(scope="class")
    def test_questions(self):
        """Common questions people ask about CVs with expected keywords for evaluation."""
        return [
            # Easy Questions (should get high scores)
            {
                "question": "What is Charlotte's experience at BCG?",
                "category": "experience",
                "expected_keywords": ["BCG", "Senior AI Engineer", "Gen AI", "Wealth Co-Pilot"],
                "difficulty": "easy"
            },
            {
                "question": "What are Charlotte's technical skills?",
                "category": "skills", 
                "expected_keywords": ["React", "JavaScript", "Python", "front-end"],
                "difficulty": "easy"
            },
            {
                "question": "Where did Charlotte go to university?",
                "category": "education",
                "expected_keywords": ["Royal Holloway", "University of London"],
                "difficulty": "easy"
            },
            
            # Medium Questions
            {
                "question": "Tell me about Charlotte's AI projects",
                "category": "experience",
                "expected_keywords": ["Wealth Co-Pilot", "Gen AI", "education-focused", "AI"],
                "difficulty": "medium"
            },
            {
                "question": "What leadership experience does Charlotte have?",
                "category": "leadership",
                "expected_keywords": ["founder", "DV Women", "Code First Girls", "teaching"],
                "difficulty": "medium"
            },
            {
                "question": "Has Charlotte given any presentations?",
                "category": "achievements", 
                "expected_keywords": ["talks", "iJS London", "Women of Silicon Roundabout"],
                "difficulty": "medium"
            },
            
            # Hard Questions (more complex/conversational)
            {
                "question": "What makes Charlotte unique as an engineer?",
                "category": "conversational",
                "expected_keywords": ["AI", "front-end", "user-first", "communication"],
                "difficulty": "hard"
            },
            {
                "question": "How did Charlotte transition into tech?",
                "category": "background",
                "expected_keywords": ["General Assembly", "Software Engineering", "2017", "2018"],
                "difficulty": "hard"
            }
        ]
    
    def test_api_health_check(self, api_base_url):
        """Test that the API is running and healthy."""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            assert response.status_code == 200, "API health check should return 200"
            
            data = response.json()
            assert 'status' in data, "Health response should contain status"
            assert data['status'] == 'healthy', "RAG system should be healthy"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running. Start with: uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
    
    def test_individual_questions(self, api_base_url, test_questions):
        """Test each question individually and evaluate responses."""
        print("\n🚀 Starting RAG System Evaluation")
        print("=" * 50)
        
        results = []
        total_start_time = time.time()
        
        for i, test_case in enumerate(test_questions):
            print(f"\n🔍 Question {i+1}/{len(test_questions)}: {test_case['question']}")
            
            # Get response from API
            start_time = time.time()
            response = self._get_api_response(api_base_url, test_case['question'])
            response_time = time.time() - start_time
            
            # Evaluate the response
            evaluation = self._evaluate_response(response, test_case, response_time)
            results.append(evaluation)
            
            # Print individual result
            self._print_question_result(evaluation)
            
            # Basic assertions
            assert response['answer'] is not None, f"Should return an answer for: {test_case['question']}"
            assert len(response['answer']) > 0, f"Answer should not be empty for: {test_case['question']}"
        
        total_time = time.time() - total_start_time
        
        # Print comprehensive report
        self._print_final_report(results, total_time)
        
        # Overall system assertions
        valid_results = [r for r in results if not r.get('error')]
        passed_tests = [r for r in valid_results if r['passed']]
        success_rate = len(passed_tests) / len(valid_results) if valid_results else 0
        
        # Assert reasonable performance
        assert success_rate >= 0.5, f"RAG system success rate too low: {success_rate:.1%}"
        assert len(valid_results) > 0, "Should have at least some valid results"
    
    def test_edge_cases(self, api_base_url):
        """Test how the system handles edge cases and unknown information."""
        edge_cases = [
            {
                "question": "Does Charlotte have experience with blockchain?",
                "should_gracefully_decline": True
            },
            {
                "question": "What is Charlotte's favorite color?",
                "should_gracefully_decline": True
            }
        ]
        
        for case in edge_cases:
            print(f"\n🔍 Testing edge case: {case['question']}")
            
            response = self._get_api_response(api_base_url, case['question'])
            answer = response['answer'].lower()
            
            if case['should_gracefully_decline']:
                # Should gracefully say it doesn't know
                graceful_responses = [
                    "don't have enough information",
                    "don't know", 
                    "no specific mention",
                    "not mentioned",
                    "there is no specific mention"
                ]
                
                is_graceful = any(phrase in answer for phrase in graceful_responses)
                if not is_graceful:
                    print(f"   ❌ Expected graceful decline but got: {answer}")
                    # Check if it's still a reasonable response (acknowledging lack of info)
                    reasonable_responses = [
                        "based on the provided context",
                        "no mention",
                        "not mentioned",
                        "no information",
                        "don't have information"
                    ]
                    is_reasonable = any(phrase in answer for phrase in reasonable_responses)
                    assert is_reasonable, f"Should acknowledge lack of information: {case['question']}"
                    print(f"   ✅ Reasonably acknowledged lack of info")
                else:
                    print(f"   ✅ Gracefully declined: {answer[:100]}...")
    
    def test_response_quality_metrics(self, api_base_url):
        """Test various quality metrics of responses."""
        test_question = "What is Charlotte's experience at BCG?"
        
        response = self._get_api_response(api_base_url, test_question)
        
        # Response structure tests
        assert 'answer' in response, "Response should contain 'answer' field"
        assert 'sources' in response, "Response should contain 'sources' field"
        
        answer = response['answer']
        sources = response['sources']
        
        # Content quality tests
        assert len(answer) > 30, "Answer should be substantial (>30 characters)"
        assert len(answer.split()) > 10, "Answer should contain multiple words"
        
        # Sources quality tests
        if len(sources) > 0:
            for source in sources:
                assert 'score' in source, "Each source should have a score"
                assert isinstance(source['score'], (int, float)), "Score should be numeric"
                assert 0 <= source['score'] <= 1, "Score should be between 0 and 1"
        
        print(f"✅ Response quality check passed")
        print(f"   Answer length: {len(answer)} chars")
        print(f"   Word count: {len(answer.split())} words")
        print(f"   Sources: {len(sources)}")
    
    def _get_api_response(self, api_base_url: str, question: str) -> Dict[str, Any]:
        """Get response from the chat API."""
        response = requests.post(
            f"{api_base_url}/chat",
            json={"message": question},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}")
        
        return response.json()
    
    def _evaluate_response(self, response: Dict[str, Any], test_case: Dict[str, Any], response_time: float) -> Dict[str, Any]:
        """Evaluate the quality of an API response."""
        answer = response.get('answer', '')
        sources = response.get('sources', [])
        
        # Keyword matching
        answer_lower = answer.lower()
        expected_keywords = test_case['expected_keywords']
        matched_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
        keyword_score = len(matched_keywords) / len(expected_keywords) if expected_keywords else 1.0
        
        # Response quality metrics
        word_count = len(answer.split())
        has_sources = len(sources) > 0
        avg_source_score = sum(s.get('score', 0) for s in sources) / len(sources) if sources else 0
        
        # Failure detection
        is_fallback = "don't have enough information" in answer_lower
        is_error = "encountered an error" in answer_lower
        is_too_short = word_count < 20
        
        # Overall score calculation
        overall_score = self._calculate_score(
            keyword_score, word_count, has_sources, avg_source_score,
            is_fallback, is_error, test_case['difficulty']
        )
        
        # Pass/fail determination
        passed = (
            overall_score >= 0.6 and 
            not is_fallback and 
            not is_error and 
            not is_too_short
        )
        
        return {
            'question': test_case['question'],
            'category': test_case['category'],
            'difficulty': test_case['difficulty'],
            'answer': answer,
            'word_count': word_count,
            'response_time': response_time,
            'keyword_score': keyword_score,
            'matched_keywords': matched_keywords,
            'missing_keywords': [kw for kw in expected_keywords if kw.lower() not in answer_lower],
            'has_sources': has_sources,
            'source_count': len(sources),
            'avg_source_score': avg_source_score,
            'is_fallback': is_fallback,
            'is_error': is_error,
            'overall_score': overall_score,
            'passed': passed
        }
    
    def _calculate_score(self, keyword_score: float, word_count: int, has_sources: bool, 
                        avg_source_score: float, is_fallback: bool, is_error: bool, 
                        difficulty: str) -> float:
        """Calculate overall response quality score."""
        if is_fallback or is_error:
            return 0.0
        
        # Base score from components
        score = 0.0
        score += keyword_score * 0.4  # 40% - keyword relevance
        score += min(word_count / 80, 1.0) * 0.2  # 20% - response completeness
        score += (1.0 if has_sources else 0.0) * 0.2  # 20% - has sources
        score += min(avg_source_score, 1.0) * 0.2  # 20% - source quality
        
        # Adjust for difficulty
        if difficulty == 'easy' and score < 0.8:
            score *= 0.8  # Penalize poor performance on easy questions
        elif difficulty == 'hard' and score > 0.4:
            score *= 1.1  # Bonus for good performance on hard questions
        
        return min(score, 1.0)
    
    def _print_question_result(self, evaluation: Dict[str, Any]):
        """Print result for a single question."""
        score = evaluation['overall_score']
        status = "✅ PASS" if evaluation['passed'] else "❌ FAIL"
        
        print(f"   {status} | Score: {score:.2f} | Keywords: {evaluation['keyword_score']:.2f}")
        print(f"   Category: {evaluation['category']} | Difficulty: {evaluation['difficulty']}")
        print(f"   Response: {evaluation['word_count']} words | {evaluation['response_time']:.2f}s")
        print(f"   Sources: {evaluation['source_count']} | Avg Score: {evaluation['avg_source_score']:.2f}")
        
        if evaluation['matched_keywords']:
            print(f"   ✓ Found: {evaluation['matched_keywords']}")
        if evaluation['missing_keywords']:
            print(f"   ✗ Missing: {evaluation['missing_keywords']}")
        
        # Show answer preview
        answer_preview = evaluation['answer'][:120] + "..." if len(evaluation['answer']) > 120 else evaluation['answer']
        print(f"   💬 Answer: {answer_preview}")
    
    def _print_final_report(self, results: List[Dict[str, Any]], total_time: float):
        """Print the final evaluation report."""
        valid_results = [r for r in results if not r.get('error')]
        
        if not valid_results:
            print("\n❌ No valid results to analyze")
            return
        
        # Overall metrics
        total_questions = len(valid_results)
        passed_questions = len([r for r in valid_results if r['passed']])
        success_rate = passed_questions / total_questions
        
        avg_score = sum(r['overall_score'] for r in valid_results) / total_questions
        avg_response_time = sum(r['response_time'] for r in valid_results) / total_questions
        avg_keyword_score = sum(r['keyword_score'] for r in valid_results) / total_questions
        
        print("\n" + "=" * 60)
        print("🎯 RAG SYSTEM EVALUATION REPORT")
        print("=" * 60)
        
        # Overall performance
        print(f"📊 Overall Performance:")
        print(f"   Success Rate: {success_rate:.1%} ({passed_questions}/{total_questions})")
        print(f"   Average Score: {avg_score:.2f}/1.0")
        print(f"   Keyword Match Rate: {avg_keyword_score:.2f}/1.0")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        print(f"   Total Evaluation Time: {total_time:.1f}s")
        
        # Performance by category
        categories = {}
        for result in valid_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        print(f"\n📋 Performance by Category:")
        for category, cat_results in categories.items():
            cat_success = len([r for r in cat_results if r['passed']]) / len(cat_results)
            cat_avg_score = sum(r['overall_score'] for r in cat_results) / len(cat_results)
            print(f"   {category.title()}: {cat_success:.1%} success, {cat_avg_score:.2f} avg score ({len(cat_results)} questions)")
        
        # Performance by difficulty
        difficulties = {}
        for result in valid_results:
            diff = result['difficulty']
            if diff not in difficulties:
                difficulties[diff] = []
            difficulties[diff].append(result)
        
        print(f"\n🎚️ Performance by Difficulty:")
        for difficulty, diff_results in difficulties.items():
            diff_success = len([r for r in diff_results if r['passed']]) / len(diff_results)
            diff_avg_score = sum(r['overall_score'] for r in diff_results) / len(diff_results)
            print(f"   {difficulty.title()}: {diff_success:.1%} success, {diff_avg_score:.2f} avg score ({len(diff_results)} questions)")
        
        # Top performers
        print(f"\n🏆 Top Performing Questions:")
        sorted_results = sorted(valid_results, key=lambda x: x['overall_score'], reverse=True)
        for i, result in enumerate(sorted_results[:3]):
            print(f"   {i+1}. {result['question'][:50]}... (Score: {result['overall_score']:.2f})")
        
        # Areas for improvement
        print(f"\n⚠️ Areas for Improvement:")
        failed_results = [r for r in valid_results if not r['passed']]
        if failed_results:
            for result in failed_results[:3]:
                print(f"   • {result['question'][:50]}... (Score: {result['overall_score']:.2f})")
        else:
            print("   🎉 All questions passed! Great job!")
        
        # RAG System Grade
        if success_rate >= 0.9 and avg_score >= 0.8:
            grade = "A+ (Excellent)"
        elif success_rate >= 0.8 and avg_score >= 0.7:
            grade = "A (Very Good)"
        elif success_rate >= 0.7 and avg_score >= 0.6:
            grade = "B (Good)"
        elif success_rate >= 0.6 and avg_score >= 0.5:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"\n🎓 RAG System Grade: {grade}")
        print("=" * 60) 