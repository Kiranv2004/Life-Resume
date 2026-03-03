from typing import List

# Complexity is estimated purely from the diff data already present in the commit
# detail response — no extra API calls needed.

_CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
              ".c", ".cpp", ".cs", ".rb", ".rs", ".php", ".swift", ".kt"}


def compute_commit_complexity(client, full_name: str, sha: str, files: List[dict]) -> float:
    """Estimate complexity from patch size without any extra API calls."""
    scores = []
    for f in files:
        filename = f.get("filename", "")
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in _CODE_EXTS:
            continue
        changes = f.get("changes", 0) or 0
        patch = f.get("patch", "") or ""
        # Count control-flow keywords in the patch as a complexity proxy
        keywords = sum(patch.count(kw) for kw in
                       ("if ", "elif ", "else:", "for ", "while ", "catch",
                        "switch", "case ", "&&", "||", "?"))
        score = min(10.0, (keywords * 0.5) + (changes * 0.01))
        scores.append(score)
    return round(sum(scores) / len(scores), 4) if scores else 0.0
