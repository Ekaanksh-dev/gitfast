import os
from gitshorts.utils.colors import Printer

GITSHORTS_DIR = os.path.expanduser("~/.gitshorts")
INIT_FILE_FISH = os.path.join(GITSHORTS_DIR, "init.fish")
SOURCE_LINE   = 'source ~/.gitshorts/init.fish'


FISH_SHORTCUTS = '''
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# gitfast shortcuts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# TIER 1 — daily
function gs; git status -s; end
function gpl; git pull origin (git branch --show-current); end
function gc
    set msg (string join " " $argv)
    if test -z "$msg"
        echo "[ERROR] Usage: gc <message>"
        return 1
    end
    echo "[..] Staging..."
    git add .
    echo "[..] Committing..."
    git commit -m "$msg"
    echo "[OK] Committed locally — run gcp to push"
end
function gcp
    set msg (string join " " $argv)
    if test -z "$msg"
        echo "[ERROR] Usage: gcp <message>"
        return 1
    end

    # Check 1 — is git repo?
    if not git rev-parse --is-inside-work-tree > /dev/null 2>&1
        echo "[ERROR] Not a git repo"
        return 1
    end

    # Check 2 — is remote configured?
    if test -z (git remote 2>/dev/null)
        echo "[ERROR] No remote configured"
        echo "[INFO]  Add one: git remote add origin <url>"
        return 1
    end

    # Check 3 — check for conflicts
    set conflicts (git diff --name-only --diff-filter=U 2>/dev/null)
    if test -n "$conflicts"
        echo "[ERROR] Conflicts found — resolve first"
        echo "[INFO]  Run: gmerge"
        return 1
    end

    # Check 4 — is remote ahead?
    git fetch origin (git branch --show-current) > /dev/null 2>&1
    set behind (git rev-list HEAD..origin/(git branch --show-current) --count 2>/dev/null)
    if test -n "$behind" -a "$behind" -gt 0
        echo "[WARN] Remote is $behind commit(s) ahead — pulling first..."
        git pull origin (git branch --show-current)
        if test $status -ne 0
            echo "[ERROR] Pull failed — fix conflicts then try again"
            return 1
        end
    end

    # Check 5 — large files warning
    set large (find . -size +100M -not -path "./.git/*" 2>/dev/null)
    if test -n "$large"
        echo "[WARN] Large files detected (>100MB):"
        for f in $large
            echo "       $f"
        end
        echo "[WARN] GitHub will reject files over 100MB"
        read --prompt "[..] Continue anyway? (y/N): " confirm
        if test "$confirm" != "y"
            echo "[INFO] Cancelled"
            return 1
        end
    end

    # Check 6 — is branch tracked?
    set tracked (git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
    if test -z "$tracked"
        echo "[WARN] Branch not tracked — setting upstream..."
        git push -u origin (git branch --show-current)
        if test $status -ne 0
            echo "[ERROR] Failed to set upstream"
            return 1
        end
        echo "[OK] Upstream set"
    end

    # All clear — add + commit + push
    echo "[..] Staging..."
    git add .
    echo "[..] Committing..."
    git commit -m "$msg"
    if test $status -ne 0
        echo "[ERROR] Nothing to commit"
        return 1
    end
    echo "[..] Pushing..."
    git push origin (git branch --show-current)
    if test $status -ne 0
        echo "[WARN] Push failed — trying auto fix..."
        git pull origin (git branch --show-current)
        set conflicts (git diff --name-only --diff-filter=U 2>/dev/null)
        if test -n "$conflicts"
            echo "[WARN] Conflicts after pull — running gmerge..."
            gitshorts merge
            if test $status -ne 0
                echo "[ERROR] Auto merge failed — fix manually"
                return 1
            end
            git push origin (git branch --show-current)
            if test $status -ne 0
                echo "[ERROR] Push still failing"
                return 1
            end
        else
            git push origin (git branch --show-current)
            if test $status -ne 0
                echo "[ERROR] Push failed — check remote"
                return 1
            end
        end
    end
    echo "[OK] Done!"
end

# TIER 2 — weekly
function gb;   git branch -a; end
function gsw;  git switch $argv[1]; end
function gm;   git merge $argv[1]; end
function gd;   git diff --stat; end
function gdf;  git diff $argv[1]; end
function gcl;  git clone $argv[1]; end
function gl;   git log --oneline --graph --decorate --color -20; end
function gll;  git log --stat --color -10; end
function gnb
    if test -z "$argv[1]"
        echo "[ERROR] Usage: gnb <name>"
        return 1
    end
    git checkout -b $argv[1]
    git push -u origin $argv[1]
    echo "[OK] Created: $argv[1]"
end

# TIER 3 — rescue
function gundo;   git reset --soft HEAD~1; echo "[OK] Undone"; end
function gundo2;  git reset HEAD~1; echo "[OK] Undone"; end
function gsave;   git stash push -m (test -n "$argv[1]"; and echo $argv[1]; or echo "wip"); end
function gpop;    git stash pop; echo "[OK] Popped"; end
function gstashes; git stash list; end
function gdrop;   git stash drop "stash@{$argv[1]}"; end
function gabort;  git merge --abort 2>/dev/null; or git rebase --abort 2>/dev/null; end
function gsquash; git rebase -i "HEAD~$argv[1]"; end
function gnuke
    echo "[WARN] This will destroy ALL uncommitted changes!"
    read --prompt "Type YES to confirm: " c
    if test "$c" = "YES"
        git reset --hard HEAD
        git clean -fd
        echo "[OK] Wiped"
    else
        echo "Cancelled"
    end
end

# TIER 4 — power
function gf;       git fetch --all --prune; end
function gtag;     git tag -a $argv[1] -m $argv[2]; and git push origin $argv[1]; end
function gtags;    git tag -l --sort=-version:refname; end
function gwho;     git blame $argv[1]; end
function greflog;  git reflog --color | head -30; end
function gshow;    git show (test -n "$argv[1]"; and echo $argv[1]; or echo "HEAD") --stat; end
function gclean;   git branch --merged | grep -v "main\\|master" | xargs git branch -d; end
function gremotes; git remote -v; end

# TOKEN
function gtoken
    gitfast token $argv[1]
end

# AUTH
function gtest_ssh
    echo "[SCAN] Testing SSH connections..."
    echo ""

    set gh (ssh -T git@github.com 2>&1)
    if echo $gh | grep -q "Hi"
        echo "[OK] GitHub connected"
    else
        echo "[SKIP] GitHub not configured"
    end

    set gl (ssh -T git@gitlab.com 2>&1)
    if echo $gl | grep -q "Welcome"
        echo "[OK] GitLab connected"
    else
        echo "[SKIP] GitLab not configured"
    end

    set bb (ssh -T git@bitbucket.org 2>&1)
    if echo $bb | grep -q "logged in"
        echo "[OK] Bitbucket connected"
    else
        echo "[SKIP] Bitbucket not configured"
    end

    echo ""
    echo "[INFO] Run gsetup to configure any platform"
end

function gsetup
    gitfast setup
end

# MERGE
function gconflicts; git diff --name-only --diff-filter=U; end

# HELP
function ghelp
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
end

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# end gitfast
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''

def install(config_path):
    framework = _detect_framework(config_path)
    if framework:
        Printer.info(f"Detected: {framework} — using safe install")

    os.makedirs(GITSHORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    try:
        with open(INIT_FILE_FISH, "w") as f:
            f.write(FISH_SHORTCUTS)
        Printer.success(f"Shortcuts written to {INIT_FILE_FISH}")
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

        if os.path.exists(INIT_FILE_FISH):
            os.remove(INIT_FILE_FISH)

        Printer.success(f"Removed from {config_path}")
        return True

    except Exception as e:
        Printer.error(f"Failed: {e}")
        return False


def _detect_framework(config_path):
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, "r") as f:
            content = f.read()
        if "oh-my-fish" in content:  return "oh-my-fish"
        if "fisher"     in content:  return "fisher"
        if "fundle"     in content:  return "fundle"
    except Exception:
        pass
    return None
