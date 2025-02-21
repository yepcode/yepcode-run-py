import pytest
from yepcode_run.utils.language_detector import LanguageDetector


def test_detect_javascript():
    js_code = """
        const hello = "world";
        function test(param) {
          if (param === undefined) {
            console.log("undefined param");
            return null;
          }
          return param;
        }
        const arrow = () => "test";
    """
    assert LanguageDetector.detect_language(js_code) == "javascript"


def test_detect_javascript_2():
    js_code = """
    async function main() {
      return { data: "test data" }
    }

    module.exports = { main };
    """
    assert LanguageDetector.detect_language(js_code) == "javascript"


def test_detect_python():
    py_code = """
        def hello_world():
          print("Hello, World!")

        class MyClass:
          def __init__(self):
            self.value = 42

        for item in items:
          if item > 0:
            print(item)
          elif item == 0:
            continue
    """
    assert LanguageDetector.detect_language(py_code) == "python"


def test_empty_code():
    assert LanguageDetector.detect_language("") == "unknown"


def test_code_with_comments():
    js_code_with_comments = """
        // This is a JavaScript comment
        /* Multi-line
           comment */
        const x = 1;
        console.log(x);
    """

    py_code_with_comments = """
        # This is a Python comment
        def test():
          # Another comment
          print("test")
    """

    assert LanguageDetector.detect_language(js_code_with_comments) == "javascript"
    assert LanguageDetector.detect_language(py_code_with_comments) == "python"
