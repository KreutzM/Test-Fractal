param(
    [Parameter(Mandatory=$true)]
    [int]$Issue,

    [string]$Config = "config/orchestrator.json",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$argsList = @("-m", "agent_orchestrator", "run", "--issue", "$Issue", "--config", $Config)
if ($DryRun) {
    $argsList += "--dry-run"
}

python @argsList
exit $LASTEXITCODE
