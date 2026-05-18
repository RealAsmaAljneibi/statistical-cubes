# Assessment rubric

Use this rubric to score the three exercises in the Statistical Cube Builder. Each exercise is scored on three axes, 0 to 3 points each, for a maximum of 9 points per exercise and 27 points total.

| Score | Meaning |
|---:|---|
| 0 | Missing or wrong |
| 1 | Partially correct but with material gaps |
| 2 | Substantially correct, minor issues |
| 3 | Fully correct and clearly justified |

## Axes

**Build correctness.** Did the learner produce the requested cube, with the right dimensions, measures, and disclosure threshold applied?

**Disclosure reasoning.** Did the learner explain why the cube looks the way it does under the chosen disclosure rule, and what would change under a different audience?

**Written clarity.** Is the written justification clear, concise, free of jargon, and at the right level for the target reader (a peer learner)?

## Exercise scoring

### Exercise 1. Find the sparsity edge

| Axis | What "3" looks like |
|---|---|
| Build correctness | Public audience selected, dimension combination produces >=50% suppression, exact suppression rate reported |
| Disclosure reasoning | Identifies the dimension that drives most suppression and explains the link between sparse combinations and the count threshold |
| Written clarity | Two sentences, no padding, named dimensions and concrete numbers |

### Exercise 2. Substitute a hierarchy level

| Axis | What "3" looks like |
|---|---|
| Build correctness | Two builds executed: one with Occupation_Major_Group, one with Occupation_Sub_Major_Group; reports cell count, suppressed cells, and median salary range for both |
| Disclosure reasoning | Argues for or against the substitution using both disclosure safety and analytical value; recognises the granularity vs sparsity trade-off |
| Written clarity | Argument fits in a short paragraph and is not hedged by vague phrases |

### Exercise 3. Design a fourth audience

| Axis | What "3" looks like |
|---|---|
| Build correctness | A coherent new profile in the audience configuration: allowed dimensions, allowed measures, suppression threshold, and a one-line description; notebook runs without error |
| Disclosure reasoning | Justifies the threshold and the dimension subset for the target audience; compares the new profile to the existing three on at least two queries |
| Written clarity | Profile rationale fits on one page; the trade-offs are stated explicitly |

## Total score and grade band

| Total | Band |
|---:|---|
| 24-27 | Excellent. Ready to teach the framework to others. |
| 18-23 | Solid. Understands the framework, ready to apply it on a new register. |
| 12-17 | Developing. Can build cubes but needs more practice on disclosure reasoning. |
| 0-11 | Re-do recommended. Revisit the side-by-side audience cell and the metadata cell. |

## Adapting the rubric

Instructors are encouraged to:

- Add a fourth axis (for example, "creativity" or "ethics") if the course emphasises it.
- Weight Exercise 3 higher if the course focuses on design rather than execution.
- Replace the Employee Register example with a register from the local context (for example, a Retiree Register or a Jobseeker Register).
