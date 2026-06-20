from __future__ import annotations

from pathlib import Path
from string import Template
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
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        fake = f"DRY RUN: would run Codex role {role} with model {model}\n\nPrompt preview:\n{prompt[:2000]}\n"
        if output_path is not None:
            output_path.write_text(fake, encoding="utf-8")
        return CommandResult(["codex", "exec", "-"], 0, fake, "")

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
    return run_command(args, cwd=cwd, input_text=prompt, check=False)
