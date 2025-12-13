import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Market Intelligence", layout="wide")

# --- DATA LOADING FUNCTIONS ---
def load_models_data():
    file_path = 'data/models.json'

    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return None, None

    with open(file_path, 'r') as f:
        data = json.load(f)

    models_list = []
    feature_matrix = []

    for m in data['models']:
        features = m.get('features', {})

        # Extract all feature flags
        has_vision = features.get('vision', False)
        has_streaming = features.get('streaming', False)
        has_reasoning = features.get('reasoning', False)
        has_dynamic_thinking = features.get('dynamic_thinking', False)
        has_deep_think = features.get('deep_think_mode', False)
        has_ultra_context = features.get('ultra_large_context', False)

        features_count = sum([
            has_vision,
            has_streaming,
            has_reasoning,
            has_dynamic_thinking,
            has_deep_think,
            has_ultra_context
        ])

        avg_price = (m['pricing']['input_per_1m_tokens'] + m['pricing']['output_per_1m_tokens']) / 2

        models_list.append({
            "Name": m['name'],
            "Provider": m['provider'],
            "Release Date": pd.to_datetime(m['release_date']),
            "Context Window": m['features']['context_window'],
            "Input Price ($/1M)": m['pricing']['input_per_1m_tokens'],
            "Output Price ($/1M)": m['pricing']['output_per_1m_tokens'],
            "Avg Price ($/1M)": avg_price,
            "Speed": m['performance']['speed_tier'],
            "Features Count": features_count
        })

        feature_matrix.append({
            "Model": m['name'],
            "Provider": m['provider'],
            "Vision": "✓" if has_vision else "",
            "Streaming": "✓" if has_streaming else "",
            "Reasoning": "✓" if has_reasoning else "",
            "Dynamic Thinking": "✓" if has_dynamic_thinking else "",
            "Deep Think": "✓" if has_deep_think else "",
            "Ultra Context": "✓" if has_ultra_context else "",
            "Total Features": features_count
        })

    return pd.DataFrame(models_list), pd.DataFrame(feature_matrix)

def load_providers_data():
    file_path = 'data/providers.json'

    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return None

    with open(file_path, 'r') as f:
        data = json.load(f)

    return data['providers']

# --- DASHBOARD HEADER ---
st.title("🤖 AI Market Intelligence Dashboard")

# Button to trigger a re-load of the data
if st.button('🔄 Refresh Data'):
    st.rerun()

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Model Overview", "🌳 Frontier Family Tree"])

# ===== TAB 1: MODEL OVERVIEW =====
with tab1:
    st.markdown("### Feature-to-Cost Analysis")

    df, feature_df = load_models_data()

    if df is not None:
        df['Features per $ (Avg)'] = df['Features Count'] / df['Avg Price ($/1M)']

        # Top Row Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Models Tracked", len(df))
        col2.metric("Input Price Range (per 1M tokens)", f"${df['Input Price ($/1M)'].min():.2f} - ${df['Input Price ($/1M)'].max():.2f}")
        col3.metric("Largest Context Window", f"{df['Context Window'].max():,} tokens")

        st.divider()

        # Feature-to-Cost Bar Chart
        st.subheader("🎯 Feature-to-Cost Ratio")
        st.caption("Higher bars = More features per dollar spent. Best bang for your buck.")

        df_sorted = df.sort_values("Features per $ (Avg)", ascending=True)

        # Add a formatted ratio score column for tooltip display
        df_sorted['Ratio Score'] = df_sorted['Features per $ (Avg)'].round(2)
        df_sorted['Calculation Note'] = 'Formula: (Feature Count / Price) normalized'

        fig_feature_cost = px.bar(
            df_sorted,
            y="Name",
            x="Features per $ (Avg)",
            color="Provider",
            orientation='h',
            title="Models Ranked by Features per Dollar",
            labels={"Features per $ (Avg)": "Value Score (Features per $1)"},
            hover_data={
                "Name": True,
                "Provider": True,
                "Ratio Score": ':.2f',
                "Features Count": True,
                "Avg Price ($/1M)": ':.2f',
                "Features per $ (Avg)": False,  # Hide the raw column
                "Calculation Note": True
            }
        )
        fig_feature_cost.update_layout(height=500)

        # Customize hover template for better formatting
        fig_feature_cost.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                         'Provider: %{customdata[0]}<br>' +
                         'Ratio Score: %{customdata[1]:.2f}<br>' +
                         'Features: %{customdata[2]}<br>' +
                         'Avg Price: $%{customdata[3]:.2f}/1M tokens<br>' +
                         '<i>Formula: (Feature Count / Price) normalized</i>' +
                         '<extra></extra>'
        )

        st.plotly_chart(fig_feature_cost, width='stretch')

        st.divider()

        # Feature Availability Matrix
        st.subheader("🗺️ Feature Availability Matrix")
        st.caption("Quick reference for which models support which capabilities")

        feature_cols = ["Vision", "Streaming", "Reasoning", "Dynamic Thinking", "Deep Think", "Ultra Context"]
        feature_df_numeric = feature_df.copy()
        for col in feature_cols:
            feature_df_numeric[col + '_num'] = feature_df_numeric[col].apply(lambda x: 1 if x == "✓" else 0)

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=feature_df_numeric[[col + '_num' for col in feature_cols]].values,
            x=feature_cols,
            y=feature_df['Model'],
            colorscale=[[0, '#f0f0f0'], [1, '#1f77b4']],
            showscale=False,
            hovertemplate='<b>%{y}</b><br>%{x}: %{z}<extra></extra>',
            text=feature_df[feature_cols].values,
            texttemplate='%{text}',
            textfont={"size": 14}
        ))

        fig_heatmap.update_layout(
            title="Feature Support by Model",
            xaxis_title="Features",
            yaxis_title="Model",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_heatmap, width='stretch')

        st.divider()

        # Detailed Comparison Table
        st.subheader("📊 Detailed Model Comparison")

        comparison_df = df[["Name", "Provider", "Features Count", "Avg Price ($/1M)",
                            "Features per $ (Avg)", "Context Window", "Speed"]].copy()
        comparison_df = comparison_df.sort_values("Features per $ (Avg)", ascending=False)
        comparison_df["Features per $ (Avg)"] = comparison_df["Features per $ (Avg)"].round(2)
        comparison_df["Avg Price ($/1M)"] = comparison_df["Avg Price ($/1M)"].apply(lambda x: f"${x:.2f}")
        comparison_df["Context Window"] = comparison_df["Context Window"].apply(lambda x: f"{x:,}")

        st.dataframe(comparison_df, hide_index=True, use_container_width=True)

        # Feature Details Table
        with st.expander("🔍 View Feature Details by Model"):
            st.dataframe(feature_df.sort_values("Total Features", ascending=False), hide_index=True, use_container_width=True)

    else:
        st.warning("Please ensure 'data/models.json' exists in the project directory.")

# ===== TAB 2: FRONTIER FAMILY TREE =====
with tab2:
    st.markdown("### Explore AI Provider Ecosystems")
    st.caption("Click on a provider to explore their full product suite and capabilities")

    # Inject custom CSS for provider cards
    st.markdown("""
    <style>
    /* Provider card styling */
    .provider-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        background: white;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .provider-card:hover {
        border-color: #4285F4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    .provider-logo {
        width: 50px;
        height: 50px;
        margin: 0 auto 12px auto;
        border-radius: 8px;
        object-fit: contain;
    }

    .provider-name {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #1f1f1f;
    }

    .provider-description {
        font-size: 13px;
        color: #666;
        line-height: 1.4;
        overflow-y: auto;
        max-height: 80px;
        padding: 0 4px;
        text-align: left;
    }

    /* Custom scrollbar for description */
    .provider-description::-webkit-scrollbar {
        width: 4px;
    }

    .provider-description::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 4px;
    }

    /* Ensure button styling doesn't interfere */
    div[data-testid="column"] > div > div > button {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    providers = load_providers_data()

    if providers:
        # Initialize session state for selected provider
        if 'selected_provider' not in st.session_state:
            st.session_state.selected_provider = None

        # Provider Cards Grid
        st.subheader("Select a Provider")
        cols = st.columns(5)

        provider_colors = {
            "Anthropic": "#D4A574",
            "OpenAI": "#10A37F",
            "Google (DeepMind)": "#4285F4",
            "xAI": "#000000",
            "DeepSeek": "#FF6B6B"
        }

        # Logo mapping (placeholder URLs - replace with actual logo paths)
        provider_logos = {
            "Anthropic": "https://placehold.co/50x50/D4A574/white?text=A",
            "OpenAI": "https://placehold.co/50x50/10A37F/white?text=O",
            "Google (DeepMind)": "https://placehold.co/50x50/4285F4/white?text=G",
            "xAI": "https://placehold.co/50x50/000000/white?text=X",
            "DeepSeek": "https://placehold.co/50x50/FF6B6B/white?text=D"
        }

        for idx, provider in enumerate(providers):
            with cols[idx]:
                # Create a clickable card container
                logo_url = provider_logos.get(provider['name'], "https://placehold.co/50x50/gray/white?text=?")
                border_color = provider_colors.get(provider['name'], "#e0e0e0")

                # Use a container with custom styling
                with st.container():
                    # Card content as HTML
                    card_html = f"""
                    <div class="provider-card" style="border-color: {border_color};">
                        <div>
                            <img src="{logo_url}" class="provider-logo" alt="{provider['name']} logo">
                            <div class="provider-name">{provider['name']}</div>
                        </div>
                        <div class="provider-description" title="{provider['description']}">{provider['description']}</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Clickable button below the card
                    if st.button(
                        f"View {provider['name']}",
                        key=f"provider_{provider['id']}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.selected_provider = provider['id']

        st.divider()

        # Display selected provider details
        if st.session_state.selected_provider:
            selected = next((p for p in providers if p['id'] == st.session_state.selected_provider), None)

            if selected:
                # Provider Header
                st.markdown(f"## {selected['name']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Founded", selected['founded'])
                col2.metric("Headquarters", selected['headquarters'])
                col3.metric("Product Categories",
                           len(selected['product_families']['llm_models']) +
                           len(selected['product_families']['specialized_products']))

                st.markdown(f"*{selected['description']}*")
                st.divider()

                # Product Family Tree
                st.subheader("🌲 Product Family")

                prod_col1, prod_col2 = st.columns(2)

                with prod_col1:
                    st.markdown("#### 🧠 LLM Models")
                    for model in selected['product_families']['llm_models']:
                        with st.container():
                            st.markdown(f"**{model['name']}** *({model['type']})*")
                            st.caption(model['description'])
                            st.markdown("")

                with prod_col2:
                    st.markdown("#### ⚡ Specialized Products")
                    if selected['product_families']['specialized_products']:
                        for product in selected['product_families']['specialized_products']:
                            with st.container():
                                st.markdown(f"**{product['name']}** *({product['type']})*")
                                st.caption(product['description'])
                                st.markdown("")
                    else:
                        st.info("No specialized products available")

                st.divider()

                # Capabilities Matrix
                st.subheader("🎯 Full Capability Breakdown")

                # Get all models from this provider
                all_models = selected['product_families']['llm_models'] + selected['product_families']['specialized_products']
                model_names = [model['name'] for model in all_models]

                # Build capability matrix with models as columns
                cap_matrix = {}
                cap_matrix['Capability'] = []

                # Initialize columns for each model
                for model_name in model_names:
                    cap_matrix[model_name] = []

                # Fill in the matrix
                for cap_name, cap_info in selected['capabilities'].items():
                    cap_label = cap_name.replace('_', ' ').title()
                    cap_matrix['Capability'].append(cap_label)

                    # For each model, check if it supports this capability
                    for model_name in model_names:
                        if model_name in cap_info['products']:
                            cap_matrix[model_name].append("✅")
                        else:
                            cap_matrix[model_name].append("❌")

                cap_df = pd.DataFrame(cap_matrix)
                st.dataframe(cap_df, hide_index=True, use_container_width=True)

                # Capability Summary
                st.divider()
                st.subheader("📈 Capability Summary")

                total_caps = len(selected['capabilities'])
                available_caps = sum(1 for cap in selected['capabilities'].values() if cap['available'])

                col1, col2 = st.columns(2)
                col1.metric("Total Capabilities", total_caps)
                col2.metric("Available Capabilities", f"{available_caps} ({available_caps/total_caps*100:.0f}%)")

                # Capability radar chart
                cap_names = []
                cap_values = []
                for cap_name, cap_info in selected['capabilities'].items():
                    cap_names.append(cap_name.replace('_', ' ').title())
                    cap_values.append(1 if cap_info['available'] else 0)

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=cap_values,
                    theta=cap_names,
                    fill='toself',
                    name=selected['name']
                ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 1])
                    ),
                    showlegend=False,
                    title=f"{selected['name']} Capability Coverage"
                )

                st.plotly_chart(fig_radar, width='stretch')

        else:
            st.info("👆 Select a provider above to explore their ecosystem")

    else:
        st.warning("Please ensure 'data/providers.json' exists in the project directory.")
