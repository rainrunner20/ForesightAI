# Host the research console on GitHub Pages

The site in `web/` is static HTML, CSS, and JavaScript. No Node build step or API key is needed. GitHub Pages can host the **synthetic demo UI**; local Qwen/Ollama experiments still run on your own machine and the resulting JSON can be imported manually.

## First-time setup (GitHub owner action)

1. Open repository **Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the publishing source.
3. Open **Actions → Deploy dashboard to GitHub Pages (manual) → Run workflow**, select `main`, and run it.
4. Visit the URL shown in the workflow's deployment result. For this public repo it is expected to be under `https://rainrunner20.github.io/ForesightAI/`, but **verify the actual Pages URL before sharing**.

The workflow intentionally uses **manual dispatch**, so creating it does not automatically attempt a Pages deployment before repository settings are configured. It uploads only `web/`, not the research data, Python scripts, or local files.

GitHub Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## What a public visitor sees

- Seven dashboard pages, five interactive twists, a fictional network and example replay.
- Synthetic values are labeled as such. The hosted site **does not make real LLM calls**.
- A visitor can upload a ForesightAI JSON report generated locally. The report is read in the browser; the site does not upload it to a server.

Do not publish confidential real-world data, API keys or private annotation files in this repository.
