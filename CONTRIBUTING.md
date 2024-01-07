# Contributing to Van Gonography

Thank you for your interest in contributing to Van Gonography! I very much welcome contributions from the community to help improve and expand this project, as a solo developer I can only do so much on my own, therefore I am very grateful for any help I get. Please read the following guidelines to learn how you can contribute to the   project.

## How to Contribute

- If you find a bug or have a feature request, please [open an issue](https://github.com/JoshuaKasa/van-gonography/issues) to report it.
- To contribute code changes, please follow these steps:
  1. Fork the repository.
  2. Create a new branch for your changes.
  3. Make your changes and commit them.
  4. Push your changes to your fork.
  5. Submit a pull request to the `main` branch of the main repository.

## Important Notes

I **DON'T** care about your coding style, as long as it's readable and consistent with the rest of the project, it's fine. I **DO** care about your commit messages tho, please, please, please, be clear, concise and descriptive, it makes it so much easier to review your changes and understand what you did.

Talking about your coding style again, as long as it's not something like:

```py
from typing import get_type_hints
import inspect

def factorial(n: "(n := inspect.stack()[4].frame.f_locals['n']) and (n * factorial(n - 1)) or 1"):    
    return get_type_hints(factorial)["n"]
```

I'm fine with it. You can use CamelCase, snake_case, PascalCase, mYbAlLsCaSe (maybe not please), whatever you want, just *be consistent with it*.

Most important of all tho (this one you is a must), please **COMMENT YOUR CODE**, I don't care if you use `#` or `""" """` or `''' '''`, just please comment your code, it makes it so much easier for me and other contributors to understand what you did and why you did it.

## Code of Conduct

Please note that I have a [Code of Conduct](CODE_OF_CONDUCT.md) in place to ensure a positive and inclusive community. I expect all contributors to adhere to it (please :heart:).