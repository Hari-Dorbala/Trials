import itertools
import math

import pandas as pd
import streamlit as st


# Must be the first Streamlit command.
st.set_page_config(page_title="Shorrocks Decomposition App")

st.title("Shorrocks Dimensional Decomposition of M1")

# Step 1: Input number of dimensions
max_dims = 5
d = int(
    st.number_input(
        "Enter number of dimensions (max 5):",
        min_value=1,
        max_value=max_dims,
        value=3,
        step=1,
    )
)

dim_names = [chr(97 + i) for i in range(d)]

# Step 2: Generate all 2^d combinations
# 0 = not deprived, 1 = deprived
combos = list(itertools.product([1, 0], repeat=d))
combo_df = pd.DataFrame(combos, columns=dim_names)

# Display combinations matrix
st.subheader("Matrix of Combinations (1 = deprived, 0 = not deprived)")
st.dataframe(combo_df.astype(str), use_container_width=True)

# Step 3: Run the Shorrocks decomposition
button_label = (
    "Do you want to see the dimensional contribution "
    "based on Shorrocks approach?"
)

if st.button(button_label):
    expressions = {}

    for j, dim in enumerate(dim_names):
        st.markdown(f"### Shorrocks Decomposition for Dimension '{dim}'")

        # Split into S1 and S0
        S1 = combo_df[combo_df[dim] == 1].copy()
        S0 = combo_df[combo_df[dim] == 0].copy()

        st.markdown("#### S1 (Combinations where dimension is present):")
        st.dataframe(S1.astype(str), use_container_width=True)

        st.markdown("#### S0 (Combinations where dimension is absent):")
        st.dataframe(S0.astype(str), use_container_width=True)

        st.markdown(
            "Let δ(t) denote the sum of entries in any row "
            "t in S₁ʲ, and δ(t′) the sum in any row t′ in S₀ʲ."
        )

        st.markdown(
            f"<h4 style='font-size:26px;'>"
            f"Deriving C<sub>{dim}</sub>(M)</h4>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<span style='font-size:14px'>"
            "Eq. 1: Let Cj(M) = X − Y</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<span style='font-size:14px'>"
            "Eq. 2: Solving X and Y separately</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<span style='font-size:14px'>Eq. 3: Now X</span>",
            unsafe_allow_html=True,
        )

        expr_lines = []
        eq_counter = 4

        # Terms from S1:
        # (δ(t)-1)! × (d-δ(t))! / d!
        for _, row in S1.iterrows():
            values = [int(row[name]) for name in dim_names]
            delta_t = sum(values)

            numerator = (
                math.factorial(delta_t - 1)
                * math.factorial(d - delta_t)
            )

            label_values = [
                dim_names[i] if values[i] == 1 else "0"
                for i in range(d)
            ]
            label = "M(" + ", ".join(label_values) + ")"

            step = (
                f"({delta_t - 1})!·({d - delta_t})!/"
                f"({d})!*{label}"
            )

            st.markdown(
                f"<span style='font-size:14px'>"
                f"Eq. {eq_counter}: {step}</span>",
                unsafe_allow_html=True,
            )

            expr_lines.append(
                f"+ {numerator}/{math.factorial(d)}·{label}"
            )
            eq_counter += 1

        st.markdown(
            f"<span style='font-size:14px'>"
            f"Eq. {eq_counter}: Now calculating Y</span>",
            unsafe_allow_html=True,
        )
        eq_counter += 1

        # Terms from S0:
        # δ(t′)! × (d-1-δ(t′))! / d!
        for _, row in S0.iterrows():
            values = [int(row[name]) for name in dim_names]
            delta_tp = sum(values)

            numerator = (
                math.factorial(delta_tp)
                * math.factorial(d - 1 - delta_tp)
            )

            label_values = [
                dim_names[i] if values[i] == 1 else "0"
                for i in range(d)
            ]
            label = "M(" + ", ".join(label_values) + ")"

            step = (
                f"{delta_tp}!·({d - 1 - delta_tp})!/"
                f"({d})!*{label}"
            )

            st.markdown(
                f"<span style='font-size:14px'>"
                f"Eq. {eq_counter}: {step}</span>",
                unsafe_allow_html=True,
            )

            expr_lines.append(
                f"- {numerator}/{math.factorial(d)}·{label}"
            )
            eq_counter += 1

        # Combine the positive and negative terms.
        full_expr = " ".join(expr_lines)
        full_expr = full_expr.replace("+ -", "-").strip()
        expression = f"C({dim}) = {full_expr}"

        st.markdown(
            f"<pre style='font-size:36px; font-weight:bold; "
            f"font-style:italic; color:darkblue;'>{expression}</pre>",
            unsafe_allow_html=True,
        )

        expressions[dim] = expression
        st.divider()

    # Final verification
    st.markdown("### Final Step: Verifying Total Contribution")

    all_dimensions = ", ".join(dim_names)
    empty_dimensions = ", ".join(["0"] * d)
    contribution_sum = " + ".join(
        [f"C<sub>{dim}</sub>(M)" for dim in dim_names]
    )

    st.markdown(
        f"{contribution_sum} = "
        f"M({all_dimensions}) − M({empty_dimensions})",
        unsafe_allow_html=True,
    )
    st.markdown(
        "If M for the empty set is zero, the contributions sum to "
        "M for the full set of dimensions."
    )

    st.subheader("Symbolic Expressions")
    for dim in dim_names:
        st.markdown(
            f"<pre style='font-size:36px; font-weight:bold; "
            f"font-style:italic; color:darkblue;'>"
            f"{expressions[dim]}</pre>",
            unsafe_allow_html=True,
        )

    st.success(
        "The Shorrocks contribution weights have been applied to all "
        "2^d combinations."
    )
