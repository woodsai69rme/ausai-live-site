#!/usr/bin/env python3
"""
GitHub Repository Sync & Organizer
Scans X:/githubrepo for existing repos, checks for updates, and organizes them
"""
import os
import sys
import subprocess
import json
import asyncio
import aiohttp
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepoSyncOrganizer:
    """Organizes and syncs existing GitHub repositories"""
    
    def __init__(self, repo_base_path: str = "X:/githubrepo"):
        self.repo_base_path = Path(repo_base_path)
        self.temp_base_path = Path("X:/githubrepo_temp")
        
        # Configuration
        self.max_concurrent_checks = 3
        self.timeout = 60
        
        # Statistics
        self.stats = {
            'total_repos': 0,
            'repos_with_updates': 0,
            'repos_up_to_date': 0,
            'repos_failed': 0,
            'repos_cloned': 0,
            'space_used_mb': 0,
            'space_freed_mb': 0,
            'errors': [],
            'warnings': []
        }
        
        # GitHub token for API calls
        self.github_token = None
        self.session = None
        
        # Repo info cache
        self.repo_cache = {}
    
    def set_github_token(self, token: str):
        """Set GitHub API token"""
        self.github_token = token
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API"""
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        return headers
    
    def scan_repositories(self) -> List[Dict]:
        """Scan base directory for existing repositories"""
        if not self.repo_base_path.exists():
            logger.error(f"Repository directory not found: {self.repo_base_path}")
            return []
        
        repositories = []
        
        logger.info(f"Scanning {self.repo_base_path} for repositories...")
        
        for item in self.repo_base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                # This is a git repository
                repo_info = self._get_local_repo_info(item)
                if repo_info:
                    repositories.append(repo_info)
                else:
                    self.stats['warnings'].append(f"Could not get info for {item.name}")
            elif item.is_dir():
                # Check if it contains git repos
                for subitem in item.iterdir():
                    if subitem.is_dir() and (subitem / ".git").exists():
                        repo_info = self._get_local_repo_info(subitem)
                        if repo_info:
                            repositories.append(repo_info)
        
        self.stats['total_repos'] = len(repositories)
        logger.info(f"Found {len(repositories)} git repositories")
        
        return repositories
    
    def _get_local_repo_info(self, repo_path: Path) -> Optional[Dict]:
        """Get information about a local repository"""
        try:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Try 'upstream' or other remotes
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'upstream'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode != 0:
                # Try to get any remote
                result = subprocess.run(
                    ['git', 'remote'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    remotes = result.stdout.strip().split('\n')
                    if remotes:
                        result = subprocess.run(
                            ['git', 'remote', 'get-url', remotes[0]],
                            cwd=repo_path,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
            
            remote_url = result.stdout.strip() if result.returncode == 0 else None
            
            # Get current commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_commit = result.stdout.strip() if result.returncode == 0 else None
            
            # Get branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_branch = result.stdout.strip() if result.returncode == 0 else None
            
            # Calculate size
            try:
                total_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
            except:
                size_mb = 0
            
            # Parse GitHub info from remote URL
            github_info = self._parse_github_url(remote_url)
            
            return {
                'name': repo_path.name,
                'path': str(repo_path),
                'remote_url': remote_url,
                'current_commit': current_commit,
                'current_branch': current_branch,
                'size_mb': round(size_mb, 2),
                'github': github_info,
                'last_modified': datetime.fromtimestamp(repo_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting repo info for {repo_path}: {e}")
            self.stats['errors'].append(f"Info error {repo_path.name}: {e}")
            return None
    
    def _parse_github_url(self, remote_url: str) -> Optional[Dict]:
        """Parse GitHub repository information from remote URL"""
        if not remote_url:
            return None
        
        # Handle different URL formats
        if remote_url.startswith('git@github.com:'):
            # SSH format: git@github.com:user/repo.git
            path = remote_url.replace('git@github.com:', '').replace('.git', '')
            parts = path.split('/')
            if len(parts) == 2:
                return {'owner': parts[0], 'repo': parts[1], 'full_name': path}
        
        elif remote_url.startswith('https://github.com/'):
            # HTTPS format: https://github.com/user/repo.git or https://github.com/user/repo
            path = remote_url.replace('https://github.com/', '').replace('.git', '')
            parts = path.split('/')
            if len(parts) == 2:
                return {'owner': parts[0], 'repo': parts[1], 'full_name': path}
        
        return None
    
    async def check_for_updates(self, repo_info: Dict) -> Dict:
        """Check if repository has updates on GitHub"""
        github_info = repo_info.get('github')
        if not github_info:
            return {'status': 'no_github', 'repo': repo_info['name']}
        
        full_name = github_info['full_name']
        
        try:
            # Get latest commit from GitHub
            url = f'https://api.github.com/repos/{full_name}/commits/main'
            if repo_info['current_branch'] and repo_info['current_branch'] != 'main':
                url = f'https://api.github.com/repos/{full_name}/commits/{repo_info["current_branch"]}'
            
            async with self.session.get(url, headers=self.get_headers(), timeout=self.timeout) as response:
                if response.status == 200:
                    commit_data = await response.json()
                    latest_commit = commit_data['sha']
                    
                    if repo_info['current_commit'] == latest_commit:
                        return {'status': 'up_to_date', 'repo': full_name, 'path': repo_info['path']}
                    else:
                        return {
                            'status': 'has_updates',
                            'repo': full_name,
                            'path': repo_info['path'],
                            'current_commit': repo_info['current_commit'],
                            'latest_commit': latest_commit
                        }
                
                elif response.status == 404:
                    return {'status': 'repo_not_found', 'repo': full_name}
                
                elif response.status == 403:
                    return {'status': 'rate_limited', 'repo': full_name}
                
                else:
                    return {'status': 'api_error', 'repo': full_name, 'error': f"Status {response.status}"}
        
        except Exception as e:
            return {'status': 'error', 'repo': full_name, 'error': str(e)}
    
    async def sync_repository(self, repo_info: Dict) -> Dict:
        """Pull updates for a repository"""
        repo_path = Path(repo_info['path'])
        
        logger.info(f"Syncing {repo_info['name']}...")
        
        try:
            # Fetch updates
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                return {'status': 'fetch_failed', 'error': result.stderr.strip()}
            
            # Check if updates are available
            result = subprocess.run(
                ['git', 'status', '-uno'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'Your branch is ahead' in result.stdout:
                # Merge updates
                merge_result = subprocess.run(
                    ['git', 'pull', '--rebase'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                if merge_result.returncode == 0:
                    logger.info(f"Successfully updated {repo_info['name']}")
                    return {'status': 'updated', 'repo': repo_info['name']}
                else:
                    return {'status': 'merge_failed', 'error': merge_result.stderr.strip()}
            
            else:
                return {'status': 'no_changes', 'repo': repo_info['name']}
        
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'repo': repo_info['name']}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def clone_if_missing(self, github_info: Dict) -> Dict:
        """Clone repository if it doesn't exist locally"""
        if not github_info:
            return {'status': 'no_github_info'}
        
        full_name = github_info['full_name']
        clone_url = f"https://github.com/{full_name}.git"
        
        # Determine target directory
        target_dir = self.repo_base_path / f"{github_info['repo']}_{github_info['owner']}"
        
        # Check if already exists
        if target_dir.exists() and (target_dir / ".git").exists():
            return {'status': 'exists', 'path': str(target_dir)}
        
        # Clone
        logger.info(f"Cloning {full_name}...")
        
        try:
            result = subprocess.run(
                ['git', 'clone', clone_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=self.timeout * 2
            )
            
            if result.returncode == 0:
                # Calculate size
                try:
                    total_size = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    self.stats['space_used_mb'] += size_mb
                except:
                    size_mb = 0
                
                logger.info(f"Successfully cloned {full_name}")
                return {'status': 'cloned', 'path': str(target_dir), 'size_mb': size_mb}
            else:
                return {'status': 'clone_failed', 'error': result.stderr.strip()}
        
        except subprocess.TimeoutExpired:
            return {'status': 'timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def check_all_repositories(self, repositories: List[Dict]) -> List[Dict]:
        """Check multiple repositories for updates"""
        semaphore = asyncio.Semaphore(self.max_concurrent_checks)
        
        async def check_with_semaphore(repo_info):
            async with semaphore:
                return await self.check_for_updates(repo_info)
        
        tasks = [check_with_semaphore(repo) for repo in repositories]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def sync_all_repositories(self, repositories: List[Dict]) -> List[Dict]:
        """Sync multiple repositories"""
        semaphore = asyncio.Semaphore(self.max_concurrent_checks)
        
        async def sync_with_semaphore(repo_info):
            async with semaphore:
                return await self.sync_repository(repo_info)
        
        tasks = [sync_with_semaphore(repo) for repo in repositories]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def generate_organized_report(self, repositories: List[Dict], update_results: List[Dict] = None) -> str:
        """Generate organized report of repositories"""
        report = []
        report.append("=" * 80)
        report.append("REPOSITORY ORGANIZATION REPORT")
        report.append("=" * 80)
        
        # Group by owner
        by_owner = {}
        for repo in repositories:
            github = repo.get('github', {})
            owner = github.get('owner', 'Unknown')
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(repo)
        
        for owner, repos in sorted(by_owner.items()):
            report.append(f"\n{owner} ({len(repos)} repos):")
            for repo in sorted(repos, key=lambda x: x['name']):
                size_info = f"{repo['size_mb']} MB" if repo['size_mb'] > 0 else "Unknown size"
                github_info = repo.get('github', {})
                if github_info:
                    full_name = github_info['full_name']
                    report.append(f"  - {repo['name']:<40} [{size_info:>10}] | {full_name}")
                else:
                    report.append(f"  - {repo['name']:<40} [{size_info:>10}] | No GitHub info")
        
        if update_results:
            report.append("\n" + "=" * 40)
            report.append("UPDATE SUMMARY")
            report.append("=" * 40)
            
            up_to_date = sum(1 for r in update_results if r.get('status') == 'up_to_date')
            has_updates = sum(1 for r in update_results if r.get('status') == 'has_updates')
            failed = sum(1 for r in update_results if r.get('status') in ['error', 'api_error', 'rate_limited'])
            
            report.append(f"Up to date: {up_to_date}")
            report.append(f"Has updates: {has_updates}")
            report.append(f"Failed checks: {failed}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)
    
    def find_duplicate_repos(self) -> List[Dict]:
        """Find duplicate repositories (same repo in different folders)"""
        repos = self.scan_repositories()
        
        # Group by full_name
        by_full_name = {}
        for repo in repos:
            github = repo.get('github', {})
            if github:
                full_name = github['full_name']
                if full_name not in by_full_name:
                    by_full_name[full_name] = []
                by_full_name[full_name].append(repo)
        
        duplicates = []
        for full_name, repo_list in by_full_name.items():
            if len(repo_list) > 1:
                duplicates.append({
                    'full_name': full_name,
                    'instances': repo_list,
                    'count': len(repo_list)
                })
        
        return duplicates
    
    def cleanup_duplicate_repos(self, dry_run: bool = True) -> Dict[str, any]:
        """Remove duplicate repositories, keeping the one with latest commit"""
        duplicates = self.find_duplicate_repos()
        
        if not duplicates:
            return {'message': 'No duplicates found', 'cleaned': 0}
        
        results = {
            'duplicates_found': len(duplicates),
            'cleaned': 0,
            'errors': []
        }
        
        for dup in duplicates:
            instances = dup['instances']
            
            # Get latest commit for each instance
            latest_instance = None
            latest_time = 0
            
            for instance in instances:
                try:
                    result = subprocess.run(
                        ['git', 'log', '-1', '--format=%at'],
                        cwd=instance['path'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        commit_time = int(result.stdout.strip())
                        if commit_time > latest_time:
                            latest_time = commit_time
                            latest_instance = instance
                except:
                    pass
            
            if not latest_instance:
                # Fallback to most recently modified
                latest_instance = max(instances, key=lambda x: Path(x['path']).stat().st_mtime)
            
            # Remove all but latest
            for instance in instances:
                if instance == latest_instance:
                    continue
                
                if dry_run:
                    results['cleaned'] += 1
                    logger.info(f"[DRY RUN] Would remove: {instance['path']}")
                else:
                    try:
                        shutil.rmtree(instance['path'])
                        results['cleaned'] += 1
                        logger.info(f"Removed duplicate: {instance['path']}")
                    except Exception as e:
                        results['errors'].append(f"Failed to remove {instance['path']}: {e}")
        
        return results
    
    def get_total_size(self) -> float:
        """Calculate total size of all repositories"""
        if not self.repo_base_path.exists():
            return 0
        
        total_size = 0
        for repo_path in self.repo_base_path.rglob('.git'):
            if repo_path.is_dir():
                parent = repo_path.parent
                try:
                    for file_path in parent.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                except:
                    pass
        
        return total_size / (1024 * 1024)  # MB
    
    def export_inventory(self, output_file: str = "repo_inventory.json") -> Dict:
        """Export repository inventory to JSON file"""
        repos = self.scan_repositories()
        
        inventory = {
            'export_date': datetime.now().isoformat(),
            'base_path': str(self.repo_base_path),
            'total_repos': len(repos),
            'total_size_mb': self.get_total_size(),
            'repositories': repos
        }
        
        with open(output_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        logger.info(f"Inventory exported to {output_file}")
        return inventory

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Repository Sync & Organizer")
    parser.add_argument('--base-path', default='X:/githubrepo', help='Base repository directory')
    parser.add_argument('--token', help='GitHub API token')
    parser.add_argument('--scan-only', action='store_true', help='Only scan, don\'t sync')
    parser.add_argument('--check-updates', action='store_true', help='Check for updates')
    parser.add_argument('--sync', action='store_true', help='Sync repositories')
    parser.add_argument('--find-duplicates', action='store_true', help='Find duplicate repos')
    parser.add_argument('--cleanup-duplicates', action='store_true', help='Remove duplicates')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--export', help='Export inventory to JSON file')
    parser.add_argument('--clone-missing', help='Clone missing repos from user/org')
    
    args = parser.parse_args()
    
    organizer = RepoSyncOrganizer(args.base_path)
    
    if args.token:
        organizer.set_github_token(args.token)
        print(f"Using GitHub token: {args.token[:4]}...{args.token[-4:]}")
    
    print(f"Repository base path: {args.base_path}")
    
    # Scan repositories
    print("\n" + "=" * 60)
    print("SCANNING REPOSITORIES")
    print("=" * 60)
    
    repos = organizer.scan_repositories()
    
    if not repos:
        print("No repositories found")
        return
    
    # Show summary
    total_size = organizer.get_total_size()
    print(f"Found {len(repos)} repositories, total size: {total_size:.1f} MB")
    
    # Export inventory
    if args.export:
        organizer.export_inventory(args.export)
    
    # Find duplicates
    if args.find_duplicates or args.cleanup_duplicates:
        print("\n" + "=" * 60)
        print("CHECKING FOR DUPLICATES")
        print("=" * 60)
        
        duplicates = organizer.find_duplicate_repos()
        if duplicates:
            print(f"Found {len(duplicates)} duplicate repository groups:")
            for dup in duplicates:
                print(f"\n{dup['full_name']} ({dup['count']} instances):")
                for instance in dup['instances']:
                    print(f"  - {instance['path']} [{instance['size_mb']} MB]")
            
            if args.cleanup_duplicates:
                results = organizer.cleanup_duplicate_repos(dry_run=args.dry_run)
                print(f"\nCleanup results: {results}")
        else:
            print("No duplicates found")
    
    # Check for updates
    if args.check_updates and organizer.github_token:
        print("\n" + "=" * 60)
        print("CHECKING FOR UPDATES")
        print("=" * 60)
        
        # Check first 20 repos to avoid rate limits
        check_repos = repos[:20] if len(repos) > 20 else repos
        
        async with aiohttp.ClientSession() as session:
            organizer.session = session
            update_results = await organizer.check_all_repositories(check_repos)
            
            up_to_date = sum(1 for r in update_results if r.get('status') == 'up_to_date')
            has_updates = sum(1 for r in update_results if r.get('status') == 'has_updates')
            failed = sum(1 for r in update_results if 'error' in r.get('status', ''))
            
            print(f"\nResults (first {len(check_repos)} repos):")
            print(f"  Up to date: {up_to_date}")
            print(f"  Has updates: {has_updates}")
            print(f"  Failed checks: {failed}")
            
            if has_updates > 0:
                print(f"\nRepos with updates:")
                for result in update_results:
                    if result.get('status') == 'has_updates':
                        print(f"  - {result['repo']}")
    
    # Sync repositories
    if args.sync and organizer.github_token:
        print("\n" + "=" * 60)
        print("SYNCING REPOSITORIES")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            organizer.session = session
            
            # Check for updates first
            update_results = await organizer.check_all_repositories(repos)
            
            repos_to_sync = []
            for i, result in enumerate(update_results):
                if result.get('status') == 'has_updates':
                    repos_to_sync.append(repos[i])
            
            if repos_to_sync:
                print(f"Syncing {len(repos_to_sync)} repositories...")
                sync_results = await organizer.sync_all_repositories(repos_to_sync)
                
                successful = sum(1 for r in sync_results if r.get('status') == 'updated')
                failed = sum(1 for r in sync_results if r.get('status') in ['merge_failed', 'timeout', 'error'])
                
                print(f"\nSync results:")
                print(f"  Successful: {successful}")
                print(f"  Failed: {failed}")
            else:
                print("No repositories need syncing")
    
    # Clone missing repos
    if args.clone_missing and organizer.github_token:
        print("\n" + "=" * 60)
        print("CLONING MISSING REPOSITORIES")
        print("=" * 60)
        
        if args.clone_missing.lower() in ['user', 'org', 'starred']:
            async with aiohttp.ClientSession() as session:
                organizer.session = session
                
                # Get repositories from GitHub
                if args.clone_missing == 'user':
                    print("Please specify username with --clone-missing username")
                elif args.clone_missing == 'org':
                    print("Please specify org name with --clone-missing orgname")
                elif args.clone_missing == 'starred':
                    # Get starred repos
                    url = 'https://api.github.com/user/starred'
                    async with session.get(url, headers=organizer.get_headers()) as response:
                        if response.status == 200:
                            starred_repos = await response.json()
                            print(f"Found {len(starred_repos)} starred repos")
                            
                            for repo in starred_repos:
                                result = await organizer.clone_if_missing({
                                    'owner': repo['owner']['login'],
                                    'repo': repo['name'],
                                    'full_name': repo['full_name']
                                })
                                print(f"  {repo['full_name']}: {result['status']}")
                        else:
                            print(f"Error fetching starred repos: {response.status}")
        
        else:
            # Assume it's a username or org
            async with aiohttp.ClientSession() as session:
                organizer.session = session
                
                # Try user repos
                url = f'https://api.github.com/users/{args.clone_missing}/repos'
                async with session.get(url, headers=organizer.get_headers()) as response:
                    if response.status == 200:
                        user_repos = await response.json()
                        print(f"Found {len(user_repos)} repos for user {args.clone_missing}")
                        
                        for repo in user_repos:
                            result = await organizer.clone_if_missing({
                                'owner': repo['owner']['login'],
                                'repo': repo['name'],
                                'full_name': repo['full_name']
                            })
                            print(f"  {repo['full_name']}: {result['status']}")
                    else:
                        print(f"No user repos found or error: {response.status}")
    
    # Generate organization report
    if not args.scan_only and not args.check_updates and not args.sync and not args.find_duplicates and not args.cleanup_duplicates and not args.clone_missing:
        print("\n" + "=" * 60)
        print("ORGANIZATION REPORT")
        print("=" * 60)
        
        report = organizer.generate_organized_report(repos)
        print(report)
    
    # Show summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total repositories: {len(repos)}")
    print(f"Total size: {total_size:.1f} MB")
    print(f"Base path: {args.base_path}")
    
    if args.dry_run:
        print("\nDRY RUN MODE - No changes were made")

if __name__ == "__main__":
    asyncio.run(main())