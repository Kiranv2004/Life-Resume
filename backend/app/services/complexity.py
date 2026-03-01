from typing import List
import lizard

from app.github_ingestion.client import GitHubClient


def compute_commit_complexity(client: GitHubClient, full_name: str, sha: str, files: List[dict]) -> float:
    complexities = []
    for file_info in files:
        filename = file_info.get("filename", "")
        if not filename:
            continue
        content = client.get_file_content(full_name, filename, sha)
        if not content:
            continue
        try:
            analysis = lizard.analyze_file.analyze_source_code(filename, content)
            for func in analysis.function_list:
                complexities.append(func.cyclomatic_complexity)
        except Exception:
            continue
    if not complexities:
        return 0.0
    return sum(complexities) / len(complexities)
