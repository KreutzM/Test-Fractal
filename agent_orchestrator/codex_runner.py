from __future__ import annotations

import json
import time
from pathlib import Path
from string import Template
from .run_log import estimate_tokens, utc_now
from .shell import CommandResult, run_command


PROMPT_DIR = Path("prompts/roles")


def load_template(role: str) -> Template:
    path = PROMPT_DIR / f"{role}.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing role prompt: {path}")
    return Template(path.read_text(encoding="utf-8"))


def render_prompt(role: str, variables: dict[str, str]) -> str:
    template = load_template(role)
    return template.safe_substitute(variables)


def _metrics_path(output_path: Path | None) -> Path | None:
    if output_path is None:
        return None
    return output_path.with_suffix(output_path.suffix + ".metrics.json")


def _write_role_metrics(
    *,
    output_path: Path | None,
    role: str,
    model: str,
    sandbox: str,
    dry_run: bool,
    started_at: str,
    duration_ms: int,
    prompt: str,
    result: CommandResult,
    output_text: str,
) -> None:
    path = _metrics_path(output_path)
    if path is None:
        return
    payload = {
        "role": role,
        "model": model,
        "sandbox": sandbox,
        "dry_run": dry_run,
        "started_at": started_at,
        "duration_ms": duration_ms,
        "returncode": result.returncode,
        "ok": result.ok,
        "output_path": str(output_path),
        "prompt_chars": len(prompt),
        "prompt_tokens_estimate": estimate_tokens(prompt),
        "output_chars": len(output_text),
        "output_tokens_estimate": estimate_tokens(output_text),
        "stdout_chars": len(result.stdout),
        "stderr_chars": len(result.stderr),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_codex_role(
    *,
    role: str,
    variables: dict[str, str],
    model: str,
    sandbox: str,
    approval: str,
    cwd: Path | str = ".",
    output_path: Path | None = None,
    extra_args: list[str] | None = None,
    dry_run: bool = False,
) -> CommandResult:
    prompt = render_prompt(role, variables)
    started_at = utc_now()
    started = time.perf_counter()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        fake = f"DRY RUN: would run Codex role {role} with model {model}\n\nPrompt preview:\n{prompt[:2000]}\n"
        if output_path is not None:
            output_path.write_text(fake, encoding="utf-8")
        result = CommandResult(["codex", "exec", "-"], 0, fake, "")
        _write_role_metrics(
            output_path=output_path,
            role=role,
            model=model,
            sandbox=sandbox,
            dry_run=True,
            started_at=started_at,
            duration_ms=int((time.perf_counter() - started) * 1000),
            prompt=prompt,
            result=result,
            output_text=fake,
        )
        return result

    args = [
        "codex",
        "exec",
        "--cd",
        str(Path(cwd).resolve()),
        "--model",
        model,
        "--sandbox",
        sandbox,
        "--color",
        "never",
    ]
    if output_path is not None:
        args.extend(["--output-last-message", str(output_path)])
    if extra_args:
        args.extend(extra_args)
    args.append("-")
    result = run_command(args, cwd=cwd, input_text=prompt, check=False)
    output_text = output_path.read_text(encoding="utf-8") if output_path and output_path.exists() else result.stdout
    _write_role_metrics(
        output_path=output_path,
        role=role,
        model=model,
        sandbox=sandbox,
        dry_run=False,
        started_at=started_at,
        duration_ms=int((time.perf_counter() - started) * 1000),
        prompt=prompt,
        result=result,
        output_text=output_text,
    )
    return result
