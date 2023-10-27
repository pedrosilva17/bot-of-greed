import constants
import re


class Condition:
    def __init__(self, key: str, value: str, operator: str = ""):
        self.key = key
        self.value = value
        self.operator = operator
        self.error = False
        try:
            self.operator = self.verify_operator() if operator == "" else operator
        except KeyError as err:
            self.error = True

    def __str__(self):
        return f"{self.key} {self.operator} {self.value}"

    def verify_operator(self):
        if not Condition.is_comparable(self.key):
            return "="
        for pattern, operator in constants.regex_comparable_patterns.items():
            if re.search(pattern, self.value):
                self.value = re.sub("gte|lte|gt|lt", "", self.value)
                try:
                    self.value = int(self.value)
                except ValueError:
                    raise KeyError
                return operator
        raise KeyError

    @staticmethod
    def is_comparable(key: str) -> bool:
        """Check if the key is comparable to an integer.

        Args:
            key (str): The search key.

        Returns:
            bool: True if key is comparable, else False.
        """
        return key in ["atk", "def", "level", "rank", "linkval", "scale"]
