import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AFIA", layout="wide")

# ---------------- Scoring ----------------

def calculate_priority(row, weights):
    components = {}
    components['Risk'] = row['Risk'] * weights['risk']
    components['Criticality'] = row['Criticality'] * weights['criticality']
    components['Compliance'] = weights['compliance'] if row['Compliance'] == 'Yes' else 0
    components['Reactive'] = weights['reactive'] if row['Reactive'] == 'Yes' else 0
    components['Downtime'] = row['DowntimeHours'] * weights['downtime']
    score = sum(components.values())
    return round(score, 1), components

# ---------------- App ----------------

def main():
    st.title("AFIA – Asset and Facilities Intelligence Assistant")
    st.caption("Explainable, configurable work order prioritisation")

    # Sidebar configuration
    st.sidebar.header("Scoring Weights")
    weights = {
        'risk': st.sidebar.slider('Risk weight', 0.0, 2.0, 0.4, 0.1),
        'criticality': st.sidebar.slider('Criticality weight', 0.0, 5.0, 2.0, 0.5),
        'compliance': st.sidebar.slider('Compliance bonus', 0, 30, 15, 1),
        'reactive': st.sidebar.slider('Reactive bonus', 0, 30, 10, 1),
        'downtime': st.sidebar.slider('Downtime weight', 0.0, 2.0, 0.3, 0.1)
    }

    risk_increase_percent = st.sidebar.slider('Risk increase (%)', 0, 50, 0, 1)

    # Data
    assets = pd.DataFrame({
        'AssetID': [1001, 1002, 1003],
        'Site': ['North', 'South', 'East'],
        'AssetClass': ['HVAC', 'Electrical', 'Lift'],
        'Criticality': [5, 4, 3],
        'BaseRisk': [78.0, 55.0, 42.0]
    })

    work_orders = pd.DataFrame({
        'WorkOrderID': [5001, 5002, 5003],
        'AssetID': [1001, 1002, 1003],
        'Compliance': ['Yes', 'No', 'No'],
        'DowntimeHours': [24, 8, 6],
        'Reactive': ['Yes', 'No', 'No']
    })

    data = work_orders.merge(assets, on='AssetID')
    data['Risk'] = data['BaseRisk'] * (1 + risk_increase_percent / 100)

    # Calculate scores
    scores = data.apply(lambda r: calculate_priority(r, weights), axis=1)
    data['PriorityScore'] = scores.apply(lambda x: x[0])
    data['Components'] = scores.apply(lambda x: x[1])

    ranked = data.sort_values('PriorityScore', ascending=False)

    st.subheader("Ranked Work Orders")
    st.dataframe(ranked.drop(columns=['Components']))

    # -------- Charts --------
    st.subheader("Priority Breakdown")

    top = ranked.iloc[0]
    comp = top['Components']

    fig, ax = plt.subplots()
    ax.bar(comp.keys(), comp.values())
    ax.set_ylabel('Score Contribution')
    ax.set_title(f"Work Order {int(top['WorkOrderID'])} – Breakdown")
    st.pyplot(fig)

    # -------- Explainability --------
    st.subheader("Explainability per Work Order")

    for _, row in ranked.iterrows():
        with st.expander(f"Work Order {int(row['WorkOrderID'])} – Why this priority?"):
            for k, v in row['Components'].items():
                st.write(f"**{k}:** {round(v,2)}")
            st.write(f"**Total Priority Score:** {row['PriorityScore']}")

    st.markdown("---")
    st.markdown("**Why this matters:** Transparent, tunable, auditable prioritisation for facilities operations.")


if __name__ == '__main__':
    main()
