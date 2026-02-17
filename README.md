This is an incomplete project.

# cliargparser
A Python library for building command-line interfaces with Options, Commands, and Operands.
Designed for simplicity from both user's perspective and parser's perspective.

It is opinionated for sake of determinism and ambiguity-safe.
The parser is feed-forward (single-pass, no backtracking).

The philosophy: all CLI arguments fall into three types:

Option – Named argument that may take values.

Command – Subcommand that triggers specific behavior.

Operand – Positional argument representing input data.


# Example
```python
from cliargparser import Command
from cliargparser.actions import count_presence_action, store_true_action
from cliargparser.enums import ParseMode

# -------------------------
# Option example
# -------------------------
root = Command()
root.option("foo", type_converter=int)  # default action stores value
args = "--foo 15"
print(root.parse_arguments(args))
# Output: Namespace(foo=15)

# -------------------------
# Flag example (present)
# -------------------------
root = Command()
root.option("verbose", action=store_true_action)  # flag
args = "--verbose"
print(root.parse_arguments(args))
# Output: Namespace(verbose=True)

# -------------------------
# Option with count action
# -------------------------
root = Command()
root.option("times", action=count_presence_action)  # counts occurrences
args = "--times --times --times"
print(root.parse_arguments(args))
# Output: Namespace(times=3)

# -------------------------
# Command + Operand example
# -------------------------
root = Command()
mv = root.subcommand("mv", parse_mode=ParseMode.OPERAND)
mv.operand("source")
mv.operand("destination")

args = "mv source_file.txt destination_file.txt"
print(root.parse_arguments(args))
# Output: Namespace(mv=Namespace(source='source_file.txt', destination='destination_file.txt'))
```
