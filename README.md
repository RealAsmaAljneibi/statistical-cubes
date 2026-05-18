# Statistical Cube Builder

An interactive, open-source learning tool that teaches how a single statistical register can produce many different cube versions, one per audience. It is built with [marimo](https://marimo.io), a reactive Python notebook that runs in the browser through WebAssembly, so it can be hosted on GitHub Pages with no server.

The tool is aimed at students, learners, and early-career official-statistics analysts. It mirrors the schema of an Employee Statistical Register, gives the learner controls to pick dimensions and measures, builds the cube live, and shows how disclosure rules change what the cube looks like for the public, for government users, and for internal analysts.

The conceptual framing (one register, many cube versions; structural quality of a cube) follows Almheiri et al. (forthcoming, *Journal of Statistics and Data Science Education*).

---

## Three ways to run

Each option takes under five minutes. Option A is recommended for classroom use.

### Option A. Browser only, zero install

After the repo is published, open the GitHub Pages URL for the project. The notebook loads through WebAssembly and runs in any modern browser. No Python, no install, no shell.

```
https://<your-org>.github.io/cube_builder_tool/
```

### Option B. Local install with pip

```bash
pip install marimo pandas numpy plotly
git clone https://github.com/<your-org>/cube_builder_tool.git
cd cube_builder_tool

marimo run cube_builder.py     # learner mode: hides the code
marimo edit cube_builder.py    # instructor mode: editable cells
```

Use edit mode if you want to change the audience profiles, suppression thresholds, or the dimension lists.

### Option C. Reproducible environment with uv

If you prefer pinned dependencies:

```bash
uv sync
uv run marimo edit cube_builder.py
```

### Regenerate the synthetic dataset

```bash
python scripts/generate_data.py
```

Re-runs deterministically with `np.random.seed(42)`.

---

## What the learner does, step by step

The notebook is eight reactive cells. Each cell explains in plain English what changes when the control above it is moved. No Python is required to read the cells; the few helper functions that build the cube are short and commented.

1. **Load** the synthetic Employee Register and inspect its shape.
2. **Pick an audience profile**: Public, Government / Researchers, or Internal Analyst. This locks the allowed dimensions, the allowed measures, and the disclosure threshold.
3. **Choose 1 to 3 dimensions** from the allowed set.
4. **Choose a measure** from the allowed set.
5. **Build the cube** live with pandas group-by. Disclosure rules are applied on the fly.
6. **Visualise** the result. With three dimensions, the notebook renders a 3D plotly cube. With one or two, it falls back to a bar or heatmap.
7. **Read the metadata block**: total cells, suppressed cells, and a disclosure-safe coverage ratio.
8. **Compare** the same query under all three audiences side by side.

---

## Learning objectives

On completing the notebook, a learner should be able to:

- Explain what a Statistical Cube is and how it relates to a statistical register.
- Identify dimensions, measures, and hierarchies in a register, and explain the role of standardised classifications (such as ADRD in the SCAD case study).
- Build a cube for a chosen audience and apply the corresponding disclosure rule.
- Compute and interpret a disclosure-safe coverage ratio.
- Justify, in plain language, why the same register produces different cubes for different audiences.

---

## Exercises

Three exercises ship with the notebook. Each pushes a specific objective.

### Exercise 1. Find the sparsity edge

In the Public audience, pick dimensions until at least 50 per cent of the cells are suppressed.

- Report the dimension combination and the percentage suppressed.
- Explain in two sentences why the suppression spikes and which dimension drives most of it.

### Exercise 2. Substitute a hierarchy level

In the Government / Researchers audience, replace `Occupation_Major_Group` with `Occupation_Sub_Major_Group`.

- Report the change in: total cells, suppressed cells, and median salary stability across cells.
- Use the result to argue for or against the substitution.

### Exercise 3. Design a fourth audience

Propose a fourth audience profile (for example, a city-level municipality analyst).

- Specify allowed dimensions, allowed measures, suppression threshold, and a short justification.
- Implement the profile by editing the `AUDIENCE_PROFILES` dict near the top of the notebook.
- Run the notebook and compare the result to the existing three versions.

---

## Instructor notes

### Suggested session shapes

**Two-hour intro session** (one classroom slot)

| Time | Activity |
|---:|---|
| 15 min | Concepts: register, dimension, measure, hierarchy, classification |
| 20 min | Walk through Public, Government, Internal versions side by side |
| 25 min | Exercise 1 with discussion |
| 25 min | Exercise 3 with discussion |
| 35 min | Q&A and learner extensions |

**Half-day workshop**

Same as above, plus a full hour on Exercise 2 and an open hour for learners to build a cube on a register of their own choice.

### Assessment

A short rubric is included in `assessment.md`. It scores each exercise on three axes: correctness of the cube build, soundness of the disclosure reasoning, and clarity of the written justification. Instructors are encouraged to adapt the rubric to their own context.

### Common learner stumbles

- Confusing dimensions and measures. Reinforce: dimensions group rows, measures summarise them.
- Treating suppression as data loss. Reframe: suppression is a publication rule, not an arithmetic mistake.
- Assuming more dimensions are always better. Use Exercise 1 to surface the sparsity trade-off.
- Picking the mean over the median in disclosure-controlled cubes. Discuss why the median is more robust under suppression.

---

## Publish to GitHub Pages (WASM, no server)

The notebook runs entirely in the browser, so it publishes as a static site:

```bash
marimo export html-wasm cube_builder.py -o public/index.html --mode run
```

Push the repo to GitHub and enable Pages with `public/` as the source.

A minimal GitHub Actions workflow is included at `.github/workflows/deploy.yml`. On every push to `main` it installs dependencies, exports the WASM site, and publishes it.

---

## Data

All data is synthetic. The file `data/employee_register_synthetic.csv` is 50,000 rows generated by `scripts/generate_data.py` with `np.random.seed(42)` for reproducibility. There is no link to any real individual, employer, or organisation. The column names mirror an Employee Statistical Register schema; the values are drawn from probability distributions chosen to look plausible in a UAE context.

---

## Repo layout

```
cube_builder_tool/
  README.md
  LICENSE
  assessment.md
  cube_builder.py
  requirements.txt
  data/
    employee_register_synthetic.csv
  scripts/
    generate_data.py
  .github/workflows/deploy.yml
```

---

## Citing the tool

If you use the Statistical Cube Builder in a course or paper, please cite:

> Almheiri, S., A. Aljneibi, M. Alshehhi, and Statistical Training Institute. Forthcoming. "Teaching Multidimensional Official Statistics through Statistical Cubes: A Register-Based Framework with an Open-Source Learning Tool." *Journal of Statistics and Data Science Education*.

The Employee Cube classifications follow the Abu Dhabi Reference Data (ADRD) catalogue published by the Statistics Centre - Abu Dhabi: https://scad.gov.ae/abu-dhabi-reference-classifications.

## Funding and institutional support

This tool was developed under the sponsorship of the **Statistics Centre - Abu Dhabi (SCAD)**, United Arab Emirates. The work was carried out within SCAD's Statistical Training Institute and reflects the organisation's commitment to building capacity in official statistics methodology across government analysts and early-career practitioners.

For enquiries, contact: sti@scad.gov.ae

---

## License

MIT, see `LICENSE`.
