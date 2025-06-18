import streamlit as st

# --- PASSWORD CHECK ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "Shorrocks":  # change this
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # cleanup
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        return False
    else:
        return True

if not check_password():
    st.stop()
# --- END PASSWORD CHECK ---


import pandas as pd
import itertools
import time
import math

st.set_page_config(page_title="Shorrocks Decomposition App")
st.title("Shorrocks Dimensional Decomposition of M1")

# Step 1: Input number of dimensions
max_dims = 5
d = st.number_input("Enter number of dimensions (max 5):", min_value=1, max_value=max_dims, value=3)

dim_names = [chr(97 + i) for i in range(d)]  # ['a', 'b', 'c', ...]

# Step 2: Generate all 2^d combinations (0 = not deprived, 1 = deprived)
combos = list(itertools.product([1, 0], repeat=d))
combo_df = pd.DataFrame(combos, columns=dim_names)

# Display combinations matrix
st.subheader("Matrix of Combinations (1 = deprived, 0 = not deprived)")
st.dataframe(combo_df.astype(str))

# Step 4: Ask user to proceed with Shorrocks decomposition
if st.button("Do you want to see the dimensional contribution based on Shorrocks approach?"):
    expressions = {}
    for j, dim in enumerate(dim_names):
        st.markdown(f"### Shorrocks Decomposition for Dimension '{dim}'")

        # Step 5: Split into S1 and S0
        S1 = combo_df[combo_df[dim] == 1].copy()
        S0 = combo_df[combo_df[dim] == 0].copy()
        st.markdown("#### S1 (Combinations where dimension is present):")
        st.dataframe(S1.astype(str))

        st.markdown("#### S0 (Combinations where dimension is absent):")
        st.dataframe(S0.astype(str))

        time.sleep(2)
        st.markdown("Now let the sum of elements in the of any row t in S₁ʲ be δ(t) and of any row t' in S₀ʲ be δ(t')")

        # Updated Heading
        st.markdown(f"<h4 style='font-size:26px;'>Deriving C<sub>{dim}</sub>(M)</h4>", unsafe_allow_html=True)
        st.markdown("<span style='font-size:14px'>Eq. 1: Let Cj(M) = X - Y</span>", unsafe_allow_html=True)
        time.sleep(1)
        st.markdown("<span style='font-size:14px'>Eq. 2: Solving X & Y separately</span>", unsafe_allow_html=True)
        time.sleep(1)
        st.markdown("<span style='font-size:14px'>Eq. 3: Now X</span>", unsafe_allow_html=True)

        expr_lines = []
        eq_counter = 4
        for idx, row in S1.iterrows():
            delta_t = int(row.sum())
            w_t = (math.factorial(delta_t - 1) * math.factorial(d - delta_t)) / math.factorial(d)
            label = "M(" + ",".join([dim_names[i] if row[i]==1 else "0" for i in range(d)]) + ")"
            step = f"({delta_t - 1})!·({d - delta_t})!/({d})!*{label}"
            st.markdown(f"<span style='font-size:14px'>Eq. {eq_counter}: {step}</span>", unsafe_allow_html=True)
            expr_lines.append(f"+ {int(w_t * math.factorial(d))}/{math.factorial(d)}·{label}")
            time.sleep(1)
            eq_counter += 1

        st.markdown(f"<span style='font-size:14px'>Eq. {eq_counter}: Now calculating Y</span>", unsafe_allow_html=True)
        eq_counter += 1

        for idx, row in S0.iterrows():
            delta_tp = int(row.sum())
            w_tp = (math.factorial(delta_tp) * math.factorial(d - 1 - delta_tp)) / math.factorial(d)
            label = "M(" + ",".join([dim_names[i] if row[i]==1 else "0" for i in range(d)]) + ")"
            step = f"{delta_tp}!·({d - 1 - delta_tp})!/({d})!*{label}"
            st.markdown(f"<span style='font-size:14px'>Eq. {eq_counter}: {step}</span>", unsafe_allow_html=True)
            expr_lines.append(f"- {int(w_tp * math.factorial(d))}/{math.factorial(d)}·{label}")
            time.sleep(1)
            eq_counter += 1

        # Combine and clean up + - issues
        full_expr = " ".join(expr_lines)
        full_expr = full_expr.replace("+ -", "-").strip()
        expression = f"C({dim}) = {full_expr}"

        st.markdown(f"<pre style='font-size:36px; font-weight:bold; font-style:italic; color:darkblue;'>{expression}</pre>", unsafe_allow_html=True)
        expressions[dim] = expression
        st.divider()

    # Step 8: Sum all contributions and show algebraic cancellation
    st.markdown("### Final Step: Verifying Total Contribution")
    st.markdown("C<sub>a</sub>(M) + C<sub>b</sub>(M) + ... = M", unsafe_allow_html=True)
    st.markdown("Each + and - term from S₁ and S₀ respectively cancel out or contribute positively, leading to total M")
    st.subheader("Symbolic Expressions")
    for dim in dim_names:
        st.markdown(f"<pre style='font-size:36px; font-weight:bold; font-style:italic; color:darkblue;'>{expressions[dim]}</pre>", unsafe_allow_html=True)
    st.success("As we used all 2^d combinations and weights based on Shorrocks, sum of contributions exactly equals M")
