import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    return go, mo, np, pd, px


@app.cell
def __(mo):
    mo.md(
        r"""
        # Statistical Cube Builder

        A statistical cube is a multidimensional aggregation produced from a register.
        Pick a few dimensions (rows of the cube) and a measure (the value in each
        cell), and the tool builds the cube for you. The same register can produce
        many cube versions: each audience sees a different slice with different
        disclosure rules. This notebook illustrates the framing used in Almheiri et
        al. (forthcoming, JSDSE).
        """
    )
    return


@app.cell
def __(mo, pd):
    df = pd.read_csv("data/employee_register_synthetic.csv")
    mo.md(
        f"**Loaded register:** {df.shape[0]:,} rows, {df.shape[1]} columns."
    )
    return (df,)


@app.cell
def __(df):
    df.head(5)
    return


@app.cell
def __(df, np, pd):
    # Helper: derive grouped fields used by audience-restricted cubes.
    def aggregate_to_groups(frame):
        out = frame.copy()
        # Age groups
        bins = [17, 24, 34, 44, 54, 64, 100]
        labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        out["age_group"] = pd.cut(out["age"], bins=bins, labels=labels).astype(str)

        # Education level grouped to three broad bands
        edu_map = {
            "No Formal": "Below Secondary",
            "Primary": "Below Secondary",
            "Secondary": "Secondary",
            "Diploma": "Post-Secondary",
            "Bachelor": "Post-Secondary",
            "Master": "Post-Secondary",
            "Doctorate": "Post-Secondary",
        }
        out["education_level_group"] = out["education_level"].map(edu_map)

        # Nationality grouped to broad regions
        nat_map = {
            "United Arab Emirates": "UAE",
            "India": "South Asia",
            "Pakistan": "South Asia",
            "Bangladesh": "South Asia",
            "Sri Lanka": "South Asia",
            "Nepal": "South Asia",
            "Philippines": "South-East Asia",
            "Indonesia": "South-East Asia",
            "China": "East Asia",
            "Egypt": "MENA (non-GCC)",
            "Jordan": "MENA (non-GCC)",
            "Syria": "MENA (non-GCC)",
            "Lebanon": "MENA (non-GCC)",
            "Sudan": "MENA (non-GCC)",
            "Yemen": "MENA (non-GCC)",
            "Morocco": "MENA (non-GCC)",
            "Tunisia": "MENA (non-GCC)",
            "Iran": "MENA (non-GCC)",
            "Iraq": "MENA (non-GCC)",
            "Saudi Arabia": "GCC (non-UAE)",
            "Oman": "GCC (non-UAE)",
            "Kuwait": "GCC (non-UAE)",
            "United Kingdom": "Europe / North America",
            "France": "Europe / North America",
            "Germany": "Europe / North America",
            "Italy": "Europe / North America",
            "Russia": "Europe / North America",
            "United States": "Europe / North America",
            "Canada": "Europe / North America",
            "Australia": "Oceania",
        }
        out["nationality_grouped"] = out["nationality"].map(nat_map).fillna("Other")

        # Occupation major group: first digit of ISCO-08
        out["occupation_major_group"] = out["occupation_unit_group"].astype(str).str[0]

        # Specialization broad bucket (same set, but keep the column name explicit)
        out["specialization_broad"] = out["specialization"]
        return out

    df_enriched = aggregate_to_groups(df)
    df_enriched.shape
    return aggregate_to_groups, df_enriched


@app.cell
def __(mo):
    audience = mo.ui.radio(
        options=["Public", "Government / Researchers", "Internal Analyst"],
        value="Public",
        label="Pick an audience for this cube version:",
    )
    audience
    return (audience,)


@app.cell
def __(audience, mo):
    # Audience profile: allowed dimensions, allowed measures, suppression rule.
    AUDIENCE_PROFILES = {
        "Public": {
            "dims": [
                "age_group",
                "gender",
                "work_emirate",
                "education_level_group",
                "employer_sector",
            ],
            "measures": ["count"],
            "threshold": 10,
        },
        "Government / Researchers": {
            "dims": [
                "age_group",
                "gender",
                "work_emirate",
                "education_level_group",
                "employer_sector",
                "nationality_grouped",
                "specialization_broad",
                "occupation_major_group",
            ],
            "measures": ["count", "median_salary"],
            "threshold": 5,
        },
        "Internal Analyst": {
            "dims": [
                "age_group",
                "gender",
                "work_emirate",
                "work_region",
                "education_level",
                "education_level_group",
                "employer_sector",
                "nationality",
                "nationality_grouped",
                "specialization",
                "specialization_broad",
                "occupation_unit_group",
                "occupation_major_group",
                "activity_class",
                "employment_status",
                "contract_type",
                "marital_status",
                "residence_emirate",
            ],
            "measures": ["count", "sum_salary", "mean_salary", "median_salary"],
            "threshold": 0,
        },
    }

    profile = AUDIENCE_PROFILES[audience.value]
    mo.md(
        f"""
        **Audience:** {audience.value}

        - Allowed dimensions: {len(profile['dims'])}
        - Allowed measures: {", ".join(profile['measures'])}
        - Suppression threshold: cells with count < **{profile['threshold']}** are hidden
        """
    )
    return AUDIENCE_PROFILES, profile


@app.cell
def __(mo, profile):
    dim_picker = mo.ui.multiselect(
        options=profile["dims"],
        value=profile["dims"][:2],
        label="Pick 1 to 3 dimensions:",
    )
    dim_picker
    return (dim_picker,)


@app.cell
def __(mo, profile):
    measure_picker = mo.ui.dropdown(
        options=profile["measures"],
        value=profile["measures"][0],
        label="Pick a measure:",
    )
    measure_picker
    return (measure_picker,)


@app.cell
def __(np, pd):
    def apply_disclosure(cube, threshold):
        """Mark cells with count below threshold as suppressed."""
        if threshold <= 0 or "count" not in cube.columns:
            cube["suppressed"] = False
            return cube
        cube = cube.copy()
        cube["suppressed"] = cube["count"] < threshold
        # Hide measure values for suppressed cells, keep the row so users can see
        # where suppression bites.
        measure_cols = [c for c in cube.columns if c not in ("suppressed",)]
        for col in measure_cols:
            if col == "count":
                cube.loc[cube["suppressed"], col] = np.nan
            elif pd.api.types.is_numeric_dtype(cube[col]):
                cube.loc[cube["suppressed"], col] = np.nan
        return cube

    def build_cube(frame, dims, measure, threshold):
        """Group by `dims` and compute the requested measure."""
        if not dims:
            return pd.DataFrame()

        grouped = frame.groupby(list(dims), dropna=False)
        if measure == "count":
            cube = grouped.size().reset_index(name="count")
        elif measure == "sum_salary":
            cube = grouped.agg(
                count=("monthly_salary", "size"),
                sum_salary=("monthly_salary", "sum"),
            ).reset_index()
        elif measure == "mean_salary":
            cube = grouped.agg(
                count=("monthly_salary", "size"),
                mean_salary=("monthly_salary", "mean"),
            ).reset_index()
            cube["mean_salary"] = cube["mean_salary"].round(0)
        elif measure == "median_salary":
            cube = grouped.agg(
                count=("monthly_salary", "size"),
                median_salary=("monthly_salary", "median"),
            ).reset_index()
        else:
            raise ValueError(f"Unknown measure: {measure}")

        cube = apply_disclosure(cube, threshold)
        return cube

    return apply_disclosure, build_cube


@app.cell
def __(build_cube, df_enriched, dim_picker, measure_picker, mo, profile):
    dims = list(dim_picker.value) if dim_picker.value else []
    if len(dims) > 3:
        dims = dims[:3]

    cube = build_cube(df_enriched, dims, measure_picker.value, profile["threshold"])
    cube_view = mo.ui.table(cube, page_size=15, label="Cube cells")
    cube_view
    return cube, cube_view, dims


@app.cell
def __(cube, dims, go, measure_picker, mo, px):
    def render_cube_plot(cube, dims, measure):
        if cube.empty or not dims:
            return mo.md("_Pick at least one dimension to render a chart._")

        plot_df = cube.dropna(subset=[measure]).copy()
        if plot_df.empty:
            return mo.md("_All cells suppressed. Try fewer or broader dimensions._")

        if len(dims) == 1:
            fig = px.bar(plot_df, x=dims[0], y=measure, title=f"{measure} by {dims[0]}")
            return mo.ui.plotly(fig)

        if len(dims) == 2:
            pivot = plot_df.pivot_table(index=dims[0], columns=dims[1], values=measure, aggfunc="sum")
            fig = px.imshow(
                pivot,
                aspect="auto",
                color_continuous_scale="Blues",
                title=f"{measure} heatmap: {dims[0]} x {dims[1]}",
            )
            return mo.ui.plotly(fig)

        # Three dimensions: render as 3D scatter with categorical positions.
        # Map categorical values to integer positions so axes are readable.
        plot = plot_df.copy()
        cat_maps = {}
        for d in dims:
            cats = sorted(plot[d].astype(str).unique())
            cat_maps[d] = {c: i for i, c in enumerate(cats)}
            plot[f"{d}__pos"] = plot[d].astype(str).map(cat_maps[d])

        values = plot[measure].astype(float)
        size_ref = (values.max() - values.min()) or 1.0
        sizes = 8 + 28 * (values - values.min()) / size_ref

        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=plot[f"{dims[0]}__pos"],
                    y=plot[f"{dims[1]}__pos"],
                    z=plot[f"{dims[2]}__pos"],
                    mode="markers",
                    marker=dict(
                        size=sizes,
                        color=values,
                        colorscale="Viridis",
                        colorbar=dict(title=measure),
                        opacity=0.85,
                    ),
                    text=[
                        f"{dims[0]}={a}<br>{dims[1]}={b}<br>{dims[2]}={c}<br>{measure}={v:,.0f}"
                        for a, b, c, v in zip(
                            plot[dims[0]], plot[dims[1]], plot[dims[2]], values
                        )
                    ],
                    hoverinfo="text",
                )
            ]
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title=dims[0],
                    tickmode="array",
                    tickvals=list(cat_maps[dims[0]].values()),
                    ticktext=list(cat_maps[dims[0]].keys()),
                ),
                yaxis=dict(
                    title=dims[1],
                    tickmode="array",
                    tickvals=list(cat_maps[dims[1]].values()),
                    ticktext=list(cat_maps[dims[1]].keys()),
                ),
                zaxis=dict(
                    title=dims[2],
                    tickmode="array",
                    tickvals=list(cat_maps[dims[2]].values()),
                    ticktext=list(cat_maps[dims[2]].keys()),
                ),
            ),
            title=f"3D cube: {dims[0]} x {dims[1]} x {dims[2]} (size and color = {measure})",
            height=650,
        )
        return mo.ui.plotly(fig)

    plot = render_cube_plot(cube, dims, measure_picker.value)
    plot
    return plot, render_cube_plot


@app.cell
def __(audience, cube, dims, measure_picker, mo, profile):
    total_cells = len(cube)
    suppressed = int(cube["suppressed"].sum()) if "suppressed" in cube.columns else 0
    visible = total_cells - suppressed
    coverage = (visible / total_cells) if total_cells > 0 else 0.0
    pct_suppressed = (100 * suppressed / total_cells) if total_cells > 0 else 0.0

    mo.md(
        f"""
        ## Cube metadata

        - **Audience profile:** {audience.value}
        - **Dimensions:** {", ".join(dims) if dims else "_none_"}
        - **Measure:** {measure_picker.value}
        - **Threshold:** count < {profile['threshold']}
        - **Total cells:** {total_cells:,}
        - **Suppressed cells:** {suppressed:,} ({pct_suppressed:.1f}%)
        - **Disclosure-safe coverage:** {coverage:.2%}
        """
    )
    return coverage, pct_suppressed, suppressed, total_cells, visible


@app.cell
def __(AUDIENCE_PROFILES, build_cube, df_enriched, mo, pd):
    # Side-by-side: same cube specification, three audiences.
    example_dims = ["age_group", "gender", "work_emirate"]
    example_measure = "count"

    versions = {}
    for name, prof in AUDIENCE_PROFILES.items():
        # Only use dimensions allowed for that audience
        allowed = [d for d in example_dims if d in prof["dims"]]
        cube_v = build_cube(df_enriched, allowed, example_measure, prof["threshold"])
        n_total = len(cube_v)
        n_supp = int(cube_v["suppressed"].sum())
        versions[name] = {
            "dims_used": ", ".join(allowed),
            "total_cells": n_total,
            "suppressed": n_supp,
            "visible": n_total - n_supp,
            "threshold": prof["threshold"],
        }

    summary = pd.DataFrame(versions).T
    mo.md(
        "## Same register, three cube versions\n\n"
        "All three versions below ask for the same cube (age_group x gender x work_emirate, "
        "measure = count). They differ only by audience: allowed dimensions and the suppression "
        "threshold change. This illustrates the one-register-to-many-cubes framing."
    )
    return example_dims, example_measure, summary, versions


@app.cell
def __(summary):
    summary
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Learning challenges

        1. Pick dimensions that produce more than 50% suppressed cells for the
           **Public** audience. What does this teach you about cube sparsity and
           why broad public tables tend to collapse small categories together?
        2. Switch to **Internal Analyst** and use `nationality` (the raw column,
           not the grouped one) crossed with `work_region`. Note the cell count.
           Then switch back to **Public** and try the same idea: which dimensions
           do you have to substitute, and what is lost?
        3. Compare median salary against mean salary for the same cube
           (Government / Researchers audience). Which one moves more when small
           cells are suppressed, and why does that matter for transparency?
        """
    )
    return


if __name__ == "__main__":
    app.run()
