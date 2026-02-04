import os
import sys

def longest_common_prefix(strs):
    if not strs:
        return ""
    s1 = min(strs)
    s2 = max(strs)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


def longest_common_suffix(strs):
    rev = [s[::-1] for s in strs]
    return longest_common_prefix(rev)[::-1]


def remove_common_parts(strs):
    prefix = longest_common_prefix(strs)
    suffix = longest_common_suffix(strs)
    _, ext = os.path.splitext(strs[0])

    result = []
    for s in strs:
        core = s[len(prefix):]
        if suffix:
            core = core[:-len(suffix)]
        result.append(core)

    return prefix, suffix, ext, result

def rename_files(dirpath):
    src = os.listdir(dirpath)
    _, _, ext, dst = remove_common_parts(src)
    for i in range(len(src)):
        os.rename(os.path.join(dirpath, src[i]), os.path.join(dirpath, dst[i] + ext))

dirpath = "pdfs" if len(sys.argv) < 2 else sys.argv[1]
rename_files(dirpath)
