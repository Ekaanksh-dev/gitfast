import os
from gitshorts.utils.colors import Printer

GITSHORTS_DIR  = os.path.expanduser("~/.gitshorts")
INIT_FILE_PS   = os.path.join(GITSHORTS_DIR, "init.ps1")
SOURCE_LINE    = '. ~/.gitshorts/init.ps1'


POWERSHELL_SHORTCUTS = '''
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# gitfast shortcuts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# helper
function Get-Branch { git branch --show-current 2>$null }

# TIER 1 — daily
function gs    { git status -s }
function gpl   { git pull origin (Get-Branch) }
function gc {
    param([string]$msg)
    if (-not $msg) { Write-Host "[ERROR] Usage: gc <message>"; return }
    Write-Host "[..] Staging..."
    git add .
    Write-Host "[..] Committing..."
    git commit -m $msg
    Write-Host "[OK] Committed locally — run gcp to push"
}
function gcp {
    $msg = $args -join " "
    if (-not $msg) { Write-Host "[ERROR] Usage: gcp <message>"; return }

    # Check 1 — git repo?
    $repo = git rev-parse --is-inside-work-tree 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] Not a git repo"; return }

    # Check 2 — remote configured?
    $remote = git remote 2>&1
    if (-not $remote) {
        Write-Host "[ERROR] No remote configured"
        Write-Host "[INFO]  Add one: git remote add origin <url>"
        return
    }

    # Check 3 — conflicts?
    $conflicts = git diff --name-only --diff-filter=U 2>&1
    if ($conflicts) {
        Write-Host "[ERROR] Conflicts found — resolve first"
        Write-Host "[INFO]  Run: gmerge"
        return
    }

    # Check 4 — remote ahead?
    $branch = git branch --show-current
    git fetch origin $branch 2>&1 | Out-Null
    $behind = git rev-list "HEAD..origin/$branch" --count 2>&1
    if ($behind -gt 0) {
        Write-Host "[WARN] Remote is $behind commit(s) ahead — pulling first..."
        git pull origin $branch
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Pull failed — fix conflicts then try again"
            return
        }
    }

    # Check 5 — branch tracked?
    $tracked = git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Branch not tracked — setting upstream..."
        git push -u origin $branch
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to set upstream"
            return
        }
        Write-Host "[OK] Upstream set"
    }

    # All clear — add + commit + push
    Write-Host "[..] Staging..."
    git add .
    Write-Host "[..] Committing..."
    git commit -m $msg
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] Nothing to commit"; return }
    Write-Host "[..] Pushing to $branch..."
    git push origin $branch
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Push failed — trying auto fix..."
        git pull origin $branch
        $conflicts = git diff --name-only --diff-filter=U 2>$null
        if ($conflicts) {
            Write-Host "[WARN] Conflicts after pull — running gmerge..."
            gitshorts merge
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ERROR] Auto merge failed — fix manually"
                return
            }
            git push origin $branch
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ERROR] Push still failing"
                return
            }
        } else {
            git push origin $branch
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ERROR] Push failed — check remote"
                return
            }
        }
    }
    Write-Host "[OK] Done!"
}

# TIER 2 — weekly
function gb    { git branch -a }
function gsw   { param($b) git switch $b }
function gm    { param($b) git merge $b }
function gd    { git diff --stat }
function gdf   { param($f) git diff $f }
function gcl   { param($u) git clone $u }
function gl    { git log --oneline --graph --decorate --color -20 }
function gll   { git log --stat --color -10 }
function gnb {
    param([string]$name)
    if (-not $name) { Write-Host "[ERROR] Usage: gnb <name>"; return }
    git checkout -b $name
    git push -u origin $name
    Write-Host "[OK] Created: $name"
}

# TIER 3 — rescue
function gundo   { git reset --soft HEAD~1; Write-Host "[OK] Undone" }
function gundo2  { git reset HEAD~1; Write-Host "[OK] Undone" }
function gsave   { param($l="wip") git stash push -m $l; Write-Host "[OK] Stashed" }
function gpop    { git stash pop; Write-Host "[OK] Popped" }
function gstashes{ git stash list }
function gdrop   { param($i=0) git stash drop "stash@{$i}" }
function gabort  { git merge --abort 2>$null; if($?) {} else { git rebase --abort } }
function gsquash { param($n) git rebase -i "HEAD~$n" }
function gnuke {
    Write-Host "[WARN] This will destroy ALL uncommitted changes!"
    $c = Read-Host "Type YES to confirm"
    if ($c -eq "YES") {
        git reset --hard HEAD
        git clean -fd
        Write-Host "[OK] Wiped"
    } else {
        Write-Host "Cancelled"
    }
}

# TIER 4 — power
function gf      { git fetch --all --prune }
function gtag    { param($t,$m="Release $t") git tag -a $t -m $m; git push origin $t }
function gtags   { git tag -l --sort=-version:refname }
function gwho    { param($f) git blame $f }
function greflog { git reflog --color | Select-Object -First 30 }
function gshow   { param($h="HEAD") git show $h --stat }
function gclean  { git branch --merged | Where-Object { $_ -notmatch "main|master" } | ForEach-Object { git branch -d $_.Trim() } }
function gremotes{ git remote -v }

#TOKEN
function gtoken { gitfast token $args[0] }

# AUTH
function gtest_ssh {
    Write-Host "[SCAN] Testing SSH connections..."
    Write-Host ""

    $gh = ssh -T git@github.com 2>&1
    if ($gh -match "Hi") { Write-Host "[OK] GitHub connected" }
    else { Write-Host "[SKIP] GitHub not configured" }

    $gl = ssh -T git@gitlab.com 2>&1
    if ($gl -match "Welcome") { Write-Host "[OK] GitLab connected" }
    else { Write-Host "[SKIP] GitLab not configured" }

    $bb = ssh -T git@bitbucket.org 2>&1
    if ($bb -match "logged in") { Write-Host "[OK] Bitbucket connected" }
    else { Write-Host "[SKIP] Bitbucket not configured" }

    Write-Host ""
    Write-Host "[INFO] Run gsetup to configure any platform"
}

#SETUP
function gsetup { gitfast setup }


# MERGE
function gconflicts { git diff --name-only --diff-filter=U }

# HELP
function ghelp {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "  gitfast shortcuts"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "  TIER 1 — Daily"
    Write-Host "  gs            show what changed"
    Write-Host "  gc  'msg'     add + commit only"
    Write-Host "  gcp 'msg'     add + commit + push"
    Write-Host "  gpl           pull latest changes"
    Write-Host ""
    Write-Host "  TIER 2 — Weekly"
    Write-Host "  gb            list all branches"
    Write-Host "  gnb 'name'    new branch + push"
    Write-Host "  gsw 'name'    switch branch"
    Write-Host "  gm  'name'    merge branch"
    Write-Host "  gl            pretty log last 20"
    Write-Host "  gll           log with file stats"
    Write-Host "  gd            diff summary"
    Write-Host "  gdf 'file'    diff one file"
    Write-Host "  gcl 'url'     clone repo"
    Write-Host ""
    Write-Host "  TIER 3 — Rescue"
    Write-Host "  gundo         undo last commit keep staged"
    Write-Host "  gundo2        undo last commit unstage"
    Write-Host "  gsave 'l'     stash with label"
    Write-Host "  gpop          pop latest stash"
    Write-Host "  gstashes      list all stashes"
    Write-Host "  gdrop N       drop stash N"
    Write-Host "  gsquash N     squash last N commits"
    Write-Host "  gabort        abort merge or rebase"
    Write-Host "  gnuke         wipe all uncommitted changes"
    Write-Host ""
    Write-Host "  TIER 4 — Power"
    Write-Host "  gf            fetch all remotes"
    Write-Host "  gtag 'v'      tag + push release"
    Write-Host "  gtags         list all tags"
    Write-Host "  gwho 'file'   who wrote each line"
    Write-Host "  greflog       full history + deleted"
    Write-Host "  gshow 'hash'  inspect a commit"
    Write-Host "  gclean        delete merged branches"
    Write-Host "  gremotes      show all remotes"
    Write-Host ""
    Write-Host "  AUTH"  
    Write-Host "  gtest_ssh     test SSH connections"
    Write-Host "  gsetup        setup platform + auth"
    Write-Host ""
    Write-Host "  TOKEN"
    Write-Host "  gtoken setup    store token securely"
    Write-Host "  gtoken test     verify token works"
    Write-Host "  gtoken test     verify token works"
    Write-Host "  gtoken revoke   remove token"
    Write-Host "  gtoken info     show token status"
    Write-Host ""
    Write-Host "  MERGE"
    Write-Host "  gconflicts      list all conflicts"
    Write-Host "  gmerge          auto resolve conflicts"
    Write-Host "  gmerge -i       interactive resolver"
    Write-Host "  gmerge --ours   keep our changes"
    Write-Host "  gmerge --theirs keep their changes"
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# end gitfast
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''

def install(config_path):
    os.makedirs(GITSHORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    try:
        with open(INIT_FILE_PS, "w") as f:
            f.write(POWERSHELL_SHORTCUTS)
        Printer.success(f"Shortcuts written to {INIT_FILE_PS}")
    except Exception as e:
        Printer.error(f"Failed: {e}")
        return False

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            if SOURCE_LINE in f.read():
                Printer.warning("gitshorts already in config — skipping")
                return True

    try:
        with open(config_path, "a") as f:
            f.write(f"\n# gitshorts\n{SOURCE_LINE}\n")
        Printer.success(f"Added source line to {config_path}")
        return True
    except Exception as e:
        Printer.error(f"Failed: {e}")
        return False


def uninstall(config_path):
    if not os.path.exists(config_path):
        return True

    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        cleaned = [
            l for l in lines
            if "gitshorts" not in l
            and SOURCE_LINE not in l
        ]

        with open(config_path, "w") as f:
            f.writelines(cleaned)

        if os.path.exists(INIT_FILE_PS):
            os.remove(INIT_FILE_PS)

        Printer.success(f"Removed from {config_path}")
        return True

    except Exception as e:
        Printer.error(f"Failed: {e}")
        return False
