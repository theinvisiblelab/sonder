import numpy as np
import pandas as pd
import random
import altair as alt
import rpy2.robjects as ro
from rpy2.robjects.packages import importr

overlapping = importr("overlapping")
random.seed(10)

# Calculate distribution overlap
def overlap_calc(df, i):
    if i <= n_top[0]:
        return 0
    else:
        df = df[df["sentiment"].notna()]
        v1 = ro.vectors.FloatVector(df["sentiment"])
        v2 = ro.vectors.FloatVector(df.iloc[n_top[0] : i + 1]["sentiment"])
        # st.write(i)
        ovl = overlapping.overlap([v1, v2])
        return np.array(ovl.rx("OV"))[0][0]


st.write("## 🚲 demo")
st.write("&nbsp;")

with st.expander("Equations"):
    st.latex(
        r"""
    V_{q,d} =\int_{R_n, q} min\left[ f_n(d), f_N(d)\right] \,\mathrm{d}d"""
    )
    st.latex(
        r"""
    E_{q,d} = \int_{n=1}^{N} \int_{R_n, q} min\left[ f_n(d), f_N(d)\right] \,\mathrm{d}d \,\mathrm{d}n = \int_{n=1}^{N} V_{q,d} \mathrm{d}n"""
    )

case = st.radio(
    "Choose case",
    ["Random Results", "Polarized Results"],
    0,
)

if case == "Polarized Results":
    # case 1 (extreme)
    df_1 = pd.DataFrame(
        [random.random() - 1 for i in range(100)],
        columns=["sentiment"],
    )
    df_2 = pd.DataFrame(
        [random.random() for i in range(100)],
        columns=["sentiment"],
    )
    df = pd.concat([df_1, df_2])
elif case == "Random Results":
    # case 2 (random)
    df = pd.DataFrame(
        [(random.random() * 2) - 1 for i in range(200)],
        columns=["sentiment"],
    )

# rank and size
df["rank"] = df.reset_index().index + 1
df_size = len(df)

n_top = st.slider("Results viewed", 0, df_size, (0, 0))
col1, col2 = st.columns(2)

with col1:
    plot_corr = (
        alt.Chart(df[df["sentiment"].notna()])
        .mark_circle(size=150, opacity=0.8)
        .encode(
            x=alt.X(
                "rank:Q",
                title="Search results viewed",
            ),
            y=alt.Y("sentiment:Q", title="Sentiment"),
            # tooltip=["title"],
            color=alt.condition(
                alt.datum.sentiment >= 0,
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    )
    rule_corr = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(strokeDash=[10, 10], size=1.5)
        .encode(y="y")
    )

    cutoff = pd.DataFrame({"start": [n_top[1], n_top[1]], "stop": [df_size, df_size]})
    areas = (
        alt.Chart(cutoff.reset_index())
        .mark_rect(opacity=0.30)
        .encode(x="start", x2="stop")
    )

    cutoff0 = pd.DataFrame({"start": [0, 0], "stop": [n_top[0], n_top[0]]})
    areas0 = (
        alt.Chart(cutoff0.reset_index())
        .mark_rect(opacity=0.30)
        .encode(x="start", x2="stop")
    )

    st.altair_chart(rule_corr + plot_corr + areas + areas0, use_container_width=True)

    df_inv = pd.DataFrame(
        [(i, overlap_calc(df, i)) for i in range(n_top[0], n_top[1] + 1)],
        columns=["rank", "visibility"],
    )

    vis_present = round(df_inv["visibility"].iloc[-1] * 100, 2)
    if n_top[1] == 200:
        effic_present = round(df_inv["visibility"].mean() * 100, 2)
    else:
        effic_present = "--"

    # df_inv["rank"] = df_inv["rank"] / df_size
    if n_top[1] == 200:
        plot_vis_continuous = (
            alt.Chart(df_inv)
            .mark_area(color="#ffd875", line=True, opacity=0.75)
            .encode(
                x=alt.X(
                    "rank:Q",
                    title="Search results viewed",
                    scale=alt.Scale(domain=(0, df_size)),
                ),
                y=alt.Y(
                    "visibility:Q",
                    title="Visibility",
                    axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=(0, 1)),
                ),
                tooltip=["visibility"],
            )
        )
    else:
        plot_vis_continuous = (
            alt.Chart(df_inv)
            .mark_area(color="#ffd875", line=True, opacity=0)
            .encode(
                x=alt.X(
                    "rank:Q",
                    title="Search results viewed",
                    scale=alt.Scale(domain=(0, df_size)),
                ),
                y=alt.Y(
                    "visibility:Q",
                    title="Visibility",
                    axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=(0, 1)),
                ),
                tooltip=["visibility"],
            )
        )

    st.altair_chart(plot_vis_continuous, use_container_width=True)


with col2:
    df_plot1 = df[df["sentiment"].notna()]
    df_plot1["Source"] = "All indexed results"

    df_plot2 = df[df["sentiment"].notna()].iloc[n_top[0] : n_top[1]]
    df_plot2["Source"] = "Results " + str(n_top[0]) + "-" + str(n_top[1])

    df_plot = pd.concat([df_plot1, df_plot2], ignore_index=True)

    # st.write(df_plot)
    plot_dist_all = (
        alt.Chart(df_plot)
        .transform_density(
            "sentiment",
            groupby=["Source"],
            as_=["sentiment", "density"],
            extent=[-1, 1],
        )
        .mark_area(opacity=0.75)
        .encode(
            x=alt.X("sentiment:Q", title="Sentiment"),
            y=alt.Y("density:Q", title="Density"),
            tooltip=["sentiment"],
            color=alt.Color("Source:N"),
        )
    )
    st.altair_chart(plot_dist_all, use_container_width=True)

    st.metric(label="Visibility", value=str(vis_present) + "%")
    st.metric(label="Efficiency", value=str(effic_present) + "%")
