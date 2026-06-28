import re

# Read the file
with open(r'C:\Users\karma\PROJECTS\ACTIVE\youtube_enhancement_tools\tests\unit\test_social_media_phase5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic test
old_test = '''    @pytest.mark.unit
    @pytest.mark.social
    def test_rate_limit_increment(self):
        """Test rate limit counter increment."""
        manager = PlatformManager()
        manager.add_platform("tiktok")

        initial = manager.check_rate_limit("tiktok")
        manager._increment_rate_limit("tiktok")
        after = manager.check_rate_limit("tiktok")

        assert after.posts_this_hour == initial.posts_this_hour + 1'''

new_test = '''    @pytest.mark.unit
    @pytest.mark.social
    def test_rate_limit_increment(self):
        """Test rate limit counter increment."""
        manager = PlatformManager()
        manager.add_platform("tiktok")

        # Capture initial value before increment (check_rate_limit returns same object reference)
        initial_count = manager.check_rate_limit("tiktok").posts_this_hour
        manager._increment_rate_limit("tiktok")
        after = manager.check_rate_limit("tiktok")

        assert after.posts_this_hour == initial_count + 1'''

if old_test in content:
    content = content.replace(old_test, new_test)
    with open(r'C:\Users\karma\PROJECTS\ACTIVE\youtube_enhancement_tools\tests\unit\test_social_media_phase5.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed rate limit increment test')
else:
    print('Could not find the test to replace')
