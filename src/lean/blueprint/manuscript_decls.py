"""Print every Lean declaration named in a LaTeX file's \\lean{...} tags, one per line.

`lake exe checkdecls` reads this list, so the manuscript's equations stay bound to
declarations that exist. Comments are skipped and tags may span lines.
"""

import re
import sys
from pathlib import Path

text = "\n".join(Path(name).read_text() for name in sys.argv[1:])
text = re.sub(r"(?m)(?<!\\)%.*$", "", text)
names = [name.strip() for tag in re.findall(r"\\lean\{([^}]*)\}", text) for name in tag.split(",")]
declarations = [name for name in names if name]
if declarations:
    print("\n".join(declarations))
