from itertools import product
import subprocess
import json
import time
from typing import Any, Optional, Dict, List, Set, Tuple
import re
from collections import defaultdict

REGISTRY = "docker://ghcr.io/ublue-os/"

IMAGE_MATRIX = {
    "base": ["desktop", "deck", "nvidia-closed", "nvidia-open"],
    "de": ["kde", "gnome"],
}

RETRIES = 3
RETRY_WAIT = 5
FEDORA_PATTERN = re.compile(r"\.fc\d\d")
STABLE_START_PATTERN = re.compile(r"\d\d\.\d")

def OTHER_START_PATTERN(target: str) -> re.Pattern:
    return re.compile(rf"{target}-\d\d\.\d")

PATTERN_ADD = "\n| ✨ | {name} | | {version} |"
PATTERN_CHANGE = "\n| 🔄 | {name} | {prev} | {new} |"
PATTERN_REMOVE = "\n| ❌ | {name} | {version} | |"
PATTERN_PKGREL_CHANGED = "{prev} ➡️ {new}"
PATTERN_PKGREL = "{version}"
COMMON_PAT = "### All Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n"
OTHER_NAMES = {
    "desktop": "### Desktop Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n",
    "deck": "### Deck Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n",
    "kde": "### KDE Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n",
    "gnome": "### Gnome Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n",
    "nvidia": "### Nvidia Images\n| | Name | Previous | New |\n| --- | --- | --- | --- |{changes}\n\n",
}

COMMITS_FORMAT = "### Commits\n| Hash | Subject | Author |\n| --- | --- | --- |{commits}\n\n"
COMMIT_FORMAT = "\n| **[{short}](https://github.com/ublue-os/bazzite/commit/{hash})** | {subject} | {author} |"

CHANGELOG_TITLE = "{tag}: {pretty}"
CHANGELOG_FORMAT = """\
{handwritten}

From previous `{target}` version `{prev}` there have been the following changes. **One package per new version shown.**

### Major packages
| Name | Version |
| --- | --- |
| **Kernel** | {pkgrel:kernel} |
| **Firmware** | {pkgrel:atheros-firmware} |
| **Mesa** | {pkgrel:mesa-filesystem} |
| **Gamescope** | {pkgrel:gamescope} |
| **Gnome** | {pkgrel:gnome-control-center-filesystem} |
| **KDE** | {pkgrel:plasma-desktop} |
| **[HHD](https://github.com/hhd-dev/hhd)** | {pkgrel:hhd} |

{changes}

### How to rebase
For current users, type the following to rebase to this version:
```bash
# For this branch (if latest):
bazzite-rollback-helper rebase {target}
# For this specific image:
bazzite-rollback-helper rebase {curr}
