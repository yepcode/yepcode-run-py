import re
from typing import List, Dict, Literal, TypedDict
from dataclasses import dataclass


@dataclass
class Pattern:
    pattern: str
    points: int


class LanguageDetector:
    # JavaScript patterns with their corresponding scores
    _js_patterns: List[Pattern] = [
        Pattern(r"undefined", 2),  # undefined keyword
        Pattern(r"console\.log( )*\(", 2),  # console.log calls
        Pattern(r"(var|const|let)( )+\w+( )*=?", 2),  # Variable declarations
        Pattern(r"(('|\").+('|\")( )*|\w+):( )*[{\[]", 2),  # Array/Object declarations
        Pattern(r"===", 1),  # === operator
        Pattern(r"!==", 1),  # !== operator
        Pattern(
            r"function\*?(( )+[\$\w]+( )*\(.*\)|( )*\(.*\))", 1
        ),  # Function definition
        Pattern(r"null", 1),  # null keyword
        Pattern(r"\(.*\)( )*=>( )*.+", 1),  # lambda expression
        Pattern(r"(else )?if( )+\(.+\)", 1),  # if statements
        Pattern(r"async( )+function", 2),  # async function
        Pattern(r"module\.exports( )*=", 2),  # module.exports
    ]

    # Python patterns with their corresponding scores
    _python_patterns: List[Pattern] = [
        Pattern(r"def( )+\w+\(.*\)( )*:", 2),  # Function definition
        Pattern(r"from [\w\.]+ import (\w+|\*)", 2),  # from import
        Pattern(r"class( )*\w+(\(( )*\w+( )*\))?( )*:", 2),  # class definition
        Pattern(r"if( )+(.+)( )*:", 2),  # if statement
        Pattern(r"elif( )+(.+)( )*:", 2),  # elif keyword
        Pattern(r"else:", 2),  # else keyword
        Pattern(r"for (\w+|\(?\w+,( )*\w+\)?) in (.+):", 2),  # for loop
        Pattern(r"\w+( )*=( )*\w+(?!;)(\n|$)", 1),  # Variable assignment
        Pattern(r"import ([[^\.]\w])+", 1),  # import statement
        Pattern(r"print((( )*\(.+\))|( )+.+)", 1),  # print statement
    ]

    @classmethod
    def detect_language(cls, code: str) -> Literal["javascript", "python", "unknown"]:
        """
        Detects if the given code is JavaScript or Python.

        Args:
            code: The source code to analyze

        Returns:
            'javascript', 'python', or 'unknown'
        """
        # Remove comments and empty lines to clean the code
        clean_code = cls._clean_code(code)

        if not clean_code:
            return "unknown"

        js_score = cls._calculate_score(clean_code, cls._js_patterns)
        py_score = cls._calculate_score(clean_code, cls._python_patterns)

        # Determine the language based on weighted scores
        if js_score > py_score:
            return "javascript"
        if py_score > js_score:
            return "python"
        return "unknown"

    @staticmethod
    def _clean_code(code: str) -> str:
        """
        Removes comments and empty lines from the code.

        Args:
            code: The source code to clean

        Returns:
            Cleaned code string
        """
        # Remove JS comments (both single-line and multi-line)
        code = re.sub(r"/\*[\s\S]*?\*/|//.*", "", code)
        # Remove Python comments
        code = re.sub(r"#.*", "", code)
        # Remove empty lines and trim
        return code.strip()

    @staticmethod
    def _calculate_score(code: str, patterns: List[Pattern]) -> int:
        """
        Calculates the score for a given set of patterns in the code.

        Args:
            code: The source code to analyze
            patterns: List of patterns to check against

        Returns:
            Total score for the matched patterns
        """
        score = 0
        for pattern in patterns:
            if re.search(pattern.pattern, code):
                score += pattern.points
        return score
