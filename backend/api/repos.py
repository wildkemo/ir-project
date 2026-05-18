from fastapi import APIRouter, HTTPException

from backend.core.engine_loader import load_engine


router = APIRouter(prefix="/repos", tags=["Repositories"])


@router.get("/")
def list_repositories(limit: int = 20):
    try:
        engine = load_engine()

        limit = max(1, min(limit, 100))

        return {
            "count": min(limit, len(engine.repos)),
            "results": engine.repos[:limit],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/options")
def get_filter_options():
    try:
        engine = load_engine()

        languages = set()
        licenses = set()
        topics = set()

        for repo in engine.repos:
            if repo.get("language"):
                languages.add(repo["language"])

            if repo.get("license"):
                licenses.add(repo["license"])

            for topic in repo.get("topics", []) or []:
                topics.add(topic)

        return {
            "languages": sorted(languages),
            "licenses": sorted(licenses),
            "topics": sorted(topics),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/details/{repo_identifier:path}")
def get_repository(repo_identifier: str):
    try:
        engine = load_engine()

        idx = engine.find_repo_index(repo_identifier)

        if idx is None:
            raise HTTPException(status_code=404, detail="Repository not found")

        return engine.repos[idx]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))