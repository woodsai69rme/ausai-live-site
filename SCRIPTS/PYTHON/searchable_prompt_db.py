import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import hashlib
from datetime import datetime
import re


class SearchablePromptDatabase:
    """
    Creates and manages a searchable database of prompts and solutions
    extracted from various sources, with full-text search capabilities.
    """
    
    def __init__(self, db_path: str = "./prompts_solutions.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        self.conn = sqlite3.connect(self.db_path)
        
        # Enable full-text search extension
        self.conn.enable_load_extension(True)
        
        # Create tables
        cursor = self.conn.cursor()
        
        # Table for prompts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_text TEXT NOT NULL,
                source_file TEXT,
                functional_category TEXT,
                project_category TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash TEXT UNIQUE
            )
        ''')
        
        # Table for code solutions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution_code TEXT NOT NULL,
                language TEXT,
                prompt_id INTEGER,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash TEXT UNIQUE,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id)
            )
        ''')
        
        # Table for conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_data TEXT,
                source_file TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create FTS (Full-Text Search) table for prompts
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS prompts_fts USING fts5(
                prompt_text, 
                source_file, 
                functional_category, 
                project_category,
                content='prompts'
            )
        ''')
        
        # Create FTS table for solutions
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS solutions_fts USING fts5(
                solution_code, 
                language,
                content='solutions'
            )
        ''')
        
        # Create triggers to keep FTS tables synchronized
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS prompts_ai AFTER INSERT ON prompts
            BEGIN
                INSERT INTO prompts_fts(rowid, prompt_text, source_file, functional_category, project_category)
                VALUES (new.id, new.prompt_text, new.source_file, new.functional_category, new.project_category);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS prompts_ad AFTER DELETE ON prompts
            BEGIN
                INSERT INTO prompts_fts(prompts_fts, rowid, prompt_text, source_file, functional_category, project_category)
                VALUES('delete', old.id, old.prompt_text, old.source_file, old.functional_category, old.project_category);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS prompts_au AFTER UPDATE ON prompts
            BEGIN
                INSERT INTO prompts_fts(prompts_fts, rowid, prompt_text, source_file, functional_category, project_category)
                VALUES('delete', old.id, old.prompt_text, old.source_file, old.functional_category, old.project_category);
                INSERT INTO prompts_fts(rowid, prompt_text, source_file, functional_category, project_category)
                VALUES (new.id, new.prompt_text, new.source_file, new.functional_category, new.project_category);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS solutions_ai AFTER INSERT ON solutions
            BEGIN
                INSERT INTO solutions_fts(rowid, solution_code, language)
                VALUES (new.id, new.solution_code, new.language);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS solutions_ad AFTER DELETE ON solutions
            BEGIN
                INSERT INTO solutions_fts(solutions_fts, rowid, solution_code, language)
                VALUES('delete', old.id, old.solution_code, old.language);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS solutions_au AFTER UPDATE ON solutions
            BEGIN
                INSERT INTO solutions_fts(solutions_fts, rowid, solution_code, language)
                VALUES('delete', old.id, old.solution_code, old.language);
                INSERT INTO solutions_fts(rowid, solution_code, language)
                VALUES (new.id, new.solution_code, new.language);
            END
        ''')
        
        self.conn.commit()
        print(f"Database initialized at {self.db_path}")
    
    def calculate_hash(self, text: str) -> str:
        """Calculate SHA256 hash of text for deduplication."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def insert_prompt(self, prompt_text: str, source_file: str = "", functional_category: str = "", project_category: str = "") -> int:
        """Insert a prompt into the database."""
        cursor = self.conn.cursor()
        prompt_hash = self.calculate_hash(prompt_text)
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO prompts 
                (prompt_text, source_file, functional_category, project_category, hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (prompt_text, source_file, functional_category, project_category, prompt_hash))
            
            self.conn.commit()
            
            # Get the ID of the inserted (or existing) record
            cursor.execute('SELECT id FROM prompts WHERE hash = ?', (prompt_hash,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error inserting prompt: {e}")
            return None
    
    def insert_solution(self, solution_code: str, language: str, prompt_id: int) -> bool:
        """Insert a solution into the database."""
        cursor = self.conn.cursor()
        solution_hash = self.calculate_hash(solution_code)
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO solutions 
                (solution_code, language, prompt_id, hash)
                VALUES (?, ?, ?, ?)
            ''', (solution_code, language, prompt_id, solution_hash))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting solution: {e}")
            return False
    
    def insert_conversation(self, conversation_data: dict, source_file: str) -> bool:
        """Insert a conversation into the database."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO conversations 
                (conversation_data, source_file)
                VALUES (?, ?)
            ''', (json.dumps(conversation_data), source_file))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting conversation: {e}")
            return False
    
    def populate_from_extracted_content(self, extracted_dir: str = "./extracted_content"):
        """Populate the database from extracted content."""
        extracted_path = Path(extracted_dir)
        
        print("Populating database from extracted content...")
        
        # Process categorized prompts
        categorized_dir = extracted_path / "categorized_prompts"
        if categorized_dir.exists():
            for json_file in categorized_dir.glob("*_prompts.json"):
                print(f"Processing: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                
                for prompt_data in prompts:
                    prompt_text = prompt_data.get('prompt', '')
                    source_file = prompt_data.get('source_file', '')
                    functional_category = prompt_data.get('functional_category', '')
                    project_category = prompt_data.get('project_category', '')
                    
                    if prompt_text:
                        prompt_id = self.insert_prompt(
                            prompt_text, 
                            source_file, 
                            functional_category, 
                            project_category
                        )
        
        # Process code snippets
        code_dir = extracted_path / "code_snippets"
        if code_dir.exists():
            for json_file in code_dir.glob("*.json"):
                print(f"Processing code snippets: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    code_snippets = json.load(f)
                
                for snippet in code_snippets:
                    code_text = snippet.get('code', '')
                    language = snippet.get('language', 'unknown')
                    
                    if code_text and language:
                        # Try to find a related prompt in the database
                        # For now, we'll insert as orphaned solutions
                        # In a real scenario, you'd link these to specific prompts
                        cursor = self.conn.cursor()
                        cursor.execute('SELECT id FROM prompts ORDER BY RANDOM() LIMIT 1')
                        result = cursor.fetchone()
                        
                        if result:
                            prompt_id = result[0]
                            self.insert_solution(code_text, language, prompt_id)
                        else:
                            # If no prompts exist yet, create a placeholder prompt
                            placeholder_prompt = f"Code solution in {language}"
                            prompt_id = self.insert_prompt(placeholder_prompt, "system_generated")
                            if prompt_id:
                                self.insert_solution(code_text, language, prompt_id)
        
        # Process conversations
        conv_dir = extracted_path / "conversations"
        if conv_dir.exists():
            for json_file in conv_dir.glob("*.json"):
                print(f"Processing conversation: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                
                for conv_data in conversations:
                    self.insert_conversation(conv_data.get('content', {}), json_file.name)
        
        print("Database population completed.")
    
    def search_prompts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for prompts using full-text search."""
        cursor = self.conn.cursor()
        
        # Use FTS to search
        cursor.execute('''
            SELECT p.id, p.prompt_text, p.source_file, p.functional_category, p.project_category, p.extracted_at
            FROM prompts p
            JOIN prompts_fts pf ON p.rowid = pf.rowid
            WHERE pf MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'prompt_text': row[1],
                'source_file': row[2],
                'functional_category': row[3],
                'project_category': row[4],
                'extracted_at': row[5]
            })
        
        return results
    
    def search_solutions(self, query: str, language: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for solutions using full-text search."""
        cursor = self.conn.cursor()
        
        if language:
            cursor.execute('''
                SELECT s.id, s.solution_code, s.language, p.prompt_text
                FROM solutions s
                JOIN solutions_fts sf ON s.rowid = sf.rowid
                LEFT JOIN prompts p ON s.prompt_id = p.id
                WHERE sf MATCH ? AND s.language = ?
                ORDER BY rank
                LIMIT ?
            ''', (query, language, limit))
        else:
            cursor.execute('''
                SELECT s.id, s.solution_code, s.language, p.prompt_text
                FROM solutions s
                JOIN solutions_fts sf ON s.rowid = sf.rowid
                LEFT JOIN prompts p ON s.prompt_id = p.id
                WHERE sf MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'solution_code': row[1],
                'language': row[2],
                'related_prompt': row[3]
            })
        
        return results
    
    def search_by_category(self, functional_category: str = None, project_category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for prompts by category."""
        cursor = self.conn.cursor()
        
        conditions = []
        params = []
        
        if functional_category:
            conditions.append("functional_category = ?")
            params.append(functional_category)
        
        if project_category:
            conditions.append("project_category = ?")
            params.append(project_category)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f'''
            SELECT id, prompt_text, source_file, functional_category, project_category, extracted_at
            FROM prompts
            WHERE {where_clause}
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'prompt_text': row[1],
                'source_file': row[2],
                'functional_category': row[3],
                'project_category': row[4],
                'extracted_at': row[5]
            })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the database content."""
        cursor = self.conn.cursor()
        
        # Count prompts
        cursor.execute("SELECT COUNT(*) FROM prompts")
        prompt_count = cursor.fetchone()[0]
        
        # Count solutions
        cursor.execute("SELECT COUNT(*) FROM solutions")
        solution_count = cursor.fetchone()[0]
        
        # Count conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        
        # Get unique functional categories
        cursor.execute("SELECT DISTINCT functional_category FROM prompts WHERE functional_category IS NOT NULL")
        functional_categories = [row[0] for row in cursor.fetchall()]
        
        # Get unique project categories
        cursor.execute("SELECT DISTINCT project_category FROM prompts WHERE project_category IS NOT NULL")
        project_categories = [row[0] for row in cursor.fetchall()]
        
        # Get languages used in solutions
        cursor.execute("SELECT DISTINCT language FROM solutions WHERE language IS NOT NULL")
        languages = [row[0] for row in cursor.fetchall()]
        
        return {
            'total_prompts': prompt_count,
            'total_solutions': solution_count,
            'total_conversations': conversation_count,
            'functional_categories': functional_categories,
            'project_categories': project_categories,
            'languages_used': languages
        }
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


class SearchInterface:
    """Provides a user-friendly interface for searching the prompt database."""
    
    def __init__(self, db_path: str = "./prompts_solutions.db"):
        self.db = SearchablePromptDatabase(db_path)
    
    def search(self, query: str, search_type: str = "both", limit: int = 10):
        """Perform a search based on the specified type."""
        if search_type == "prompts":
            return self.db.search_prompts(query, limit)
        elif search_type == "solutions":
            # Extract language from query if specified
            language_match = re.search(r'in (\w+)', query, re.IGNORECASE)
            language = language_match.group(1) if language_match else None
            
            # Clean query to remove language specification
            clean_query = re.sub(r'\s+in\s+\w+', '', query, flags=re.IGNORECASE).strip()
            
            return self.db.search_solutions(clean_query, language, limit)
        elif search_type == "both":
            prompts = self.db.search_prompts(query, limit // 2)
            solutions = self.db.search_solutions(query, limit=limit // 2)
            return {"prompts": prompts, "solutions": solutions}
        else:
            raise ValueError("search_type must be 'prompts', 'solutions', or 'both'")
    
    def search_by_category(self, functional_category: str = None, project_category: str = None, limit: int = 10):
        """Search by category."""
        return self.db.search_by_category(functional_category, project_category, limit)
    
    def get_stats(self):
        """Get database statistics."""
        return self.db.get_statistics()
    
    def close(self):
        """Close the database connection."""
        self.db.close()


def main():
    """Main function to demonstrate the searchable database."""
    print("Searchable Prompt Database")
    print("=" * 30)
    
    db_path = input("Enter database path (default: ./prompts_solutions.db): ").strip()
    if not db_path:
        db_path = "./prompts_solutions.db"
    
    extracted_dir = input("Enter directory with extracted content (default: ./extracted_content): ").strip()
    if not extracted_dir:
        extracted_dir = "./extracted_content"
    
    # Initialize the database
    db = SearchablePromptDatabase(db_path)
    
    # Populate from extracted content
    if Path(extracted_dir).exists():
        db.populate_from_extracted_content(extracted_dir)
    else:
        print(f"Warning: {extracted_dir} does not exist. Skipping population.")
    
    # Show statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(f"  Total Prompts: {stats['total_prompts']}")
    print(f"  Total Solutions: {stats['total_solutions']}")
    print(f"  Total Conversations: {stats['total_conversations']}")
    print(f"  Functional Categories: {', '.join(stats['functional_categories'])}")
    print(f"  Project Categories: {', '.join(stats['project_categories'])}")
    print(f"  Languages Used: {', '.join(stats['languages_used'])}")
    
    # Interactive search
    print("\nInteractive Search (type 'quit' to exit):")
    while True:
        query = input("\nEnter search query: ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        search_type = input("Search type (prompts/solutions/both - default: both): ").strip().lower()
        if not search_type:
            search_type = "both"
        
        try:
            results = db.search(query, search_type=search_type)
            
            if search_type == "both":
                print(f"\nPrompts matching '{query}':")
                for i, prompt in enumerate(results["prompts"], 1):
                    print(f"  {i}. [{prompt['functional_category']}/{prompt['project_category']}] {prompt['prompt_text'][:100]}...")
                
                print(f"\nSolutions matching '{query}':")
                for i, solution in enumerate(results["solutions"], 1):
                    preview = solution['solution_code'][:100] + "..." if len(solution['solution_code']) > 100 else solution['solution_code']
                    print(f"  {i}. [{solution['language']}] {preview}")
            elif search_type == "prompts":
                for i, prompt in enumerate(results, 1):
                    print(f"  {i}. [{prompt['functional_category']}/{prompt['project_category']}] {prompt['prompt_text'][:100]}...")
            elif search_type == "solutions":
                for i, solution in enumerate(results, 1):
                    preview = solution['solution_code'][:100] + "..." if len(solution['solution_code']) > 100 else solution['solution_code']
                    print(f"  {i}. [{solution['language']}] {preview}")
            
            if not any(results.values()) if isinstance(results, dict) else not results:
                print("  No results found.")
        
        except Exception as e:
            print(f"Search error: {e}")
    
    db.close()
    print("\nDatabase closed. Searchable prompt database created successfully!")


if __name__ == "__main__":
    main()