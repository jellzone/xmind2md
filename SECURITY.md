# Security Policy

中文或英文报告均可。请勿在公开 Issue 或 PR 中披露漏洞细节、私密思维导图或凭据。

## Supported versions

Security fixes target the latest commit on `main`. Older snapshots have no
separate maintenance or backport commitment. The project currently has no
automated security audit or published support SLA.

## Reporting a vulnerability

Do not disclose vulnerability details in a public issue or pull request.

If GitHub shows a **Report a vulnerability** button in this repository's
[Security tab](https://github.com/jellzone/xmind2md/security), use that private
reporting channel. Its availability depends on the repository settings.

Otherwise, [open an issue](https://github.com/jellzone/xmind2md/issues/new)
with only the subject "Private security report — contact requested" and a
request for a maintainer to arrange a private channel. Do not include exploit
details, files, logs, or personal information there. Wait for a private
channel before sharing the report.

Once a private channel is available, include:

- The affected commit, Python version and operating system.
- A minimal synthetic input and exact reproduction commands.
- Expected behavior, actual behavior and security impact.
- Whether the issue has already been disclosed elsewhere.

## Scope and handling input files

xmind2md reads ZIP archives containing JSON or XML, then writes a local Markdown
file. Reports about malicious input causing resource exhaustion, unintended
file access or writes, or unsafe generated links are welcome.

The tool does not impose archive-size, nesting-depth or runtime limits and
does not sanitize links for a particular Markdown renderer. Its output can
contain source content in the file and the terminal preview.

- Convert trusted files; isolate untrusted files in a restricted environment
  with resource limits.
- Review the Markdown and links before rendering, publishing or sharing it.
- Use an explicit `-o` path when you need to protect an existing Markdown file:
  the script overwrites the selected output path.
- Use synthetic or redacted files in public reports.

There is no stated response-time guarantee or bug bounty.
