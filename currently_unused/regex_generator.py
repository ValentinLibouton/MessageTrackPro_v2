import re


class RegexGenerator:
    def __init__(self):
        self.pattern = ""

    def add_literal(self, literal):
        self.pattern += re.escape(literal)
        return self

    def add_any_digit(self):
        self.pattern += r"\d"
        return self

    def add_any_word(self):
        self.pattern += r"\w"
        return self

    def add_any_whitespace(self):
        self.pattern += r"\s"
        return self

    def add_custom_class(self, char_class):
        self.pattern += f"[{char_class}]"
        return self

    def add_quantifier(self, quantifier):
        self.pattern += quantifier
        return self

    def add_group(self, group_pattern):
        self.pattern += f"({group_pattern})"
        return self

    def add_alternation(self, alt_patterns):
        self.pattern += "(" + "|".join(alt_patterns) + ")"
        return self

    def build(self):
        return self.pattern


if __name__ == "__main__":
    regex_gen = RegexGenerator()
    regex = (regex_gen.add_literal("Hello")
             .add_any_whitespace()
             .add_any_word()
             .add_quantifier("+")
             .add_literal("!")
             .build())

    print(f"Regex générée : {regex}")
