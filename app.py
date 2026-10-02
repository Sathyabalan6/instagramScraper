"""
IG Design-Skill Extractor — Web Dashboard & Control Studio
FastAPI application providing a complete modern UI to:
- Run extraction on Instagram handles or saved collections
- Stream live pipeline execution logs and progress
- Explore global and creator-specific UI/UX design principles
- Inspect posts, captions, and audio transcripts
- Manage session cookies and API keys
"""

import os
import sys
import re
import json
import uuid
import queue
import logging
import asyncio
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure project root in sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except Exception:
    pass

from scripts.fetch_posts import load_cookies_as_dict, extract_browser_cookies

app = FastAPI(title="IG Design-Skill Studio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active pipeline tasks
# { task_id: { "process": Popen, "status": "running"|"completed"|"failed", "target": str, "logs": [...], "exit_code": int } }
_ACTIVE_TASKS = {}
_TASK_QUEUES: Dict[str, List[queue.Queue]] = {}


def get_cookie_status() -> dict:
    """Check availability and key health of Instagram cookies."""
    cookies_dict = load_cookies_as_dict("cookies/instagram_cookies.txt")
    has_sessionid = "sessionid" in cookies_dict
    has_user_id = "ds_user_id" in cookies_dict
    has_csrftoken = "csrftoken" in cookies_dict
    has_mid = "mid" in cookies_dict

    valid = bool(has_sessionid and has_user_id)
    source_name = "Cached File (cookies/instagram_cookies.txt)"
    if not valid:
        # Try dynamic extraction
        b_cookies, b_source = extract_browser_cookies()
        if b_cookies and "sessionid" in b_cookies:
            cookies_dict = b_cookies
            has_sessionid = True
            has_user_id = "ds_user_id" in cookies_dict
            has_csrftoken = "csrftoken" in cookies_dict
            has_mid = "mid" in cookies_dict
            valid = True
            source_name = f"Browser Auto-Pull: {b_source}"
    elif Path("cookies/instagram_cookies.txt").exists():
        source_name = "Local Session (cookies/instagram_cookies.txt)"

    return {
        "loaded": len(cookies_dict) > 0,
        "valid": valid,
        "source": source_name if valid else None,
        "cookie_count": len(cookies_dict),
        "keys": {
            "sessionid": has_sessionid,
            "ds_user_id": has_user_id,
            "csrftoken": has_csrftoken,
            "mid": has_mid
        }
    }


def get_llm_status() -> dict:
    """Check configuration of LLM provider API keys."""
    return {
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "gemini": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")),
        "groq": bool(os.environ.get("GROQ_API_KEY")),
    }


@app.post("/api/settings/keys")
async def save_api_keys(request: Request):
    """Save LLM API keys to .env and active process environment."""
    data = await request.json()
    env_file = _ROOT / ".env"

    existing_lines = []
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

    env_dict = {}
    for line in existing_lines:
        line_s = line.strip()
        if "=" in line_s and not line_s.startswith("#"):
            k, v = line_s.split("=", 1)
            env_dict[k.strip()] = v.strip().strip("'\"")

    allowed_keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY", "GOOGLE_API_KEY"]
    for k in allowed_keys:
        if k in data and data[k]:
            clean_val = str(data[k]).strip()
            env_dict[k] = clean_val
            os.environ[k] = clean_val

    with open(env_file, "w", encoding="utf-8") as f:
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")

    return {"status": "ok", "llm": get_llm_status()}


def get_available_targets() -> list:
    """List all extracted skills in skills/ and targets in output/."""
    from scripts.merge_skill import get_clean_skill_name
    skills_dir = _ROOT / "skills"
    out_dir = _ROOT / "output"
    targets = set()
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith(".") and (item / "SKILL.md").exists():
                targets.add(item.name)
    if out_dir.exists():
        for item in out_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                targets.add(get_clean_skill_name(item.name))
    return sorted(list(targets))


@app.get("/api/status")
async def api_status():
    """System health check and credentials diagnostics."""
    from scripts.fetch_posts import InstagramCollectionPipeline
    try:
        saved_cols = InstagramCollectionPipeline.list_local_saved_collections()
    except Exception:
        saved_cols = []

    targets = get_available_targets()
    return {
        "cookies": get_cookie_status(),
        "llm": get_llm_status(),
        "targets": targets,
        "saved_collections": saved_cols,
        "total_skills": len(targets)
    }


@app.get("/api/saved-collections")
async def api_saved_collections():
    """Returns all saved collections discovered from local browser history."""
    from scripts.fetch_posts import InstagramCollectionPipeline
    try:
        cols = InstagramCollectionPipeline.list_local_saved_collections()
        return {"status": "ok", "collections": cols}
    except Exception as e:
        return {"status": "error", "message": str(e), "collections": []}


@app.post("/api/cookies")
async def save_cookies(request: Request):
    """Save cookies (Netscape, JSON string, or parsed JSON payload) to cookies/instagram_cookies.txt."""
    try:
        data = await request.json()
    except Exception:
        body_bytes = await request.body()
        data = {"cookies": body_bytes.decode("utf-8", errors="replace")}

    raw_content = data.get("cookies", "")
    if isinstance(raw_content, (dict, list)):
        raw_content = json.dumps(raw_content, indent=2)
    elif isinstance(raw_content, str):
        raw_content = raw_content.strip()

    if not raw_content and ("sessionid" in data or "items" in data or "cookies" in data):
        raw_content = json.dumps(data, indent=2)

    if not raw_content:
        raise HTTPException(status_code=400, detail="Empty cookie content provided")

    cookies_dir = _ROOT / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)
    cookie_path = cookies_dir / "instagram_cookies.txt"

    with open(cookie_path, "w", encoding="utf-8") as f:
        f.write(raw_content + "\n")

    status = get_cookie_status()
    return {"status": "saved", "path": str(cookie_path), "diagnostics": status}



@app.get("/api/principles")
async def get_principles(target: Optional[str] = None, category: Optional[str] = None, q: Optional[str] = None):
    """Fetch principles from target skill folder in skills/<target>/."""
    from scripts.merge_skill import get_clean_skill_name
    
    if not target or target == "global":
        available = get_available_targets()
        target = available[0] if available else "checkups"

    clean_target = get_clean_skill_name(target)
    candidate_paths = [
        _ROOT / "skills" / clean_target / "principles.json",
        _ROOT / "skills" / target / "principles.json",
        _ROOT / "output" / target / "principles.json",
        _ROOT / "output" / f"collection_{target}" / "principles.json",
    ]
    store_path = None
    for p in candidate_paths:
        if p.exists():
            store_path = p
            break

    if not store_path:
        return {"principles": [], "target": clean_target, "total": 0}

    with open(store_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data
    if category and category.lower() != "all":
        results = [p for p in results if p.get("category", "").lower() == category.lower()]

    if q:
        query = q.lower().strip()
        results = [
            p for p in results
            if query in p.get("principle", "").lower()
            or query in p.get("rule", "").lower()
            or query in p.get("why", "").lower()
            or query in p.get("example", "").lower()
            or any(query in str(s.get("handle", "")).lower() for s in p.get("sources", []))
        ]

    return {"principles": results, "target": clean_target, "total": len(results)}


@app.get("/api/skill_md")
async def get_skill_md(target: Optional[str] = None):
    """Fetch deliverable SKILL.md content from skills/<target>/."""
    from scripts.merge_skill import get_clean_skill_name
    if not target or target == "global":
        available = get_available_targets()
        target = available[0] if available else "checkups"

    clean_target = get_clean_skill_name(target)
    candidate_paths = [
        _ROOT / "skills" / clean_target / "SKILL.md",
        _ROOT / "skills" / target / "SKILL.md",
        _ROOT / "output" / target / "SKILL.md",
        _ROOT / "output" / f"collection_{target}" / "SKILL.md",
    ]
    skill_path = None
    for p in candidate_paths:
        if p.exists():
            skill_path = p
            break

    if not skill_path:
        return PlainTextResponse(f"# No SKILL.md found for '{clean_target}'\nRun extraction first to generate this deliverable.")

    with open(skill_path, "r", encoding="utf-8") as f:
        return PlainTextResponse(f.read())


@app.get("/api/posts")
async def get_posts(target: str):
    """Fetch raw post metadata and transcripts for a given target."""
    from scripts.merge_skill import get_clean_skill_name
    clean_target = get_clean_skill_name(target)

    candidate_paths = [
        _ROOT / "output" / target / "posts.json",
        _ROOT / "output" / f"collection_{target}" / "posts.json",
        _ROOT / "output" / clean_target / "posts.json",
        _ROOT / "data/raw" / target / "posts.json",
        _ROOT / "data/raw" / f"collection_{target}" / "posts.json",
    ]
    posts_file = None
    for p in candidate_paths:
        if p.exists():
            posts_file = p
            break

    if not posts_file:
        return {"posts": [], "target": target, "total": 0}

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    return {"posts": posts, "target": target, "total": len(posts)}


def _log_reader_worker(task_id: str, proc: subprocess.Popen):
    """Read subprocess stdout line by line and broadcast to task queues."""
    for line in iter(proc.stdout.readline, ""):
        if not line:
            break
        clean_line = line.rstrip()
        if task_id in _ACTIVE_TASKS:
            _ACTIVE_TASKS[task_id]["logs"].append(clean_line)

        # Broadcast to listeners
        queues = _TASK_QUEUES.get(task_id, [])
        for q in queues:
            q.put(clean_line)

    proc.stdout.close()
    proc.wait()

    if task_id in _ACTIVE_TASKS:
        _ACTIVE_TASKS[task_id]["exit_code"] = proc.returncode
        _ACTIVE_TASKS[task_id]["status"] = "completed" if proc.returncode == 0 else "failed"

    # Send EOF marker to all queues
    queues = _TASK_QUEUES.get(task_id, [])
    for q in queues:
        q.put(None)


@app.post("/api/run")
async def start_pipeline_run(request: Request):
    """Trigger a new pipeline execution."""
    data = await request.json()
    mode = data.get("mode", "handle")  # 'handle' or 'collection'
    target_input = data.get("target", "").strip()
    limit = int(data.get("limit", 20))
    skip_transcribe = bool(data.get("skip_transcribe", False))

    if not target_input:
        raise HTTPException(status_code=400, detail="Target handle or collection URL is required")

    task_id = str(uuid.uuid4())[:8]

    # Build command line
    cmd = [sys.executable, "-u", str(_ROOT / "scripts/run_pipeline.py"), "--limit", str(limit)]
    if mode == "collection":
        cmd.extend(["--collection", target_input])
    else:
        # Strip leading @ if user entered it
        clean_handle = target_input.lstrip("@").strip()
        cmd.extend(["--handle", clean_handle])

    if skip_transcribe:
        cmd.append("--skip-transcribe")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(_ROOT),
            env=os.environ.copy()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {e}")

    _ACTIVE_TASKS[task_id] = {
        "task_id": task_id,
        "mode": mode,
        "target": target_input,
        "status": "running",
        "logs": [],
        "exit_code": None
    }
    _TASK_QUEUES[task_id] = []

    # Start reader thread
    t = threading.Thread(target=_log_reader_worker, args=(task_id, proc), daemon=True)
    t.start()

    return {"task_id": task_id, "status": "started", "target": target_input}


@app.get("/api/run/stream/{task_id}")
async def stream_task_logs(task_id: str):
    """Server-Sent Events (SSE) endpoint to stream live console output."""
    if task_id not in _ACTIVE_TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    client_q = queue.Queue()
    _TASK_QUEUES[task_id].append(client_q)

    # First replay any existing buffered logs
    for line in _ACTIVE_TASKS[task_id]["logs"]:
        client_q.put(line)

    async def event_generator():
        try:
            while True:
                # Run queue get in executor to avoid blocking event loop
                loop = asyncio.get_event_loop()
                line = await loop.run_in_executor(None, client_q.get)
                if line is None:
                    # Task ended
                    status = _ACTIVE_TASKS.get(task_id, {}).get("status", "completed")
                    yield f"event: end\ndata: {json.dumps({'status': status})}\n\n"
                    break
                yield f"data: {json.dumps({'line': line})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if task_id in _TASK_QUEUES and client_q in _TASK_QUEUES[task_id]:
                _TASK_QUEUES[task_id].remove(client_q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/run/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of an extraction run."""
    task = _ACTIVE_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": task["status"],
        "target": task["target"],
        "log_count": len(task["logs"]),
        "exit_code": task["exit_code"],
        "latest_logs": task["logs"][-15:]
    }


_TEMPLATE_PATH = _ROOT / "templates" / "index.html"


def get_dashboard_html() -> str:
    """Load dashboard HTML template from disk."""
    if _TEMPLATE_PATH.exists():
        with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Design Skill Studio</h1><p>Template missing at templates/index.html</p>"


# Embed Single-Page Application Dashboard (Vue 3 + Tailwind CSS + Apple HIG Design)
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=get_dashboard_html())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting IG Design-Skill Studio Dashboard on http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
