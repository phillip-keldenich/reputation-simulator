import argparse
import textwrap
import re


# Try to get nicer help message: Make argParser use <> as newline symbol;
# with the default formatter, newlines are simply ignored.
class MyFormatter(argparse.HelpFormatter):
    def _join_parts(self, part_strings):
        lines = [
            part for part in part_strings if part and part is not argparse.SUPPRESS
        ]
        indentedLines = [self.splitAndIndent(line) for line in lines]
        flattenedListOfLines = sum(indentedLines, [])
        return "".join(flattenedListOfLines)

    def splitAndIndent(self, line):
        indent = len(line) - len(line.lstrip())
        return line.replace("<>", "\n<>" + (" " * indent)).split("<>")

    def _split_lines(self, text, width):
        return textwrap.wrap(
            text, width, drop_whitespace=False, replace_whitespace=False
        )


# Verify polarizing player and N
class PolarizingPlayerAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed!")
        super(PolarizingPlayerAction, self).__init__(option_strings, dest, **kwargs)
        self.argument = argparse.Namespace(option_strings=option_strings, dest=dest)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string == "-N" or option_string == "--N":
            if not (getattr(namespace, "polarizing_player", None) is None):
                raise argparse.ArgumentError(
                    self.argument,
                    "Trying to set N after setting polarizing player is invalid!",
                )

            if type(values) != int or values <= 0:
                raise argparse.ArgumentError(
                    self.argument, "N needs a positive integer argument!"
                )

            setattr(namespace, self.dest, values)
        else:
            coordinates = self._polarizing_parse_values(values)

            if coordinates[0] >= getattr(namespace, "N") or coordinates[1] >= getattr(
                namespace, "N"
            ):
                raise argparse.ArgumentError(
                    self.argument, "Coordinates are out of range!"
                )

            setattr(namespace, self.dest, coordinates)

    def _polarizing_parse_values(self, values):
        if values is None:
            raise argparse.ArgumentError(
                self.argument, "The argument must be of the form (x,y)!"
            )

        m = re.match("^\(\s*([0-9]+)\s*,\s*([0-9]+)\s*\)$", values)

        if m is None:
            raise argparse.ArgumentError(
                self.argument, "The argument must be of the form (x,y)!"
            )

        x = int(m.group(1))
        y = int(m.group(2))

        return (x, y)
