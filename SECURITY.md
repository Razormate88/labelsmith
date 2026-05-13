# Security policy

## Scope and design posture

LabelSmith is a small, local string-transformation library. By design
it:

* Has **no runtime dependencies** — only Python's standard library.
* Makes **no network calls**.
* Does **not** execute any dynamic code (no `eval`, no `exec`, no
  importing of user input).
* Does **not** read or write files.
* Does **not** process or store secrets.

The public API takes strings and returns strings. The intended attack
surface is correspondingly small.

## Supported versions

Security fixes are applied to the latest released version. Older
versions are not patched in place; please upgrade to the latest
release on PyPI: <https://pypi.org/project/labelsmith/>.

## Reporting a vulnerability

If you believe you've found a security issue in LabelSmith:

1. **Do not** post the details in a public GitHub issue or PR if the
   report contains sensitive information.
2. Open a private report via GitHub's "Report a vulnerability" link
   on <https://github.com/Razormate88/labelsmith/security> if
   available.
3. If a private channel is not available, open a regular GitHub issue
   with a **minimal, non-sensitive reproduction** that does not
   include real customer data, internal labels, or proprietary
   information. Sanitize any examples before posting.

When reporting, please include:

* The LabelSmith version (e.g. `0.1.1`).
* The Python version and OS.
* The minimal input and the unexpected/unsafe output.
* Why you believe the behavior is a security issue (e.g. unsafe
  identifier, unbounded resource use, regex backtracking concern).

We will acknowledge the report and work on a fix within a reasonable
timeframe for a community-maintained, side-project-scale package.

## Things that are *not* security issues

* Output that "looks ugly" but is deterministic and safe (e.g.
  `pfmea_cause_s` for `"PFMEA Cause(s)"`).
* Behavioral choices documented in the README and CHANGELOG (acronym
  preservation, fallback names, reserved-word mangling).
* Feature requests for new styles, options, or integrations — please
  use the feature-request template instead.
