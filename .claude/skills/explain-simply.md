# explain-simply

Explain any code snippet, file, or technical concept in plain language that a beginner can understand.

## Steps

1. Check if the user passed something as an argument (a concept name, a file path, or a code snippet).
   - If a file path: read the file and use its contents as the subject.
   - If a concept or snippet: use it directly.
   - If nothing was provided: ask the user what they want explained.

2. Identify what the subject is (a function, a class, an algorithm, a tool, a pattern, a term, etc.).

3. Explain it using these rules:
   - No jargon unless you define it immediately after in simple terms.
   - Use short sentences.
   - Use real-world analogies when they help (e.g. "a function is like a recipe — you give it ingredients and it gives you back a dish").
   - If explaining code, walk through what it does step by step, not line by line. Focus on the big picture first, then the details.
   - Never assume the reader knows programming concepts beyond variables and basic math.

4. Structure the explanation as:
   - **What it is** — one sentence summary in plain English.
   - **Why it exists / what problem it solves** — one or two sentences.
   - **How it works** — a simple walkthrough. Use a short example if it helps.
   - **Key things to remember** — two or three bullet points of the most important takeaways.

5. End by asking: "Does that make sense, or would you like me to go deeper on any part?"
