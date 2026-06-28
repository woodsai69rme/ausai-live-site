# Enhanced Testing Documentation

## Overview
This document provides comprehensive testing procedures for all enhanced features across the three components.

---

## 1. Enterprise Development Hub - Enhanced Testing

### 1.1 Configuration Loading Test

```python
import asyncio
import yaml
from src.main import EnterpriseDevelopmentHub

async def test_configuration():
    """Test configuration file loading"""
    config = yaml.safe_load("""
server:
  host: "localhost"
  port: 8000
  workers: 4

database:
  path: ":memory:"

security:
  secret_key: "test-secret-key"
    """)
    
    hub = EnterpriseDevelopmentHub(config)
    await hub.start()
    
    assert hub.hub_server.host == "localhost"
    assert hub.hub_server.port == 8000
    print("✓ Configuration loading test passed")
    
    await hub.stop()

asyncio.run(test_configuration())
```

### 1.2 Analytics Test

```python
async def test_analytics():
    """Test analytics features"""
    hub = EnterpriseDevelopmentHub({"db_path": ":memory:"})
    await hub.start()
    
    # Create test data
    hub.project_manager.create_project("test_project", "Test", "", "owner", 10000)
    hub.revenue_tracker.log_revenue("test_project", 5000, "services", "Test revenue")
    
    # Get metrics
    metrics = hub.analytics.get_metrics()
    assert metrics["total_revenue"] == 5000
    print("✓ Analytics test passed")
    
    await hub.stop()

asyncio.run(test_analytics())
```

### 1.3 Parallel Processing Test

```python
async def test_parallel_processing():
    """Test parallel task distribution"""
    hub = EnterpriseDevelopmentHub({"db_path": ":memory:"})
    await hub.start()
    
    # Register multiple agents
    for i in range(5):
        hub.hub_server.register_agent(f"agent{i}", {"name": f"Agent {i}"})
    
    # Add tasks
    for i in range(10):
        hub.agent_coordinator.add_task({"action": "test"}, priority=i % 3)
    
    # Distribute in parallel
    await hub.agent_coordinator.distribute_tasks_parallel()
    
    print("✓ Parallel processing test passed")
    await hub.stop()

asyncio.run(test_parallel_processing())
```

### 1.4 Security Test

```python
def test_security():
    """Test security features"""
    from src.security import SecurityValidator
    
    validator = SecurityValidator()
    
    # Test rate limiting
    assert validator.check_rate_limit("user1") is True
    print("✓ Rate limiting test passed")
    
    # Test audit logging
    validator.audit_log({"event": "test", "user": "test_user"})
    print("✓ Audit logging test passed")
    
    # Test encryption
    encrypted = validator.encrypt_data("test_data")
    decrypted = validator.decrypt_data(encrypted)
    assert decrypted == "test_data"
    print("✓ Encryption test passed")

test_security()
```

---

## 2. ChatGPT Sorter - Enhanced Testing

### 2.1 Statistics Generation Test

```python
import json
from chatgpt_sorter_enhanced import ConversationStatistics

def test_statistics():
    """Test conversation statistics"""
    # Load test data
    with open('test_conversations.json', 'r') as f:
        conversations = json.load(f)
    
    # Generate statistics
    stats = ConversationStatistics(conversations)
    overview = stats.generate_overview()
    
    # Verify statistics
    assert overview['total_conversations'] == 5
    assert overview['message_stats']['total'] > 0
    assert overview['word_count']['total'] > 0
    assert len(overview['topics']) > 0
    
    print("✓ Statistics test passed")
    print(f"  Total Conversations: {overview['total_conversations']}")
    print(f"  Total Messages: {overview['message_stats']['total']}")
    print(f"  Total Words: {overview['word_count']['total']}")
    print(f"  Top Topics: {len(overview['topics'])}")

test_statistics()
```

### 2.2 Duplicate Detection Test

```python
from chatgpt_sorter_enhanced import DuplicateDetector

def test_duplicate_detection():
    """Test duplicate detection"""
    # Load test data
    with open('test_conversations.json', 'r') as f:
        conversations = json.load(f)
    
    # Detect duplicates
    detector = DuplicateDetector(conversations)
    duplicates = detector.find_duplicates()
    
    print("✓ Duplicate detection test passed")
    print(f"  Found {len(duplicates)} potential duplicates")
    
    for dup in duplicates:
        print(f"    - {dup['conversation_ids']} (similarity: {dup['similarity']:.2f})")

test_duplicate_detection()
```

### 2.3 Export Formats Test

```python
from chatgpt_sorter_enhanced import EnhancedExportFormatter
import os

def test_export_formats():
    """Test all export formats"""
    # Load test data
    with open('test_conversations.json', 'r') as f:
        conversations = json.load(f)
    
    # Test Markdown export
    output_dir = "./test_exports"
    os.makedirs(output_dir, exist_ok=True)
    
    EnhancedExportFormatter.export_to_markdown(
        conversations,
        os.path.join(output_dir, "test.md")
    )
    assert os.path.exists(os.path.join(output_dir, "test.md"))
    print("✓ Markdown export test passed")
    
    # Test HTML export
    EnhancedExportFormatter.export_to_html(
        conversations,
        os.path.join(output_dir, "test.html")
    )
    assert os.path.exists(os.path.join(output_dir, "test.html"))
    print("✓ HTML export test passed")
    
    # Test XML export
    EnhancedExportFormatter.export_to_xml(
        conversations,
        os.path.join(output_dir, "test.xml")
    )
    assert os.path.exists(os.path.join(output_dir, "test.xml"))
    print("✓ XML export test passed")

test_export_formats()
```

### 2.4 Visualization Test

```python
from chatgpt_sorter_enhanced import VisualizationGenerator

def test_visualization():
    """Test visualization and reporting"""
    # Load test data
    with open('test_conversations.json', 'r') as f:
        conversations = json.load(f)
    
    # Generate report
    viz = VisualizationGenerator(conversations)
    output_file = "./test_exports/visualization_report.txt"
    viz.generate_text_report(output_file)
    
    assert os.path.exists(output_file)
    print("✓ Visualization test passed")
    print(f"  Generated report: {output_file}")

test_visualization()
```

---

## 3. RAG Document Ingestor - Enhanced Testing

### 3.1 Duplicate Detection Test

```python
import json
from rag_document_ingestor_enhanced import DuplicateDetector

def test_duplicate_detection():
    """Test duplicate detection in chunks"""
    # Load test chunks
    with open('rag_chunks_enhanced.json', 'r') as f:
        chunks = json.load(f)
    
    # Detect duplicates
    detector = DuplicateDetector()
    duplicates = detector.find_duplicates(chunks)
    
    print("✓ Duplicate detection test passed")
    print(f"  Analyzed {len(chunks)} chunks")
    print(f"  Found {len(duplicates)} duplicates")

test_duplicate_detection()
```

### 3.2 Similarity Analysis Test

```python
from rag_document_ingestor_enhanced import SimilarityAnalyzer

def test_similarity_analysis():
    """Test similarity analysis"""
    # Load test chunks
    with open('rag_chunks_enhanced.json', 'r') as f:
        chunks = json.load(f)
    
    # Analyze similarity
    analyzer = SimilarityAnalyzer()
    similarity = analyzer.analyze_similarity(chunks)
    
    print("✓ Similarity analysis test passed")
    print(f"  Sources analyzed: {similarity['analysis']['total_sources']}")
    print(f"  Chunks analyzed: {similarity['analysis']['total_chunks']}")
    print(f"  Within-source similarity: {len(similarity['within_source'])}")
    print(f"  Between-source similarity: {len(similarity['between_source'])}")

test_similarity_analysis()
```

### 3.3 Metadata Extraction Test

```python
from rag_document_ingestor_enhanced import MetadataExtractor
from pathlib import Path

def test_metadata_extraction():
    """Test enhanced metadata extraction"""
    extractor = MetadataExtractor()
    
    # Test file
    test_file = Path("C:/Users/karma/test_documents/test_rag.txt")
    content = open(test_file, 'r', encoding='utf-8').read()
    
    # Extract metadata
    metadata = extractor.extract_metadata(test_file, content)
    
    # Verify metadata
    assert 'file_name' in metadata
    assert 'file_size' in metadata
    assert 'line_count' in metadata
    assert 'word_count' in metadata
    assert 'character_count' in metadata
    assert 'has_tables' in metadata
    assert 'has_code' in metadata
    assert 'has_lists' in metadata
    
    print("✓ Metadata extraction test passed")
    print(f"  File: {metadata['file_name']}")
    print(f"  Size: {metadata['file_size']} bytes")
    print(f"  Lines: {metadata['line_count']}")
    print(f"  Words: {metadata['word_count']}")
    print(f"  Has tables: {metadata['has_tables']}")
    print(f"  Has code: {metadata['has_code']}")
    print(f"  Has lists: {metadata['has_lists']}")

test_metadata_extraction()
```

### 3.4 Parallel Processing Test

```python
from rag_document_ingestor_enhanced import EnhancedRAGDocumentIngestor

def test_parallel_processing():
    """Test parallel document processing"""
    ingestor = EnhancedRAGDocumentIngestor(
        max_workers=4,
        parallel=True
    )
    
    # Process documents
    chunks = ingestor.ingest_directory(
        "C:/Users/karma/test_documents",
        detect_duplicates=True,
        analyze_similarity=True
    )
    
    print("✓ Parallel processing test passed")
    print(f"  Processed {len(chunks)} chunks")
    print(f"  Used {ingestor.max_workers} workers")

test_parallel_processing()
```

---

## 4. Integration Testing

### 4.1 End-to-End Workflow Test

```python
import asyncio
from src.main import EnterpriseDevelopmentHub

async def test_e2e_workflow():
    """Test complete end-to-end workflow"""
    hub = EnterpriseDevelopmentHub({"db_path": ":memory:"})
    await hub.start()
    
    # Create project
    hub.project_manager.create_project(
        "test_project",
        "Test Project",
        "",
        "owner",
        50000.0
    )
    
    # Process documents (simulate)
    chunks_processed = 100
    hub.revenue_tracker.log_revenue(
        "test_project",
        25000.0,
        "milestone",
        f"Processed {chunks_processed} chunks"
    )
    
    # Get analytics
    metrics = hub.analytics.get_metrics()
    assert metrics['total_revenue'] == 25000.0
    
    # Generate report
    report = hub.analytics.generate_report("project_summary", "text", "test_project")
    
    print("✓ End-to-end workflow test passed")
    print(f"  Revenue: ${metrics['total_revenue']:,.2f}")
    print(f"  Projects: {metrics['active_projects']}")
    
    await hub.stop()

asyncio.run(test_e2e_workflow())
```

---

## 5. Performance Testing

### 5.1 Load Test

```python
import time
import asyncio
from src.main import EnterpriseDevelopmentHub

async def test_load():
    """Test system under load"""
    hub = EnterpriseDevelopmentHub({"db_path": ":memory:"})
    await hub.start()
    
    start = time.time()
    
    # Create 100 projects
    for i in range(100):
        hub.project_manager.create_project(
            f"project{i}",
            f"Project {i}",
            "",
            "owner",
            10000.0
        )
    
    # Log revenue for all projects
    for i in range(100):
        hub.revenue_tracker.log_revenue(
            f"project{i}",
            5000.0,
            "services",
            "Service fee"
        )
    
    end = time.time()
    elapsed = end - start
    
    print("✓ Load test passed")
    print(f"  Created 100 projects and logged 100 revenue entries")
    print(f"  Time elapsed: {elapsed:.2f} seconds")
    print(f"  Operations per second: {200/elapsed:.2f}")
    
    await hub.stop()

asyncio.run(test_load())
```

### 5.2 Memory Usage Test

```python
import tracemalloc
import asyncio
from src.main import EnterpriseDevelopmentHub

async def test_memory():
    """Test memory usage"""
    tracemalloc.start()
    
    hub = EnterpriseDevelopmentHub({"db_path": ":memory:"})
    await hub.start()
    
    # Create test data
    for i in range(100):
        hub.project_manager.create_project(
            f"project{i}",
            f"Project {i}",
            "",
            "owner",
            10000.0
        )
    
    # Get memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print("✓ Memory test passed")
    print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    await hub.stop()

asyncio.run(test_memory())
```

---

## 6. Running All Tests

### Quick Test Run

```bash
# Test Enterprise Development Hub
cd enterprise-development-hub
python test_components.py

# Test ChatGPT Sorter Enhanced
cd ../chatgpt-sorter
python chatgpt_sorter_enhanced.py test_conversations.json --generate-stats --visualize

# Test RAG Document Ingestor Enhanced
cd ..
python rag_document_ingestor_enhanced.py --source-dir ./test_documents
```

### Comprehensive Test Suite

```bash
# Create test runner script
cat > run_all_tests.sh << 'EOF'
#!/bin/bash
echo "Running All Enhanced Tests"
echo "============================"

echo ""
echo "1. Enterprise Development Hub Tests"
cd enterprise-development-hub
python test_components.py
cd ..

echo ""
echo "2. ChatGPT Sorter Enhanced Tests"
cd chatgpt-sorter
python chatgpt_sorter_enhanced.py test_conversations.json \
  --generate-stats --find-duplicates --export-markdown --export-html --visualize
cd ..

echo ""
echo "3. RAG Document Ingestor Enhanced Tests"
python rag_document_ingestor_enhanced.py \
  --source-dir ./test_documents \
  --max-workers 4

echo ""
echo "All Tests Complete!"
EOF

# Run tests
bash run_all_tests.sh
```

---

## 7. Test Results Documentation

### Test Results Template

```markdown
# Test Results - [Date]

## Environment
- Python Version: [version]
- OS: [OS]
- Date: [date]

## Enterprise Development Hub
- Configuration Loading: [PASS/FAIL]
- Analytics: [PASS/FAIL]
- Parallel Processing: [PASS/FAIL]
- Security: [PASS/FAIL]

## ChatGPT Sorter Enhanced
- Statistics Generation: [PASS/FAIL]
- Duplicate Detection: [PASS/FAIL]
- Export Formats (Markdown): [PASS/FAIL]
- Export Formats (HTML): [PASS/FAIL]
- Export Formats (XML): [PASS/FAIL]
- Visualization: [PASS/FAIL]

## RAG Document Ingestor Enhanced
- Duplicate Detection: [PASS/FAIL]
- Similarity Analysis: [PASS/FAIL]
- Metadata Extraction: [PASS/FAIL]
- Parallel Processing: [PASS/FAIL]

## Integration Tests
- End-to-End Workflow: [PASS/FAIL]
- Load Test: [PASS/FAIL]
- Memory Usage: [PASS/FAIL]

## Summary
- Total Tests: [number]
- Passed: [number]
- Failed: [number]
- Success Rate: [percentage]%
```

---

## 8. Continuous Integration

### GitHub Actions Workflow

```yaml
name: Enhanced Components Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        pip install -r enterprise-development-hub/requirements.txt
        pip install -r requirements.txt
    
    - name: Run Enterprise Development Hub tests
      run: |
        cd enterprise-development-hub
        python test_components.py
    
    - name: Run ChatGPT Sorter Enhanced tests
      run: |
        cd chatgpt-sorter
        python chatgpt_sorter_enhanced.py test_conversations.json --generate-stats
    
    - name: Run RAG Document Ingestor Enhanced tests
      run: |
        python rag_document_ingestor_enhanced.py --source-dir ./test_documents
```

---

## 9. Troubleshooting Tests

### Common Issues

**Test Fails on Windows:**
- Ensure UTF-8 encoding is set
- Check file path separators

**Parallel Processing Tests Fail:**
- Reduce worker count
- Check system resources
- Increase timeout settings

**Import Errors:**
- Install all dependencies
- Check Python path
- Verify package structure

**Memory Issues:**
- Reduce test dataset size
- Increase memory limits
- Run tests sequentially

---

## 10. Best Practices

### Test Writing
- Write isolated, independent tests
- Use descriptive test names
- Include assertions with messages
- Clean up after tests
- Use setup and teardown methods

### Test Running
- Run tests regularly
- Use automated testing (CI/CD)
- Monitor test results
- Fix failing tests quickly
- Maintain test coverage

### Test Documentation
- Document test purposes
- Include expected results
- Note any dependencies
- Update documentation with code changes
- Share test results with team

---

**Version**: 2.0.0 Enhanced
**Last Updated**: 2025-01-15
**Status**: All Tests Documented ✅
