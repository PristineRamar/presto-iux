function highlightPythonCode(code) {
  // Define the list of Python keywords
  const keywords = [
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
  ];

  // Define the CSS classes for syntax highlighting
  const cssClasses = {
    keyword: "keyword",
    comment: "comment",
    string: "string",
    number: "number",
    operator: "operator",
    builtin: "builtin",
  };

  // Escape special characters in the code
  code = code
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Split the code into lines
  const lines = code.split("\n");

  // Process each line and apply syntax highlighting
  const highlightedCode = lines
    .map((line) => {
      // Check for comments
      if (line.trim().startsWith("#")) {
        return `<span class="${cssClasses.comment}">${line}</span>`;
      }

      // Split the line into individual tokens
      const tokens = line.split(/(\W)/);

      // Process each token and apply syntax highlighting
      const highlightedLine = tokens
        .map((token) => {
          // Check for keywords
          if (keywords.includes(token)) {
            return `<span class="${cssClasses.keyword}">${token}</span>`;
          }

          // Check for strings
          if (/^(['"]).*\1$/.test(token)) {
            return `<span class="${cssClasses.string}">${token}</span>`;
          }

          // Check for numbers
          if (/^\d+$/.test(token)) {
            return `<span class="${cssClasses.number}">${token}</span>`;
          }

          // Check for operators
          if (
            /^\+|-|\*|\/|%|=|==|!=|<|>|<=|>=|&|\||!|~|\^|\[|\]|{|}|,|\(|\)|:|\.|\?|@|->$/.test(
              token
            )
          ) {
            return `<span class="${cssClasses.operator}">${token}</span>`;
          }

          // Default case (assumed to be built-in functions, variables, etc.)
          return `<span class="${cssClasses.builtin}">${token}</span>`;
        })
        .join("");

      return highlightedLine;
    })
    .join("\n");

  // Wrap the highlighted code in a pre tag and return
  return `<pre>${highlightedCode}</pre>`;
}
