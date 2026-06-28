import re

# Read the file
with open(r'C:\Users\karma\PROJECTS\ACTIVE\youtube_enhancement_tools\social_media\instagram.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)}")
print(f"Contains random.sample: {'random.sample' in content}")

# Find and replace the problematic code
old_code = """        # Create recommended mix (Instagram best practice)
        # Mix of high, medium, and low competition
        hashtag_set.recommended_mix = (
            random.sample(hashtag_set.high_competition, 3) +
            random.sample(hashtag_set.medium_competition, 5) +
            random.sample(hashtag_set.low_competition, 5) +
            hashtag_set.branded[:2]
        )[:self.RECOMMENDED_HASHTAGS]"""

new_code = """        # Create recommended mix (Instagram best practice)
        # Mix of high, medium, and low competition
        # Use min() to avoid sampling more than available
        high_count = min(3, len(hashtag_set.high_competition))
        medium_count = min(5, len(hashtag_set.medium_competition))
        low_count = min(5, len(hashtag_set.low_competition))
        
        hashtag_set.recommended_mix = (
            (random.sample(hashtag_set.high_competition, high_count) if high_count > 0 else []) +
            (random.sample(hashtag_set.medium_competition, medium_count) if medium_count > 0 else []) +
            (random.sample(hashtag_set.low_competition, low_count) if low_count > 0 else []) +
            hashtag_set.branded[:2]
        )[:self.RECOMMENDED_HASHTAGS]"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(r'C:\Users\karma\PROJECTS\ACTIVE\youtube_enhancement_tools\social_media\instagram.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed Instagram hashtag optimization')
else:
    print('Could not find the code to replace')
    # Try to find similar code
    if 'random.sample(hashtag_set.high_competition, 3)' in content:
        print('Found similar pattern - trying alternate fix')
