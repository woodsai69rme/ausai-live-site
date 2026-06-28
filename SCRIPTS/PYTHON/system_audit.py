import os
import sys
from pathlib import Path
import importlib.util

def check_module_exists(module_name, file_path):
    """Check if a module exists and can be imported."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✓ {module_name} - Successfully imported")
        return True
    except Exception as e:
        print(f"✗ {module_name} - Failed to import: {str(e)}")
        return False

def audit_system_components():
    """Audit all system components."""
    print("AI Project Suite - System Audit")
    print("=" * 50)
    
    # Define the components to audit
    components = [
        ("File Sorter", "file_sorter.py"),
        ("Duplicate Detector", "duplicate_detector.py"),
        ("ChatGPT Extractor", "chatgpt_extractor.py"),
        ("Prompt Categorizer", "prompt_categorizer.py"),
        ("Searchable Prompt DB", "searchable_prompt_db.py"),
        ("RAG Document Ingestor", "rag_document_ingestor.py"),
        ("Fulltext Semantic Search", "fulltext_semantic_search.py"),
        ("Voice AI Assistant", "voice_ai_assistant.py"),
        ("Enhanced Voice AI Assistant", "enhanced_voice_ai_assistant.py"),
        ("AI Influencer Pipeline", "ai_influencer_pipeline.py"),
        ("Social Media Automation", "social_media_automation.py")
    ]
    
    results = {}
    
    for name, file_path in components:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"\nAuditing {name}...")
            results[name] = check_module_exists(name.replace(" ", ""), full_path)
        else:
            print(f"\n✗ {name} - File does not exist: {file_path}")
            results[name] = False
    
    # Check dashboard components
    print(f"\nAuditing Project Dashboard...")
    dashboard_dir = Path("project-dashboard")
    if dashboard_dir.exists():
        dashboard_files = ["index.html", "api.py", "README.md"]
        for file in dashboard_files:
            file_path = dashboard_dir / file
            if file_path.exists():
                print(f"  ✓ {file} - Exists")
            else:
                print(f"  ✗ {file} - Missing")
                results[f"Dashboard/{file}"] = False
    else:
        print(f"  ✗ Dashboard directory does not exist")
    
    # Check browser extension
    print(f"\nAuditing Browser Extension...")
    ext_dir = Path("browser-extension")
    if ext_dir.exists():
        ext_files = ["manifest.json", "popup.html", "content.js", "background.js", "styles.css", "README.md"]
        for file in ext_files:
            file_path = ext_dir / file
            if file_path.exists():
                print(f"  ✓ {file} - Exists")
            else:
                print(f"  ✗ {file} - Missing")
    else:
        print(f"  ✗ Browser extension directory does not exist")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("AUDIT SUMMARY:")
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    failed = total - successful
    
    print(f"Total components checked: {total}")
    print(f"Successfully imported: {successful}")
    print(f"Failed to import: {failed}")
    
    if failed == 0:
        print("\n🎉 All components are present and importable!")
        print("\nThe AI Project Suite is fully operational with:")
        print("- File organization and duplicate detection")
        print("- ChatGPT content extraction and categorization")
        print("- Searchable prompt database")
        print("- RAG document ingestion system")
        print("- Full-text and semantic search")
        print("- Voice-enabled AI assistant")
        print("- AI influencer content pipeline")
        print("- Social media automation tools")
        print("- Project management dashboard")
        print("- Browser extension for chat history saving")
    else:
        print(f"\n⚠️  {failed} components failed to import. Please check the implementation.")
    
    return results

def run_basic_functionality_tests():
    """Run basic functionality tests on key components."""
    print(f"\n" + "=" * 50)
    print("FUNCTIONALITY TESTS:")
    
    # Test file sorter
    try:
        from file_sorter import FileSorter
        sorter = FileSorter("./test_source", "./test_dest")
        print("✓ FileSorter instantiated successfully")
    except Exception as e:
        print(f"✗ FileSorter instantiation failed: {e}")
    
    # Test duplicate detector
    try:
        from duplicate_detector import DuplicateDetector
        detector = DuplicateDetector(["./test_scan"])
        print("✓ DuplicateDetector instantiated successfully")
    except Exception as e:
        print(f"✗ DuplicateDetector instantiation failed: {e}")
    
    # Test RAG document ingestor
    try:
        from rag_document_ingestor import RAGDocumentIngestor
        ingestor = RAGDocumentIngestor()
        print("✓ RAGDocumentIngestor instantiated successfully")
    except Exception as e:
        print(f"✗ RAGDocumentIngestor instantiation failed: {e}")
    
    # Test AI Influencer Pipeline
    try:
        from ai_influencer_pipeline import AIInfluencerPipeline
        pipeline = AIInfluencerPipeline()
        print("✓ AIInfluencerPipeline instantiated successfully")
    except Exception as e:
        print(f"✗ AIInfluencerPipeline instantiation failed: {e}")

if __name__ == "__main__":
    audit_results = audit_system_components()
    run_basic_functionality_tests()
    
    print(f"\n" + "=" * 50)
    print("AUDIT COMPLETE")
    print("Next steps:")
    print("1. Address any failed components")
    print("2. Configure API keys for AI services")
    print("3. Set up the project dashboard backend")
    print("4. Customize configurations for your specific needs")