import itertools
import math
import string
from fractions import Fraction

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Shorrocks Dimensional Decomposition",
    page_icon="📊",
    layout="wide",
)

st.title("Shorrocks Dimensional Decomposition of M1")
st.write(
    "This app derives the symbolic Shorrocks contribution of each dimension "
    "for a binary deprivation profile."
)

# Choose the number of dimensions.
max_dims = 5
d = int(
    st.number_input(
        "Number of dimensions",
        min_value=1,
        max_value=max_dims,
        value=3,
        step=1,
    )
)

dim_names = list(string.ascii_lowercase[:d])

# Generate every binary profile: 0 = not deprived, 1 = deprived.
profiles = list(itertools.product([0, 1], repeat=d))
profile_df = pd.DataFrame(profiles, columns=dim_names)

st.subheader("All deprivation profiles")
st.caption("In the matrix, 1 means deprived and 0 means not deprived.")
st.dataframe(profile_df, hide_index=True, use_container_width=True)


def profile_label(profile):
    """Display a profile using dimension names in place of 1s."""
    labels = [
        dim_names[i] if value == 1 else "0"
        for i, value in enumerate(profile)
    ]
    return f"M({', '.join(labels)})"


def coalition_label(coalition):
    """Display a coalition, such as {a, c}, or the empty set."""
    members = [dim_names[i] for i, value in enumerate(coalition) if value == 1]
    return "{" + ", ".join(members) + "}" if members else "∅"


def fraction_latex(value):
    """Format an exact fraction for display in a LaTeX equation."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return rf"\frac{{{value.numerator}}}{{{value.denominator}}}"


if st.button("Show dimensional contributions", type="primary"):
    st.subheader("Shorrocks contribution by dimension")

    for j, dim in enumerate(dim_names):
        detail_rows = []
        terms = []

        # For each coalition S that excludes dimension j, calculate:
        # |S|! (d - |S| - 1)! / d! × [M(S ∪ {j}) - M(S)]
        other_dimensions = [i for i in range(d) if i != j]

        for other_values in itertools.product([0, 1], repeat=d - 1):
            coalition = [0] * d
            for i, value in zip(other_dimensions, other_values):
                coalition[i] = value

            coalition_size = sum(coalition)
            weight = Fraction(
                math.factorial(coalition_size)
                * math.factorial(d - coalition_size - 1),
                math.factorial(d),
            )

            profile_without_j = tuple(coalition)

            profile_with_j = coalition.copy()
            profile_with_j[j] = 1
            profile_with_j = tuple(profile_with_j)

            detail_rows.append(
                {
                    "Coalition S": coalition_label(coalition),
                    "|S|": coalition_size,
                    "M(S)": profile_label(profile_without_j),
                    f"M(S ∪ {{{dim}}})": profile_label(profile_with_j),
                    "Weight": str(weight),
                }
            )

            terms.append((1, weight, profile_with_j))
            terms.append((-1, weight, profile_without_j))

        with st.expander(f"Contribution of dimension {dim}", expanded=True):
            st.latex(
                rf"C_{{{dim}}}(M) = "
                rf"\sum_{{S \subseteq N \setminus \{{{dim}\}}}} "
                rf"\frac{{|S|!(d-|S|-1)!}}{{d!}}"
                rf"\left[M(S \cup \{{{dim}\}})-M(S)\right]"
            )

            st.dataframe(
                pd.DataFrame(detail_rows),
                hide_index=True,
                use_container_width=True,
            )

            expression_parts = []
            for sign, weight, profile in terms:
                sign_text = "-" if sign < 0 else "+"
                coefficient = fraction_latex(weight)
                value_label = profile_label(profile)

                if not expression_parts:
                    prefix = "-" if sign < 0 else ""
                else:
                    prefix = f" {sign_text} "

                expression_parts.append(
                    rf"{prefix}{coefficient}\,{value_label}"
                )

            st.latex(
                rf"C_{{{dim}}}(M) = "
                + "".join(expression_parts)
            )

    st.subheader("Efficiency check")
    st.latex(
        r"\sum_{j=1}^{d} C_j(M)"
        r" = M(\text{all dimensions}) - M(\varnothing)"
    )
    st.caption(
        "If the value for the empty set of dimensions is zero, "
        "the contributions sum to M(all dimensions)."
    )
    st.success("The contribution weights are calculated exactly as fractions.")
