# Security and data handling

ForesightAI is a university research prototype, not a fact-checking or financial decision service.

- Only supply **public or properly licensed** datasets. Never commit private claims, personal information, API keys or access tokens.
- The dashboard processes imported JSON locally in the browser; it does not send that file to an external backend.
- The Ollama provider only accepts loopback HTTP endpoints by default. Run local models on a trusted machine.
- Treat all model outputs as untrusted text. Cite and audit source evidence before interpreting results.
- To report a bug or security concern, open a GitHub issue with a minimal reproduction that contains no secrets. For sensitive vulnerability details, avoid posting exploit information publicly; contact repository maintainers through a private channel if available.

Security testing beyond the local unit suite has **not** been completed.
