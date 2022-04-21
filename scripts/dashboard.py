import pandas as pd
import altair as alt
from vega_datasets import data

def draw_bar(df_summary):
    plot_summary = (
        alt.Chart(df_summary.head(10))
        .mark_bar(opacity=0.80)
        .encode(
            x=alt.X("Trust Score", title="Trust Score"),
            y=alt.Y("Website", title="", sort="x"),
            tooltip=["Trust Score"],
            color=alt.condition(
                        alt.datum["Trust Score"] < 50,
                        alt.value("#ff1717"),  # The negative color
                        alt.value("#ebb113"),  # The positive color
                    ),
        )
        .configure_title(fontSize=18)
        .configure_axis(labelFontSize=15, titleFontSize=15)
    ).interactive()
    st.altair_chart(plot_summary, use_container_width=True)


st.write("## 🎬 Dashboard")
st.write("&nbsp;")

counties = alt.topo_feature(data.us_10m.url, 'counties')
source = data.unemployment.url


df_full = pd.read_csv("/Users/saurabh/Everything/GitHub/sonder/data/misinformation_dashboard.csv")
df_full.rename(columns={'score': 'Trust Score'}, inplace=True)

#st.write(df_full.head())

df = df_full.groupby(['id'])['Trust Score'].mean().reset_index()
df['Trust Score'] = df['Trust Score'].round(2)
df["id"] = pd.to_numeric(df["id"])

us_map = alt.Chart(counties).mark_geoshape().encode(
    color=alt.Color('Trust Score:Q', legend=None),
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df, 'id', ['Trust Score'])
).encode(
 tooltip=[alt.Tooltip("id:N", title="County FIPS"), "Trust Score:Q"],
).project(
    type='albersUsa'
).properties(
    width=1200,
    height=600
).configure_mark(
    strokeOpacity=0,
    strokeWidth=0,
  )

st.write("## Nationwide Trust Scores")
st.write("_Updated: 04-21-2022_")
st.write("&nbsp;")

st.altair_chart(us_map, use_container_width=True)

county_list = sorted(list(set(df_full["county"].tolist())))
county_list.insert(0, "")

st.write("&nbsp;")

st.write("## County-level Statistics")
st.write("&nbsp;")

county = st.selectbox("Choose a county", county_list)
if county != "":
    df_temp = df_full[df_full["county"] == county].sort_values(by=["Trust Score"])

    df_temp = df_temp[df_temp["Trust Score"] > 0]
    df_temp = df_temp[df_temp["Trust Score"] < 100]
    df_temp.rename(columns={'domain': 'Website'}, inplace=True)

    col_a, col_b = st.columns([1.618, 1])
    
    with col_a:
        st.write("### Low Trust Sites")
        draw_bar(df_temp[['Website', 'Trust Score']])

    with col_b:
        st.write("### Overall Trust Score")
        st.metric(label="", value = str(round(df_temp['Trust Score'].mean(), 2)) + "/100")