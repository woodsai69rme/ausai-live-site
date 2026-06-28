import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


class PromptCategorizer:
    """
    Categorizes prompts by functionality and project type using keyword analysis
    and natural language processing techniques.
    """
    
    def __init__(self, extracted_prompts_dir: str = "./extracted_content/prompts"):
        self.extracted_prompts_dir = Path(extracted_prompts_dir)
        self.categorized_prompts = defaultdict(lambda: defaultdict(list))
        
        # Define categories and their associated keywords
        self.functional_categories = {
            'coding': [
                'code', 'implement', 'create', 'write', 'develop', 'program', 'function', 
                'class', 'method', 'algorithm', 'debug', 'fix', 'refactor', 'optimize',
                'syntax', 'programming', 'software', 'application', 'script'
            ],
            'research': [
                'research', 'analyze', 'study', 'investigate', 'examine', 'explore', 
                'data', 'information', 'find', 'search', 'summary', 'report', 'insight'
            ],
            'content_creation': [
                'write', 'create', 'generate', 'draft', 'compose', 'design', 'content',
                'article', 'blog', 'story', 'text', 'narrative', 'copy', 'marketing'
            ],
            'problem_solving': [
                'solve', 'solution', 'problem', 'issue', 'troubleshoot', 'resolve', 
                'fix', 'overcome', 'address', 'handle', 'deal with', 'tackle'
            ],
            'planning': [
                'plan', 'strategy', 'outline', 'structure', 'organize', 'schedule',
                'timeline', 'roadmap', 'approach', 'methodology', 'framework'
            ],
            'learning': [
                'learn', 'understand', 'explain', 'teach', 'education', 'tutorial',
                'how to', 'guide', 'instructions', 'knowledge', 'concept', 'principle'
            ],
            'analysis': [
                'analyze', 'analysis', 'evaluate', 'assess', 'review', 'compare',
                'benchmark', 'metrics', 'performance', 'efficiency', 'quality'
            ],
            'design': [
                'design', 'ui', 'ux', 'interface', 'layout', 'visual', 'aesthetic',
                'prototype', 'wireframe', 'mockup', 'user experience', 'appearance'
            ]
        }
        
        self.project_categories = {
            'web_development': [
                'web', 'website', 'html', 'css', 'javascript', 'react', 'vue', 'angular',
                'frontend', 'backend', 'fullstack', 'api', 'rest', 'graphql', 'http',
                'server', 'client', 'framework', 'library', 'spa', 'pwa', 'responsive'
            ],
            'ai_ml': [
                'ai', 'ml', 'machine learning', 'neural', 'tensorflow', 'pytorch', 
                'model', 'algorithm', 'data science', 'deep learning', 'nlp', 'cv',
                'classification', 'regression', 'prediction', 'training', 'dataset'
            ],
            'mobile_development': [
                'mobile', 'ios', 'android', 'flutter', 'react native', 'app', 'application',
                'swift', 'kotlin', 'xamarin', 'native', 'cross-platform', 'mobile app'
            ],
            'data_analysis': [
                'data', 'analysis', 'analytics', 'database', 'sql', 'mysql', 'postgresql',
                'mongodb', 'excel', 'spreadsheet', 'visualization', 'dashboard', 'report'
            ],
            'devops': [
                'devops', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'aws', 'azure',
                'gcp', 'cloud', 'deployment', 'infrastructure', 'automation', 'pipeline'
            ],
            'security': [
                'security', 'encryption', 'authentication', 'authorization', 'firewall',
                'ssl', 'tls', 'vulnerability', 'penetration', 'secure', 'privacy'
            ],
            'gaming': [
                'game', 'gaming', 'unity', 'unreal', 'engine', '2d', '3d', 'graphics',
                'physics', 'multiplayer', 'vr', 'ar', 'simulation', 'rendering'
            ],
            'iot': [
                'iot', 'internet of things', 'arduino', 'raspberry pi', 'sensor',
                'embedded', 'hardware', 'microcontroller', 'rfid', 'bluetooth', 'wifi'
            ]
        }
        
        # Download required NLTK data (only if not already present)
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by tokenizing, removing stopwords, and lemmatizing.
        """
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation, then lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token.isalnum() and token not in self.stop_words
        ]
        
        return processed_tokens
    
    def categorize_single_prompt(self, prompt: str) -> Tuple[List[str], List[str]]:
        """
        Categorize a single prompt into functional and project categories.
        
        Returns:
            Tuple of (functional_categories, project_categories)
        """
        # Preprocess the prompt
        tokens = self.preprocess_text(prompt)
        prompt_lower = prompt.lower()
        
        # Identify functional categories
        functional_matches = set()
        for category, keywords in self.functional_categories.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    functional_matches.add(category)
                    break  # Break to avoid multiple matches from same category
        
        # If no functional category matched, use keyword analysis
        if not functional_matches:
            for token in tokens:
                for category, keywords in self.functional_categories.items():
                    if token in keywords:
                        functional_matches.add(category)
                        break
        
        # Identify project categories
        project_matches = set()
        for category, keywords in self.project_categories.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    project_matches.add(category)
                    break  # Break to avoid multiple matches from same category
        
        # If no project category matched, use keyword analysis
        if not project_matches:
            for token in tokens:
                for category, keywords in self.project_categories.items():
                    if token in keywords:
                        project_matches.add(category)
                        break
        
        # If still no matches, assign to 'general' categories
        if not functional_matches:
            functional_matches.add('general')
        
        if not project_matches:
            project_matches.add('general')
        
        return list(functional_matches), list(project_matches)
    
    def categorize_all_prompts(self):
        """
        Categorize all prompts from the extracted content directory.
        """
        print("Categorizing prompts...")
        
        prompt_files = list(self.extracted_prompts_dir.glob("*.txt"))
        
        if not prompt_files:
            print(f"No prompt files found in {self.extracted_prompts_dir}")
            return
        
        total_prompts = 0
        
        for prompt_file in prompt_files:
            print(f"Processing: {prompt_file.name}")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into individual prompts
            # Assuming prompts are separated by double newlines
            potential_prompts = content.split('\n\n')
            
            for potential_prompt in potential_prompts:
                # Clean up the prompt text
                clean_prompt = potential_prompt.strip()
                
                # Skip if it's just a header like "Prompt 1:"
                if re.match(r'^Prompt \d+:?$', clean_prompt):
                    continue
                
                # Skip if too short
                if len(clean_prompt) < 10:
                    continue
                
                # Categorize the prompt
                functional_cats, project_cats = self.categorize_single_prompt(clean_prompt)
                
                # Store in categorized structure
                for f_cat in functional_cats:
                    for p_cat in project_cats:
                        self.categorized_prompts[f_cat][p_cat].append({
                            'prompt': clean_prompt,
                            'source_file': prompt_file.name,
                            'functional_category': f_cat,
                            'project_category': p_cat
                        })
                
                total_prompts += 1
        
        print(f"Categorized {total_prompts} prompts into {len(self.categorized_prompts)} functional categories.")
    
    def save_categorized_prompts(self, output_dir: str = "./categorized_prompts"):
        """
        Save categorized prompts to organized JSON files.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create a summary of categories
        summary = {
            'functional_categories': list(self.categorized_prompts.keys()),
            'project_categories': set(),
            'category_counts': {},
            'total_prompts': 0
        }
        
        for f_cat, p_cats in self.categorized_prompts.items():
            for p_cat, prompts in p_cats.items():
                summary['project_categories'].add(p_cat)
                
                # Create filename-safe category names
                safe_f_cat = re.sub(r'[^a-zA-Z0-9_]', '_', f_cat)
                safe_p_cat = re.sub(r'[^a-zA-Z0-9_]', '_', p_cat)
                
                # Save prompts for this functional-project category combination
                category_file = output_path / f"{safe_f_cat}_{safe_p_cat}_prompts.json"
                
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts, f, indent=2, ensure_ascii=False)
                
                # Update summary
                category_key = f"{f_cat}_{p_cat}"
                summary['category_counts'][category_key] = len(prompts)
                summary['total_prompts'] += len(prompts)
        
        # Convert set back to list for JSON serialization
        summary['project_categories'] = list(summary['project_categories'])
        
        # Save summary
        summary_file = output_path / "categorization_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved categorized prompts to {output_path}")
        print(f"Total categorized prompts: {summary['total_prompts']}")
    
    def print_categorization_report(self):
        """
        Print a report of the categorization results.
        """
        print("\nCategorization Report")
        print("=" * 50)
        
        total_prompts = 0
        for f_cat, p_cats in self.categorized_prompts.items():
            print(f"\nFunctional Category: {f_cat}")
            print("-" * 30)
            
            for p_cat, prompts in p_cats.items():
                count = len(prompts)
                total_prompts += count
                print(f"  {p_cat}: {count} prompts")
        
        print(f"\nTotal Prompts Categorized: {total_prompts}")
        
        # Print top functional categories
        print(f"\nTop Functional Categories:")
        func_counts = {}
        for f_cat, p_cats in self.categorized_prompts.items():
            count = sum(len(prompts) for prompts in p_cats.values())
            func_counts[f_cat] = count
        
        sorted_func = sorted(func_counts.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_func[:5]:
            print(f"  {cat}: {count} prompts")
        
        # Print top project categories
        print(f"\nTop Project Categories:")
        proj_counts = {}
        for f_cat, p_cats in self.categorized_prompts.items():
            for p_cat, prompts in p_cats.items():
                if p_cat in proj_counts:
                    proj_counts[p_cat] += len(prompts)
                else:
                    proj_counts[p_cat] = len(prompts)
        
        sorted_proj = sorted(proj_counts.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_proj[:5]:
            print(f"  {cat}: {count} prompts")


def main():
    """
    Main function to run the prompt categorizer.
    """
    print("Prompt Categorizer")
    print("=" * 20)
    
    extracted_dir = input("Enter directory with extracted prompts (default: ./extracted_content/prompts): ").strip()
    if not extracted_dir:
        extracted_dir = "./extracted_content/prompts"
    
    output_dir = input("Enter output directory for categorized prompts (default: ./categorized_prompts): ").strip()
    if not output_dir:
        output_dir = "./categorized_prompts"
    
    categorizer = PromptCategorizer(extracted_dir)
    categorizer.categorize_all_prompts()
    categorizer.print_categorization_report()
    categorizer.save_categorized_prompts(output_dir)
    
    print("\nCategorization completed!")


if __name__ == "__main__":
    main()