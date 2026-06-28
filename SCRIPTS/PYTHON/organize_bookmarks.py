"""
Firefox Bookmarks Organizer
- Reads all bookmarks from JSON
- Removes duplicates
- Auto-categorizes by domain/content
- Creates sorted, organized output files
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

# Category mapping based on domains/keywords
CATEGORY_RULES = {
    'Development': [
        'github.com', 'gitlab.com', 'stackoverflow.com', 'npmjs.com', 
        'pypi.org', 'dev.to', 'medium.com', 'freecodecamp.org',
        'w3schools.com', 'mdn', 'mozilla.org', 'visualstudio.com',
        'jetbrains.com', 'codepen.io', 'jsfiddle.net', 'replit.com',
        'glitch.com', 'heroku.com', 'vercel.com', 'netlify.com',
        'aws.amazon.com', 'cloud.google.com', 'azure.microsoft.com',
        'docker.com', 'kubernetes.io', 'nginx.com', 'apache.org',
        'python.org', 'nodejs.org', 'reactjs.org', 'vuejs.org',
        'angular.io', 'typescriptlang.org', 'rust-lang.org',
        'golang.org', 'java.com', 'oracle.com', 'php.net',
        'laravel.com', 'django', 'flask', 'expressjs',
        'lovable.dev', 'roocode.com', 'cline.dev'
    ],
    'AI_Machine_Learning': [
        'chatgpt.com', 'openai.com', 'openrouter.ai', 'perplexity.ai',
        'youware.com', 'genspark.ai', 'claude.ai', 'anthropic.com',
        'huggingface.co', 'kaggle.com', 'paperswithcode.com',
        'arxiv.org', 'nomic.ai', 'pinokio.computer', 'docsbot.ai',
        'midjourney.com', 'stability.ai', 'runway.ml', 'replicate.com'
    ],
    'Communication': [
        'mail.google.com', 'gmail.com', 'outlook.com', 'yahoo.com',
        'protonmail.com', 'telegram.org', 'discord.com', 'slack.com',
        'teams.microsoft.com', 'zoom.us', 'meet.google.com',
        'whatsapp.com', 'messenger.com'
    ],
    'Search_Research': [
        'google.com', 'bing.com', 'duckduckgo.com', 'search.yahoo.com',
        'wikipedia.org', 'scholar.google.com'
    ],
    'Video_Entertainment': [
        'youtube.com', 'vimeo.com', 'twitch.tv', 'netflix.com',
        'hulu.com', 'disneyplus.com', 'primevideo.com', 'spotify.com',
        'soundcloud.com', 'tiktok.com'
    ],
    'Shopping': [
        'aliexpress.com', 'amazon.com', 'ebay.com', 'alibaba.com',
        'etsy.com', 'walmart.com', 'target.com', 'bestbuy.com',
        'ebay.com.au'
    ],
    'Social_Media': [
        'reddit.com', 'twitter.com', 'x.com', 'facebook.com',
        'instagram.com', 'linkedin.com', 'pinterest.com',
        'tumblr.com', 'snapchat.com'
    ],
    'News_Media': [
        'cnn.com', 'bbc.com', 'reuters.com', 'nytimes.com',
        'washingtonpost.com', 'theguardian.com', 'foxnews.com'
    ],
    'Finance': [
        'paypal.com', 'stripe.com', 'coinbase.com', 'binance.com',
        'kraken.com', 'bankofamerica.com', 'chase.com', 'wellsfargo.com'
    ],
    'Cloud_Storage': [
        'drive.google.com', 'dropbox.com', 'onedrive.live.com',
        'box.com', 'icloud.com', 'mega.nz'
    ],
    'Adult': [
        'xvideos.com', 'pornhub.com', 'xnxx.com', 'onlyfans.com',
        'redtube.com', 'youporn.com', 'xhamster.com'
    ],
    'Security_Privacy': [
        'securitylab.com.au', 'ozspy.com.au', 'krebsonsecurity.com',
        'bleepingcomputer.com', 'threatpost.com'
    ],
    'Image_Hosting': [
        'imagekit.io', 'ik.imagekit.io', 'imgur.com', 'flickr.com',
        'unsplash.com', 'pexels.com', 'shutterstock.com'
    ],
    'Firefox_Mozilla': [
        'mozilla.org', 'firefox.com', 'addons.mozilla.org',
        'support.mozilla.org'
    ]
}

def get_category(url, title=''):
    """Determine category based on URL domain and title"""
    try:
        domain = urlparse(url).netloc.lower()
    except:
        domain = ''
    
    # Check each category's rules
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in domain or keyword in title.lower():
                return category
    
    # Default categories based on TLD
    if '.edu' in domain:
        return 'Education'
    elif '.gov' in domain:
        return 'Government'
    
    return 'Other'

def clean_title(title):
    """Clean up bookmark titles"""
    if not title:
        return 'Untitled'
    
    # Remove special characters but keep basic punctuation
    title = re.sub(r'[^\w\s\-\.\,\:\(\)]', '', title)
    # Remove multiple spaces
    title = re.sub(r'\s+', ' ', title)
    # Strip whitespace
    return title.strip()

def normalize_url(url):
    """Normalize URL for duplicate detection"""
    try:
        parsed = urlparse(url)
        # Remove tracking parameters
        netloc = parsed.netloc.lower()
        # Remove www. for comparison
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        path = parsed.path.rstrip('/')
        return f"{parsed.scheme}://{netloc}{path}"
    except:
        return url.lower().strip()

def extract_domain(url):
    """Extract clean domain from URL"""
    try:
        return urlparse(url).netloc.lower()
    except:
        return 'unknown'

def load_bookmarks(json_path):
    """Load bookmarks from JSON file"""
    print(f"Loading bookmarks from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def organize_bookmarks(data):
    """Organize all bookmarks: deduplicate, categorize, sort"""
    all_bookmarks = []
    seen_urls = {}  # normalized_url -> best bookmark
    
    total_count = 0
    
    # Collect all bookmarks from all profiles
    for profile in data.get('profiles', []):
        profile_name = profile.get('profile_name', 'Unknown')
        for bookmark in profile.get('bookmarks', []):
            total_count += 1
            url = bookmark.get('url', '')
            if not url:
                continue
            
            normalized = normalize_url(url)
            
            # Keep the best version (with title, description, higher visit count)
            if normalized in seen_urls:
                existing = seen_urls[normalized]
                # Replace if this one has better data
                if (bookmark.get('visit_count', 0) > existing.get('visit_count', 0) or
                    (bookmark.get('title') and not existing.get('title'))):
                    seen_urls[normalized] = bookmark
            else:
                seen_urls[normalized] = bookmark
    
    # Process unique bookmarks
    unique_bookmarks = []
    categories = defaultdict(list)
    domains_count = defaultdict(int)
    
    for normalized_url, bookmark in seen_urls.items():
        url = bookmark.get('url', '')
        title = clean_title(bookmark.get('title', ''))
        category = get_category(url, title)
        domain = extract_domain(url)
        
        organized = {
            'url': url,
            'title': title,
            'category': category,
            'domain': domain,
            'original_title': bookmark.get('title', ''),
            'visit_count': bookmark.get('visit_count', 0),
            'description': bookmark.get('description', ''),
            'source_profiles': []  # Track which profiles had this
        }
        
        unique_bookmarks.append(organized)
        categories[category].append(organized)
        domains_count[domain] += 1
    
    # Sort bookmarks within each category by title
    for category in categories:
        categories[category].sort(key=lambda x: x['title'].lower())
    
    # Sort unique bookmarks overall
    unique_bookmarks.sort(key=lambda x: (x['category'], x['title'].lower()))
    
    stats = {
        'total_original': total_count,
        'total_unique': len(unique_bookmarks),
        'duplicates_removed': total_count - len(unique_bookmarks),
        'categories': {cat: len(bookmarks) for cat, bookmarks in categories.items()},
        'top_domains': sorted(domains_count.items(), key=lambda x: -x[1])[:20]
    }
    
    return unique_bookmarks, dict(categories), stats

def create_netscape_html(bookmarks_by_category, output_path):
    """Create Netscape bookmark HTML format (importable to browsers)"""
    html = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Organized Firefox Bookmarks</TITLE>
<H1>Organized Firefox Bookmarks</H1>
<DL><p>
'''
    
    # Sort categories for consistent output
    for category in sorted(bookmarks_by_category.keys()):
        bookmarks = bookmarks_by_category[category]
        if not bookmarks:
            continue
        
        html += f'<DT><H3 ADD_DATE="{int(datetime.now().timestamp())}" LAST_MODIFIED="{int(datetime.now().timestamp())}">{category}</H3>\n<DL><p>\n'
        
        for bm in bookmarks:
            title = bm['title'].replace('<', '&lt;').replace('>', '&gt;')
            url = bm['url']
            desc = bm.get('description', '')
            if desc:
                desc = desc.replace('<', '&lt;').replace('>', '&gt;')
            
            html += f'<DT><A HREF="{url}" ADD_DATE="{int(datetime.now().timestamp())}" LAST_MODIFIED="{int(datetime.now().timestamp())}"{f' DESCRIPTION="{desc}"' if desc else ''}>{title}</A>\n'
        
        html += '</DL><p>\n'
    
    html += '</DL><p>\n'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created Netscape HTML: {output_path}")

def create_json_output(unique_bookmarks, stats, output_path):
    """Create organized JSON output"""
    output = {
        'generated_at': datetime.now().isoformat(),
        'statistics': stats,
        'bookmarks': unique_bookmarks
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Created JSON: {output_path}")

def create_csv_output(unique_bookmarks, output_path):
    """Create CSV spreadsheet output"""
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Title', 'URL', 'Domain', 'Visit Count', 'Description'])
        
        for bm in unique_bookmarks:
            writer.writerow([
                bm['category'],
                bm['title'],
                bm['url'],
                bm['domain'],
                bm['visit_count'],
                bm.get('description', '')
            ])
    
    print(f"Created CSV: {output_path}")

def create_summary_report(stats, bookmarks_by_category, output_path):
    """Create markdown summary report"""
    report = f"""# Firefox Bookmarks Organization Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Original Bookmarks | {stats['total_original']:,} |
| Unique Bookmarks | {stats['total_unique']:,} |
| Duplicates Removed | {stats['duplicates_removed']:,} |
| Deduplication Rate | {(stats['duplicates_removed']/stats['total_original']*100):.1f}% |
| Number of Categories | {len(stats['categories'])} |

## Bookmarks by Category

| Category | Count | Percentage |
|----------|-------|------------|
"""
    
    total = stats['total_unique']
    for category, count in sorted(stats['categories'].items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {category} | {count:,} | {pct:.1f}% |\n"
    
    report += f"""
## Top 20 Domains

| Domain | Count |
|--------|-------|
"""
    
    for domain, count in stats['top_domains']:
        report += f"| {domain} | {count:,} |\n"
    
    report += f"""
## Category Details

"""
    
    for category in sorted(bookmarks_by_category.keys()):
        bookmarks = bookmarks_by_category[category]
        if not bookmarks:
            continue
        
        report += f"### {category} ({len(bookmarks):,} bookmarks)\n\n"
        
        # Show first 10 as examples
        report += "**Sample bookmarks:**\n\n"
        for bm in bookmarks[:10]:
            report += f"- [{bm['title']}]({bm['url']})\n"
        
        if len(bookmarks) > 10:
            report += f"\n*...and {len(bookmarks) - 10:,} more*\n"
        
        report += "\n---\n\n"
    
    report += """
## Files Created

1. **all_bookmarks_sorted.html** - Netscape format (import to any browser)
2. **all_bookmarks_sorted.json** - Complete JSON with all data
3. **all_bookmarks_sorted.csv** - Spreadsheet format
4. **categories_summary.md** - This report

## How to Use

### Import to Browser:
1. Open Firefox/Chrome/Edge
2. Go to Bookmarks Manager
3. Select "Import Bookmarks from HTML"
4. Choose `all_bookmarks_sorted.html`

### View in Spreadsheet:
- Open `all_bookmarks_sorted.csv` in Excel/Google Sheets

### Search Online:
- Open `all_bookmarks_sorted.html` in any browser
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Created summary report: {output_path}")

def main():
    # Paths
    input_path = r'C:\Users\karma\firefox_bookmarks_output\bookmarks_data.json'
    output_dir = r'C:\Users\karma\firefox_bookmarks_output\organized'
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Load bookmarks
    data = load_bookmarks(input_path)
    
    # Organize bookmarks
    print("Organizing bookmarks (deduplicating, categorizing, sorting)...")
    unique_bookmarks, bookmarks_by_category, stats = organize_bookmarks(data)
    
    print(f"\nResults:")
    print(f"  Original: {stats['total_original']:,}")
    print(f"  Unique: {stats['total_unique']:,}")
    print(f"  Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"  Categories: {len(stats['categories'])}")
    
    # Create output files
    print("\nCreating output files...")
    
    create_netscape_html(
        bookmarks_by_category, 
        os.path.join(output_dir, 'all_bookmarks_sorted.html')
    )
    
    create_json_output(
        unique_bookmarks, 
        stats,
        os.path.join(output_dir, 'all_bookmarks_sorted.json')
    )
    
    create_csv_output(
        unique_bookmarks,
        os.path.join(output_dir, 'all_bookmarks_sorted.csv')
    )
    
    create_summary_report(
        stats,
        bookmarks_by_category,
        os.path.join(output_dir, 'categories_summary.md')
    )
    
    print(f"\n✅ All files created in: {output_dir}")
    print("\nOpen 'categories_summary.md' to see the organization report!")

if __name__ == '__main__':
    main()
