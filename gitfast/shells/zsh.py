import os
from gitfast.utils.colors import Printer


ZSH_SHORTCUTS = '''
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# gitfast shortcuts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# helper
_gf_branch() { git branch --show-current 2>/dev/null }
_gf_repo()   { git rev-parse --is-inside-work-tree &>/dev/null }

# TIER 1 — daily
gs()  { _gf_repo && git status -s }
gpl() { _gf_repo && git pull origin $(_gf_branch) }
gc()  {
    param([string]$msg)
    if (-not $msg) { Write-Host "[ERROR] Usage: gc <message>"; return }
    Write-Host "[..] Staging..."
    git add .
    Write-Host "[..] Committing..."
    git commit -m $msg
    Write-Host "[OK] Committed locally — run gcp to push"
}
gcp() {
    _gf_repo || return
    local msg="${*}"
    [[ -z "$msg" ]] && echo "[ERROR] Usage: gcp <message>" && return 1

    # Check 1 — remote configured?
    if [[ -z $(git remote 2>/dev/null) ]]; then
        echo "[ERROR] No remote configured"
        echo "[INFO]  Add one: git remote add origin <url>"
        return 1
    fi

    # Check 2 — conflicts?
    if [[ -n $(git diff --name-only --diff-filter=U 2>/dev/null) ]]; then
        echo "[ERROR] Conflicts found — resolve first"
        echo "[INFO]  Run: gmerge"
        return 1
    fi

    # Check 3 — remote ahead?
    local branch=$(_gf_branch)
    git fetch origin "$branch" > /dev/null 2>&1
    local behind=$(git rev-list HEAD..origin/"$branch" --count 2>/dev/null)
    if [[ -n "$behind" && "$behind" -gt 0 ]]; then
        echo "[WARN] Remote is $behind commit(s) ahead — pulling first..."
        git pull origin "$branch" || { echo "[ERROR] Pull failed"; return 1; }
    fi

    # Check 4 — large files?
    local large=$(find . -size +100M -not -path "./.git/*" 2>/dev/null)
    if [[ -n "$large" ]]; then
        echo "[WARN] Large files detected (>100MB):"
        echo "$large"
        read "confirm?[..] Continue anyway? (y/N): "
        [[ "$confirm" != "y" ]] && echo "[INFO] Cancelled" && return 1
    fi

    # Check 5 — branch tracked?
    if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        echo "[WARN] Branch not tracked — setting upstream..."
        git push -u origin "$branch" || { echo "[ERROR] Failed"; return 1; }
        echo "[OK] Upstream set"
    fi

    # All clear
    echo "[..] Staging..."
    git add .
    echo "[..] Committing..."
    git commit -m "$msg" || { echo "[ERROR] Nothing to commit"; return 1; }
    echo "[..] Pushing to $branch..."
    git push origin "$branch" || {
        echo "[WARN] Push failed — trying auto fix..."
        git pull origin "$branch" && git push origin "$branch"
    }
    echo "[OK] Done!"
}

# TIER 2 — weekly
gb()  { _gf_repo && git branch -a }
gsw() { _gf_repo && git switch "$1" }
gm()  { _gf_repo && git merge "$1" }
gd()  { _gf_repo && git diff --stat }
gdf() { _gf_repo && git diff "$1" }
gcl() { git clone "$1" }
gl()  { _gf_repo && git log --oneline --graph --decorate --color -20 }
gll() { _gf_repo && git log --stat --color -10 }
gnb() {
    _gf_repo || return
    [[ -z "$1" ]] && echo "[ERROR] Usage: gnb <name>" && return 1
    git checkout -b "$1"
    git push -u origin "$1"
    echo "[OK] Created: $1"
}

# TIER 3 — rescue
gundo()   { _gf_repo && git reset --soft HEAD~1 && echo "[OK] Undone" }
gundo2()  { _gf_repo && git reset HEAD~1 && echo "[OK] Undone" }
gsave()   { _gf_repo && git stash push -m "${1:-wip}" && echo "[OK] Stashed" }
gpop()    { _gf_repo && git stash pop && echo "[OK] Popped" }
gstashes(){ _gf_repo && git stash list }
gdrop()   { _gf_repo && git stash drop "stash@{${1:-0}}" }
gabort()  { git merge --abort 2>/dev/null || git rebase --abort 2>/dev/null }
gsquash() { _gf_repo && git rebase -i "HEAD~$1" }
gnuke()   {
    _gf_repo || return
    echo "[WARN] This will destroy ALL uncommitted changes!"
    read "c?Type YES to confirm: "
    [[ "$c" != "YES" ]] && echo "Cancelled" && return
    git reset --hard HEAD && git clean -fd
    echo "[OK] Wiped"
}

# TIER 4 — power
gf()      { _gf_repo && git fetch --all --prune }
gtag()    { _gf_repo && git tag -a "$1" -m "${2:-Release $1}" && git push origin "$1" }
gtags()   { _gf_repo && git tag -l --sort=-version:refname }
gwho()    { _gf_repo && git blame "$1" }
greflog() { _gf_repo && git reflog --color | head -30 }
gshow()   { _gf_repo && git show "${1:-HEAD}" --stat }
gclean()  { _gf_repo && git branch --merged | grep -v "\\*\\|main\\|master" | xargs git branch -d }
gremotes(){ _gf_repo && git remote -v }

#TOKEN
gtoken() { gitfast token "$1" }

# AUTH
gtest_ssh() {
    echo "[SCAN] Testing SSH connections..."
    echo ""

    gh=$(ssh -T git@github.com 2>&1)
    if echo "$gh" | grep -q "Hi"; then
        echo "[OK] GitHub connected"
    else
        echo "[SKIP] GitHub not configured"
    fi

    gl=$(ssh -T git@gitlab.com 2>&1)
    if echo "$gl" | grep -q "Welcome"; then
        echo "[OK] GitLab connected"
    else
        echo "[SKIP] GitLab not configured"
    fi

    bb=$(ssh -T git@bitbucket.org 2>&1)
    if echo "$bb" | grep -q "logged in"; then
        echo "[OK] Bitbucket connected"
    else
        echo "[SKIP] Bitbucket not configured"
    fi

    echo ""
    echo "[INFO] Run gsetup to configure any platform"
}

#SETUP
gsetup()  { gitfast setup }

# MERGE
gconflicts() { _gf_repo && git diff --name-only --diff-filter=U }

# HELP
ghelp() {
        echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  gitfast shortcuts"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  TIER 1 — Daily"
    echo "  gs            show what changed"
    echo "  gc  'msg'     add + commit only"
    echo "  gcp 'msg'     add + commit + push"
    echo "  gpl           pull latest changes"
    echo ""
    echo "  TIER 2 — Weekly"
    echo "  gb            list all branches"
    echo "  gnb 'name'    new branch + push"
    echo "  gsw 'name'    switch branch"
    echo "  gm  'name'    merge branch"
    echo "  gl            pretty log last 20"
    echo "  gll           log with file stats"
    echo "  gd            diff summary"
    echo "  gdf 'file'    diff one file"
    echo "  gcl 'url'     clone repo"
    echo ""
    echo "  TIER 3 — Rescue"
    echo "  gundo         undo last commit keep staged"
    echo "  gundo2        undo last commit unstage"
    echo "  gsave 'l'     stash with label"
    echo "  gpop          pop latest stash"
    echo "  gstashes      list all stashes"
    echo "  gdrop N       drop stash N"
    echo "  gsquash N     squash last N commits"
    echo "  gabort        abort merge or rebase"
    echo "  gnuke         wipe all uncommitted changes"
    echo ""
    echo "  TIER 4 — Power"
    echo "  gf            fetch all remotes"
    echo "  gtag 'v'      tag + push release"
    echo "  gtags         list all tags"
    echo "  gwho 'file'   who wrote each line"
    echo "  greflog       full history + deleted"
    echo "  gshow 'hash'  inspect a commit"
    echo "  gclean        delete merged branches"
    echo "  gremotes      show all remotes"
    echo ""
    echo "  AUTH"
    echo "  gtest_ssh     test SSH connections"
    echo "  gsetup        setup platform + auth"
    echo ""
    echo "  TOKEN"
    echo "  gtoken setup    store token securely"
    echo "  gtoken test     verify token works"
    echo "  gtoken refresh  update expired token"
    echo "  gtoken revoke   remove token"
    echo "  gtoken info     show token status"
    echo ""
    echo "  MERGE"
    echo "  gconflicts      list all conflicts"
    echo "  gmerge          auto resolve conflicts"
    echo "  gmerge -i       interactive resolver"
    echo "  gmerge --ours   keep our changes"
    echo "  gmerge --theirs keep their changes"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# end gitfast
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''


def install(config_path):
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            if "gitfast shortcuts" in f.read():
                Printer.warning("gitfast already in zshrc — skipping")
                return True

    try:
        with open(config_path, "a") as f:
            f.write(ZSH_SHORTCUTS)
        Printer.success(f"Shortcuts added to {config_path}")
        return True
    except Exception as e:
        Printer.error(f"Failed to write to {config_path}: {e}")
        return False


def uninstall(config_path):
    if not os.path.exists(config_path):
        return True

    try:
        with open(config_path, "r") as f:
            content = f.read()

        start = content.find("# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n# gitfast shortcuts")
        end   = content.find("# end gitfast\n# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if start == -1 or end == -1:
            Printer.warning("gitfast block not found in zshrc")
            return False

        cleaned = content[:start] + content[end + len("# end gitfast\n# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"):]

        with open(config_path, "w") as f:
            f.write(cleaned)

        Printer.success("Removed from zshrc")
        return True

    except Exception as e:
        Printer.error(f"Failed: {e}")
        return False
