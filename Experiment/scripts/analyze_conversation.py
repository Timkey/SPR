#!/usr/bin/env python3
"""
Comprehensive Analysis Script for SPR Architecture
Compares the depth of Gemini conversation against the white paper
"""

import re
import json
from collections import Counter, defaultdict
from pathlib import Path
import pdfplumber

class ConversationAnalyzer:
    """Analyzes the depth and breadth of the Gemini conversation"""
    
    def __init__(self, conversation_path):
        self.conversation_path = Path(conversation_path)
        self.concepts = defaultdict(list)
        self.questions = []
        self.insights = []
        self.mathematical_concepts = []
        self.cryptographic_concepts = []
        
    def extract_concepts(self):
        """Extract key concepts from conversation"""
        with open(self.conversation_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define concept patterns
        patterns = {
            'roman_rules': [
                r'subtractive pair', r'scan and leap', r'left-to-right',
                r'geometric progression', r'bi-quinary', r'×5.*×2',
                r'additive.*subtractive', r'triple repeat'
            ],
            'encryption': [
                r'encryption', r'cipher', r'obfuscation', r'key.*space',
                r'diffusion', r'confusion', r'malleability', r'avalanche.*effect'
            ],
            'quantum': [
                r'quantum', r'Grover', r'Shor', r'post-quantum', r'PQ',
                r'quantum.*resistant', r'qubit'
            ],
            'architecture': [
                r'positional.*system', r'radix', r'base-\d+', r'ghosting',
                r'modular.*overflow', r'S-Box', r'state.*machine',
                r'index-dependent', r'sealed'
            ],
            'performance': [
                r'O\([^)]+\)', r'space.*complexity', r'throughput',
                r'latency', r'CPU.*cycle', r'branch.*prediction',
                r'cache.*miss', r'clock cycle'
            ],
            'comparison': [
                r'AES', r'RSA', r'Lattice', r'Kyber', r'McEliece',
                r'vs\.', r'compared.*to', r'better.*than'
            ]
        }
        
        # Extract concepts
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Get context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]
                    self.concepts[category].append({
                        'term': match.group(),
                        'context': context.strip()
                    })
        
        # Extract questions
        questions = re.findall(r'You said\n(.*?)(?=Gemini said|$)', content, re.DOTALL)
        self.questions = [q.strip() for q in questions if q.strip()]
        
        return self.concepts
    
    def analyze_depth(self):
        """Analyze the depth of discussion for each topic"""
        depth_analysis = {}
        
        for category, items in self.concepts.items():
            depth_analysis[category] = {
                'count': len(items),
                'unique_terms': len(set(item['term'].lower() for item in items)),
                'coverage': 'High' if len(items) > 20 else 'Medium' if len(items) > 10 else 'Low'
            }
        
        return depth_analysis
    
    def extract_key_insights(self):
        """Extract key insights and discoveries from the conversation"""
        insights = []
        
        with open(self.conversation_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for insight markers
        insight_patterns = [
            r'The Insight:.*?(?=\n\n)',
            r'Key Advantage:.*?(?=\n\n)',
            r'Why it.*?:.*?(?=\n\n)',
            r'The.*Effect:.*?(?=\n\n)',
            r'Final.*Verdict:.*?(?=\n\n)'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            insights.extend(matches)
        
        return insights


class PaperAnalyzer:
    """Analyzes the existing white paper"""
    
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.content = ""
        self.sections = []
        
    def extract_text(self):
        """Extract text from PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    self.content += page.extract_text() or ""
            return self.content
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def extract_sections(self):
        """Extract sections from paper"""
        # Look for section headers (numbers followed by title)
        section_pattern = r'(\d+\.?\d*)\s+([A-Z][^\n]+)'
        sections = re.findall(section_pattern, self.content)
        
        self.sections = [{'number': num, 'title': title.strip()} 
                        for num, title in sections]
        return self.sections
    
    def find_coverage(self, search_terms):
        """Check if specific terms are covered in the paper"""
        coverage = {}
        for term in search_terms:
            count = len(re.findall(term, self.content, re.IGNORECASE))
            coverage[term] = count > 0
        return coverage


class GapAnalyzer:
    """Performs gap analysis between conversation and paper"""
    
    def __init__(self, conversation_analyzer, paper_analyzer):
        self.conv = conversation_analyzer
        self.paper = paper_analyzer
        
    def identify_gaps(self):
        """Identify concepts discussed but missing or underrepresented in paper"""
        gaps = {
            'missing_concepts': [],
            'insufficient_depth': [],
            'missing_comparisons': [],
            'missing_insights': []
        }
        
        # Check each concept category
        for category, items in self.conv.concepts.items():
            unique_terms = list(set(item['term'].lower() for item in items))
            
            for term in unique_terms[:10]:  # Check top 10 terms per category
                if term not in self.paper.content.lower():
                    gaps['missing_concepts'].append({
                        'category': category,
                        'term': term,
                        'frequency_in_conv': sum(1 for i in items if i['term'].lower() == term)
                    })
        
        # Check insights
        insights = self.conv.extract_key_insights()
        for insight in insights[:20]:  # Check key insights
            # Check if the insight essence is in the paper
            key_words = set(re.findall(r'\w+', insight.lower()))
            paper_words = set(re.findall(r'\w+', self.paper.content.lower()))
            
            overlap = len(key_words & paper_words) / len(key_words) if key_words else 0
            
            if overlap < 0.3:  # Less than 30% overlap
                gaps['missing_insights'].append({
                    'insight': insight[:100] + '...',
                    'overlap': f"{overlap:.1%}"
                })
        
        return gaps
    
    def generate_recommendations(self, gaps):
        """Generate specific recommendations"""
        recommendations = []
        
        # Group missing concepts by category
        by_category = defaultdict(list)
        for concept in gaps['missing_concepts']:
            by_category[concept['category']].append(concept)
        
        for category, concepts in by_category.items():
            if len(concepts) > 3:
                recommendations.append({
                    'priority': 'High',
                    'area': category,
                    'action': f'Add comprehensive section covering {len(concepts)} missing concepts',
                    'examples': [c['term'] for c in concepts[:5]]
                })
        
        if len(gaps['missing_insights']) > 10:
            recommendations.append({
                'priority': 'Critical',
                'area': 'Key Insights',
                'action': 'Document major insights from conversation',
                'count': len(gaps['missing_insights'])
            })
        
        return recommendations


def main():
    print("="*80)
    print("SPR ARCHITECTURE: DEPTH ANALYSIS")
    print("Conversation vs. White Paper v1")
    print("="*80)
    print()
    
    # Paths
    conv_path = "/workspace/Documentation/gemini_conversation"
    pdf_path = "/workspace/Documentation/paper_v1.pdf"
    
    # Analyze conversation
    print("[1/5] Analyzing Gemini conversation...")
    conv_analyzer = ConversationAnalyzer(conv_path)
    concepts = conv_analyzer.extract_concepts()
    depth = conv_analyzer.analyze_depth()
    
    print(f"  ✓ Extracted {len(conv_analyzer.questions)} questions")
    print(f"  ✓ Found concepts in {len(concepts)} categories")
    print()
    
    # Analyze paper
    print("[2/5] Extracting content from paper_v1.pdf...")
    paper_analyzer = PaperAnalyzer(pdf_path)
    paper_content = paper_analyzer.extract_text()
    paper_sections = paper_analyzer.extract_sections()
    
    print(f"  ✓ Extracted {len(paper_content)} characters")
    print(f"  ✓ Found {len(paper_sections)} sections")
    print()
    
    # Perform gap analysis
    print("[3/5] Performing gap analysis...")
    gap_analyzer = GapAnalyzer(conv_analyzer, paper_analyzer)
    gaps = gap_analyzer.identify_gaps()
    
    print(f"  ✓ Identified {len(gaps['missing_concepts'])} missing concepts")
    print(f"  ✓ Found {len(gaps['missing_insights'])} underrepresented insights")
    print()
    
    # Generate recommendations
    print("[4/5] Generating recommendations...")
    recommendations = gap_analyzer.generate_recommendations(gaps)
    
    print(f"  ✓ Created {len(recommendations)} recommendations")
    print()
    
    # Generate report
    print("[5/5] Generating detailed report...")
    
    report = {
        'summary': {
            'conversation_lines': len(conv_analyzer.questions),
            'concepts_categories': len(concepts),
            'total_concept_mentions': sum(len(items) for items in concepts.values()),
            'paper_sections': len(paper_sections),
            'paper_length': len(paper_content),
            'gaps_found': len(gaps['missing_concepts']) + len(gaps['missing_insights'])
        },
        'depth_analysis': depth,
        'gaps': gaps,
        'recommendations': recommendations,
        'sections_in_paper': [s['title'] for s in paper_sections]
    }
    
    # Save report
    report_path = "/workspace/Analysis/depth_analysis_report.json"
    Path(report_path).parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✓ Report saved to {report_path}")
    print()
    
    # Print summary
    print("="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    print()
    print(f"Conversation Depth: {report['summary']['conversation_lines']} Q&A exchanges")
    print(f"Concept Categories: {report['summary']['concepts_categories']}")
    print(f"Total Mentions: {report['summary']['total_concept_mentions']}")
    print()
    print(f"Paper Sections: {report['summary']['paper_sections']}")
    print(f"Paper Length: {report['summary']['paper_length']:,} characters")
    print()
    print(f"GAPS IDENTIFIED: {report['summary']['gaps_found']}")
    print()
    
    # Print top recommendations
    print("TOP RECOMMENDATIONS:")
    print("-" * 80)
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. [{rec['priority']}] {rec['area']}")
        print(f"   → {rec['action']}")
        if 'examples' in rec:
            print(f"   Examples: {', '.join(rec['examples'][:3])}")
        print()
    
    print("="*80)
    print(f"Full report available at: {report_path}")
    print("="*80)
    
    return report


if __name__ == "__main__":
    main()
