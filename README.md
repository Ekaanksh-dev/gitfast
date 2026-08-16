# gitblaze

42 git shortcuts + auto merge conflict resolver — zero AI, pure Python

```bash
pip install gitblaze
gitblaze install
ghelp
```

---

## Why gitfast?

Before gitfast — 3 commands every commit:
```bash
git add .
git commit -m "fix login bug"
git push origin main
```

After gitfast — 1 command:
```bash
gcp "fix login bug"
```

---

## Install

```bash
# install
pip install gitblaze

# setup
gitblaze install

# reload your shell
source ~/.bashrc          # bash
source ~/.zshrc           # zsh
source ~/.config/fish/config.fish   # fish

# verify
ghelp
```

---

## All Commands

### TIER 1 — Daily

| Command | Does | Replaces |
|---------|------|---------|
| `gs` | git status short | `git status` |
| `gc "msg"` | add + commit | `git add . && git commit -m` |
| `gcp "msg"` | add + commit + push | 3 separate commands |
| `gpl` | pull current branch | `git pull origin <branch>` |

### TIER 2 — Weekly

| Command | Does | Replaces |
|---------|------|---------|
| `gb` | list all branches | `git branch -a` |
| `gnb "name"` | new branch + push upstream | 2 commands |
| `gsw "branch"` | switch branch | `git switch` |
| `gm "branch"` | merge branch | `git merge` |
| `gl` | pretty log last 20 | `git log --oneline --graph` |
| `gll` | log with file stats | `git log --stat` |
| `gd` | diff summary | `git diff --stat` |
| `gdf "file"` | diff one file | `git diff <file>` |
| `gcl "url"` | clone repo | `git clone` |

### TIER 3 — Rescue

| Command | Does | Replaces |
|---------|------|---------|
| `gundo` | undo last commit keep staged | `git reset --soft HEAD~1` |
| `gundo2` | undo last commit unstage | `git reset HEAD~1` |
| `gsave "label"` | stash with label | `git stash push -m` |
| `gpop` | pop latest stash | `git stash pop` |
| `gstashes` | list all stashes | `git stash list` |
| `gdrop N` | drop stash N | `git stash drop stash@{N}` |
| `gsquash N` | squash last N commits | `git rebase -i HEAD~N` |
| `gabort` | abort merge or rebase | `git merge --abort` |
| `gnuke` | wipe all uncommitted changes | `git reset --hard HEAD` |

### TIER 4 — Power

| Command | Does | Replaces |
|---------|------|---------|
| `gf` | fetch all remotes | `git fetch --all --prune` |
| `gtag v1.0` | tag + push release | 2 commands |
| `gtags` | list all tags | `git tag -l` |
| `gwho "file"` | blame file | `git blame` |
| `greflog` | full history + deleted | `git reflog` |
| `gshow "hash"` | inspect commit | `git show --stat` |
| `gclean` | delete merged branches | complex command |
| `gremotes` | show all remotes | `git remote -v` |

### AUTH

| Command | Does |
|---------|------|
| `gtest_ssh` | test SSH to GitHub/GitLab/Bitbucket |
| `gsetup_ssh` | full SSH key setup in one command |
| `gsetup_creds` | configure OS credential helper |
| `ghttps_to_ssh` | convert HTTPS remote to SSH |
| `gauth_info` | show full auth status |

### TOKEN

| Command | Does |
|---------|------|
| `gtoken setup` | store GitHub PAT securely |
| `gtoken test` | verify token works |
| `gtoken refresh` | update expired token |
| `gtoken revoke` | remove stored token |
| `gtoken info` | show token status + expiry |

### MERGE — The Killer Feature

| Command | Does |
|---------|------|
| `gconflicts` | scan + list all conflicts |
| `gmerge` | auto resolve all conflicts |
| `gmerge -i` | interactive — pick ours/theirs per conflict |
| `gmerge --ours` | always keep our changes |
| `gmerge --theirs` | always keep their changes |
| `gmerge --dry-run` | show conflicts without resolving |

---

## Auto Push Error Fix

gitfast automatically fixes the most common push error:

error: failed to push some refs
hint: Updates were rejected because the remote
hint: contains work that you do not have locally


When this happens gitfast:
detects the error automatically
pulls remote changes
merges with your changes
resolves conflicts if any
pushes again

You never see this error with gitfast.

---

## Token Security

gitfast stores your GitHub token in OS secure storage:

| OS | Storage |
|----|---------|
| macOS | Keychain |
| Linux | GNOME Keyring |
| Windows | Credential Manager |
| Any OS | ~/.netrc (chmod 600) |

Token is never stored in plain text. Never in .bashrc. Never logged.

---

## Shell Support

| Shell | Support |
|-------|---------|
| Bash | full |
| Zsh | full |
| Fish | full |
| PowerShell | full |

---

## OS Support

| OS | Support |
|----|---------|
| Ubuntu / Debian | full |
| Arch / Manjaro | full |
| Fedora / RHEL | full |
| macOS | full |
| WSL2 | full |
| Git Bash | full |
| Any OS | netrc fallback |

---

## Uninstall

```bash
gitblaze uninstall
pip uninstall gitblaze
```

---

## Update

```bash
gitblaze update
```

---

## License

MIT — see LICENSE file

---

## Author

Built for developers who live in the terminal.
# gitblaze — 42 git shortcuts
