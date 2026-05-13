---
name: Feature request
about: Suggest a new option, style, or behavior for LabelSmith
title: "[feature] "
labels: [enhancement]
assignees: []
---

## Use case

<!-- What are you trying to do? What kind of labels are you working
     with (spreadsheet headers, form captions, checksheet questions,
     etc.)? Why do the current functions/options fall short? -->

## Proposed behavior

<!-- Describe the change you'd like to see. If you have a concrete
     API in mind (a new keyword argument, a new style, etc.), spell
     it out. -->

## Example input / output

<!-- Show the inputs you'd pass in and the outputs you'd expect after
     this change. Concrete examples make the proposal much easier to
     evaluate. -->

```python
from labelsmith import field_name

field_name("EXAMPLE INPUT", ...)   # 'expected_output'
```

## Existing behavior impact

<!-- Would this change anything about how LabelSmith behaves today for
     callers that don't use the new option? If yes, please describe
     the difference. -->

- [ ] No change to existing behavior (opt-in only)
- [ ] Existing behavior would change for some inputs (please describe)

## Out-of-scope reminders

LabelSmith intentionally avoids:

- Excel / PDF parsing
- AI / LLM calls
- Database integration
- Schema generation

Features in those areas are better suited to companion packages.
