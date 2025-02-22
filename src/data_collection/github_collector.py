from github import Github

class GitHubTrendCollector:
    def collect_tech_trends(self):
        """Collect trending repositories and technologies"""
        # No API key needed for basic access
        trending = self.get_trending_repos()
        technologies = self.extract_technologies(trending)
        return technologies 