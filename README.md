# Stoicbot

A Stoic Chatbot for Slack

This project will have two phases:

1. Post a daily entry from the Daily Stoic into the relevant slack channel.
2. Allow users to query the Stoicbot and get Stoic thoughts on various topics (e.g. anger, happiness, confidence, etc).

## Tests

For the tests, run the following command:

```bash
python3 pdf_parsing/parser.py && pytest pdf_parsing/test_parser_result.py
```
