# GitHub Repository Manager

A comprehensive tool for downloading, updating, and managing GitHub repositories with support for both public and private repositories.

## Features

- **Download repositories** from any GitHub user
- **Update existing repositories** to the latest version
- **Support for private repositories** using GitHub tokens
- **Configurable delays** between downloads to respect API limits
- **Search functionality** to find repositories by criteria
- **Filter options** to include/exclude repositories based on stars, language, etc.
- **Batch operations** for processing multiple repositories
- **Preserve existing repositories** or force updates

## Configuration

The tool uses a configuration file (`github_config.json`) with the following options:

- `github_token`: Your GitHub personal access token for private repositories and higher API limits
- `base_directory`: Where to store downloaded repositories
- `delay_between_downloads`: Time to wait between downloads (in seconds)
- `max_retries`: Number of retries for failed operations
- `timeout`: Timeout for HTTP requests (in seconds)
- `clone_depth`: Depth for shallow clones (1 for latest commit only)
- `preserve_existing`: Whether to skip existing repositories
- `include_private`: Whether to include private repositories
- `include_public`: Whether to include public repositories
- `repo_filters`: Filters for repository selection:
  - `min_stars`: Minimum number of stars required
  - `languages`: List of allowed programming languages
  - `exclude_forks`: Whether to exclude forked repositories

## Usage

### Command Line Interface

```bash
python GITHUB_REPO_MANAGER.py [action] [options]
```

Actions:
- `download`: Download repositories
- `update`: Update existing repositories
- `search`: Search for repositories
- `list`: List current configuration

Options:
- `--username, -u`: GitHub username to download from
- `--repo-list, -l`: File containing list of repository URLs
- `--search, -s`: Search query for repositories
- `--force-update, -f`: Force update existing repositories
- `--config, -c`: Configuration file path
- `--output, -o`: Output file for search results

### Examples

1. Download all repositories from a user:
   ```bash
   python GITHUB_REPO_MANAGER.py download --username octocat
   ```

2. Update all existing repositories:
   ```bash
   python GITHUB_REPO_MANAGER.py update
   ```

3. Download repositories from a list of URLs:
   ```bash
   python GITHUB_REPO_MANAGER.py download --repo-list my_repos.txt
   ```

4. Search for Python repositories with at least 100 stars:
   ```bash
   python GITHUB_REPO_MANAGER.py search --search "language:python stars:>100"
   ```

### Interactive Mode

Run the `RUN_GITHUB_MANAGER.bat` file to use the interactive menu system.

## Authentication

For private repositories or to increase API rate limits, you'll need to provide a GitHub personal access token. The tool will prompt you for the token if it's not already configured, and it will be saved to the configuration file.

To create a personal access token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select the scopes you need (typically "repo" for private repositories)
4. Copy the generated token

## Repository Filtering

You can filter repositories based on:
- Minimum number of stars
- Programming language
- Whether to include forked repositories

These filters are configured in the `repo_filters` section of the configuration file.

## Delay Configuration

The tool includes configurable delays between downloads to respect GitHub's API limits and avoid overwhelming the network. The default delay is 5 seconds, but this can be adjusted in the configuration file.

## Batch Operations

The tool supports batch operations for processing multiple repositories at once:
- Download all repositories from a user
- Update all existing repositories
- Process repositories from a list of URLs

## Troubleshooting

- If you get API rate limit errors, ensure you're using a GitHub token
- For private repositories, make sure your token has the appropriate scopes
- If downloads fail, check your network connection and retry
- For authentication issues, regenerate your token and update the configuration

## Security

- GitHub tokens are stored in plain text in the configuration file
- Ensure the configuration file is protected from unauthorized access
- Use tokens with minimal required permissions
- Regenerate tokens periodically for security