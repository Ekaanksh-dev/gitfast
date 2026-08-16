import re


# conflict marker constants
OURS_START   = "<<<<<<< "
SEPARATOR    = "======="
THEIRS_END   = ">>>>>>> "


class Conflict:
    def __init__(self, ours, theirs, branch, start_line, end_line):
        self.ours       = ours        # our code
        self.theirs     = theirs      # their code
        self.branch     = branch      # their branch name
        self.start_line = start_line  # line where conflict starts
        self.end_line   = end_line    # line where conflict ends

    def __repr__(self):
        return (
            f"Conflict(\n"
            f"  start={self.start_line}\n"
            f"  end={self.end_line}\n"
            f"  ours={self.ours[:50]}...\n"
            f"  theirs={self.theirs[:50]}...\n"
            f")"
        )


def parse_conflicts(filepath):
    """
    Parse all conflicts in a file
    Returns list of Conflict objects
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        # try latin-1 for older files
        with open(filepath, "r", encoding="latin-1") as f:
            lines = f.readlines()

    conflicts = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # found start of conflict
        if line.startswith(OURS_START):
            start_line = i
            branch     = line[len(OURS_START):].strip()
            ours_lines = []
            theirs_lines = []
            in_ours    = True
            i += 1

            # collect ours and theirs
            while i < len(lines):
                current = lines[i]

                if current.strip() == SEPARATOR:
                    in_ours = False
                    i += 1
                    continue

                if current.startswith(THEIRS_END):
                    end_line = i
                    conflicts.append(Conflict(
                        ours      = "".join(ours_lines),
                        theirs    = "".join(theirs_lines),
                        branch    = branch,
                        start_line= start_line,
                        end_line  = end_line,
                    ))
                    break

                if in_ours:
                    ours_lines.append(current)
                else:
                    theirs_lines.append(current)

                i += 1

        i += 1

    return conflicts


def has_conflicts(filepath):
    """Quick check if file has conflicts"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return OURS_START in content
    except Exception:
        return False


def count_conflicts(filepath):
    """Count number of conflicts in file"""
    return len(parse_conflicts(filepath))


def get_clean_content(filepath, resolved_conflicts):
    """
    Build clean file content after resolving conflicts
    resolved_conflicts: dict of {conflict_index: chosen_text}
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return None

    conflicts = parse_conflicts(filepath)
    if not conflicts:
        return "".join(lines)

    result     = []
    current    = 0
    conf_index = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # check if we hit a conflict start
        if conf_index < len(conflicts) and i == conflicts[conf_index].start_line:
            conflict = conflicts[conf_index]

            # insert resolved text
            chosen = resolved_conflicts.get(conf_index, conflict.ours)
            result.append(chosen)

            # skip to end of conflict block
            i = conflict.end_line + 1
            conf_index += 1
            continue

        result.append(line)
        i += 1

    return "".join(result)


def write_resolved(filepath, resolved_conflicts):
    """Write resolved content back to file"""
    content = get_clean_content(filepath, resolved_conflicts)
    if content is None:
        return False

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False
