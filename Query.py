from Condition import Condition
import constants
import re


class Query:
    def __init__(self, table, dictionary) -> None:
        self.table = table
        self.dictionary = dictionary
        self.key_list = []
        self.value_list = []
        self.cond_list = []
        self.error = ""
        self.query = self.build_conditions()

    def build_conditions(self) -> str:
        for key in self.dictionary.keys():
            if key not in constants.short_terms.values():
                self.error = f"Invalid key {key}."
                return self.error
            match key:
                case "name":
                    if "PARTIAL" not in self.dictionary[key]:
                        cond = Condition(key, self.dictionary[key], "=")
                        self.key_list = [cond.key]
                        self.value_list = [cond.value]
                        cond.value = "?"
                        self.cond_list = [str(cond)]
                        break
                    else:
                        self.dictionary[key] = self.dictionary[key].replace(
                            "PARTIAL", ""
                        )
                        cond = Condition("name", f"%{self.dictionary[key]}%", "LIKE")
                case "archetype":
                    cond = Condition(
                        key, f"(^|, ){re.escape(self.dictionary[key])}(,|$)", "REGEXP"
                    )
                case "linkmarkers":
                    sorted_markers = [
                        value.lower().replace(" ", "")
                        for value in self.dictionary[key].split(",")
                    ]
                    try:
                        sorted_markers.sort(
                            key=[
                                marker.lower() for marker in constants.link_markers
                            ].index
                        )
                    except ValueError:
                        self.error += f'One or more link markers are invalid: {", ".join(sorted_markers)}\n'
                    markers_regex = ",.*".join(sorted_markers)

                    # Match cards with at least the listed markers, but without partially matching hyphenated markers.
                    # For example, "Left, Top" doesn't match "Bottom-Left, Top".
                    pattern = f"(^|.*[^-]+){markers_regex}($|[^-]+.*)"
                    cond = Condition(key, pattern, "REGEXP")
                case "sort" | "order":
                    continue
                case _:
                    cond = Condition(key, self.dictionary[key])
                    if cond.error:
                        self.error += (
                            f"{cond.value} is not a valid value for key {cond.key}.\n"
                        )

            self._add_key_value_condition(cond)
        ordering_string = (
            f" ORDER BY {constants.short_terms[self.dictionary['sort']]} {self.dictionary['order']};"
            if "sort" in self.dictionary.keys()
            else ""
        )
        return f"SELECT * FROM {self.table}{' WHERE ' if len(self.cond_list) != 0 else ''}{' AND '.join(self.cond_list) + ordering_string}"

    def _add_key_value_condition(self, cond) -> None:
        self.key_list.append(cond.key)
        self.value_list.append(cond.value)
        self.dictionary[cond.key] = cond.value
        cond.value = "?"
        self.cond_list.append(str(cond))

    def __str__(self) -> str:
        return self.query
