## PARAMETERS ##
import requests
import io
import yaml
import socket
import numpy as np
import pandas as pd
import scipy
from statistics import mean, median
from nltk import tokenize

# from scipy.stats import ks_2samp
import rpy2.robjects as ro
from rpy2.robjects.packages import importr

overlapping = importr("overlapping")

from textblob import TextBlob
import geoip2.database
import folium
from streamlit_folium import folium_static
import altair as alt

from transformers import pipeline

# The url below can be replaced with 'http://localhost/8888/search' if searx is locally setup.
# See https://searx.github.io/searx/admin/installation.html for more details.
url = "http://searx.sonder.care/search"


@st.cache(allow_output_mutation=True, show_spinner=False)
def load_searx_data(query):
    df = []
    results = 0
    # search the first 5 pages
    for page in range(1, 6):
        querystring = {
            "q": query,
            "categories": "general",
            "engines": ["google", "bing", "duckduckgo"],
            "pageno": page,
            "format": "json",
        }
        response = requests.request("GET", url, params=querystring)
        text = yaml.safe_load(response.text)
        df_mini = pd.DataFrame(text["results"])
        df.append(df_mini)
        # keeping at least 30 results
        results += len(df_mini)
        if results >= 30:
            break
    df = pd.concat(df)
    df = df.sort_values(by=["score"], ascending=False)
    if "title" in df.columns:
        df["title"] = df["title"].str.encode("utf-8", "ignore").str.decode("utf-8")
    if "content" in df.columns:
        df["content"] = df["content"].str.encode("utf-8", "ignore").str.decode("utf-8")
    df.drop_duplicates(subset="url", inplace=True)
    return df


def subjectivity_calc(text):
    try:
        return TextBlob(text).sentiment.subjectivity
    except:
        return None


def sentiment_calc(text):
    try:
        if subjectivity_calc(text) == 0:
            return 0
        else:
            result = classifier(text)[0]
            if result["label"] == "POSITIVE":
                return round(result["score"], 4)
            elif result["label"] == "NEGATIVE":
                return -result["score"]
            else:
                return 0
    except:
        return None


@st.cache(allow_output_mutation=True, show_spinner=False)
def sentiment_all(text):
    try:
        sent_list = []
        for sent in tokenize.sent_tokenize(text):
            sent_list.append(sentiment_calc(sent))
        return mean(sent_list)
    except:
        return None


def get_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None


# You can get your own free maxmind geoip key and GeoLite2-City database if deploying your own sonder servers
# Check https://dev.maxmind.com/geoip/geoip2/geolite2/ for more details.
def map_result(ip_address):
    try:
        with geoip2.database.Reader(Path("geoip/GeoLite2-City.mmdb")) as reader:
            response = reader.city(ip_address)
            return (
                response.country.iso_code,
                response.location.latitude,
                response.location.longitude,
                response.city.name,
                response.country.name,
            )
    except:
        return None


# Calculate RMAD coefficient
def rmad(x):
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # RMAD (Relative mean absolute difference)
    rmad = mad / np.mean(x)
    # Scaling
    return 0.5 * rmad


# Calculate distribution overlap
def overlap_calc(df, n_top=10):
    v1 = ro.vectors.FloatVector(df[df["sentiment"].notna()]["sentiment"])
    v2 = ro.vectors.FloatVector(df[df["sentiment"].notna()].head(n_top)["sentiment"])
    ovl = overlapping.overlap([v1, v2])
    return np.array(ovl.rx("OV"))[0][0]


## CONTENT ##

# st.markdown(Path("markdown/bias.md").read_text(), unsafe_allow_html=True)
with st.beta_expander("🎈 Why Sonder?"):
    st.info(
        """
    *son$\cdot$der (n.)*

    the realization that each random passerby is living a life as vivid and complex as your own
    """
    )
    st.markdown(
        """
    Internet search shows you what you consume. Sonder shows you what you miss out on. We assess the opportunity cost of internet search.

    Our access to knowledge is biased by ~~public~~ private algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~understanding~~ consumption. This robs us of the choice to understand those who think and learn differently. Sonder is an attempt to make our lack of choice explicit. To at least be mindful of our filter bubbles, if not break them.

    We are working along two dimensions (view 👈 sidebar):

    + ⚖️ *Balance*: Tackle bias as you search the web. Balance relevance with diversity.
    + 📣 *Trends*: Highlight fairness in web, news, wiki, and social media trends.

    &nbsp;
    """
    )

st.markdown("## ⚖️ Balance")
st.write("Evaluate what you _miss_ as you search the web.")

st.markdown("&nbsp;")

query = st.text_input("Seek fairer human knowledge...").lower().strip()

st.markdown("&nbsp;")

if query != "":

    col2, col1 = st.beta_columns(2)

    with st.spinner("Assessing latent knowledge in your search..."):
        df = load_searx_data(query)
        df["search_rank"] = df.reset_index().index + 1
        df_size = len(df.index)
        green_list = pd.read_csv(Path("green/greendomain.txt"))["url"].tolist()

    with col1:
        st.markdown("### Search results")
        st.markdown("---")
        # st.markdown("\n\n")
        # presently printing out top 20 search results
        for index, row in df.iterrows():
            with st.beta_container():
                # st.write("Sentiment: ", row["sentiment"])
                # st.write("Host Country: `", row["country_name"], "`")
                if row["content"] == row["content"]:
                    st.markdown(
                        "> "
                        + row["url"]
                        + "<br/><br/><i>"
                        + row["title"]
                        + ".</i> "
                        + row["content"],
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "> " + row["url"] + "<br/><br/>" + row["title"],
                        unsafe_allow_html=True,
                    )
                st.markdown("---")

    col2.markdown("### Representation in search results")
    col2.markdown("---")
    summary_chart = col2.empty()

    expander1 = col2.beta_expander("🗣️ Sentiment")
    expander2 = col2.beta_expander("🌍 Geographies")
    expander3 = col2.beta_expander("🔥 Carbon Cost")

    with expander1:
        with st.spinner("Assessing sentiment in your search results..."):
            # sentiment analyzer loading
            classifier = pipeline("sentiment-analysis")
            df["sentiment"] = df.apply(
                lambda row: sentiment_all(
                    str(row["title"]) + ". " + str(row["content"])
                ),
                axis=1,
            )

            # df["subjectivity"] = df.apply(lambda row: subjectivity_calc(str(row["title"])), axis=1)
            # st.write(df[["title", "content", "subjectivity", "sentiment"]])

            sentiment_mean = round(df["sentiment"].mean(), 4)
            sentiment_median = round(df["sentiment"].median(), 4)
            sentiment_min = df["sentiment"].min()
            sentiment_max = df["sentiment"].max()

            # correlation = 1 - abs(df["search_rank"].corr(df["sentiment"]))

            sentiment_bias = round(((1 - overlap_calc(df)) * 100), 2)
            n_top = 10  # number of top results

            st.error("Invisibility: __" + str(sentiment_bias) + "%__")
            st.write("\n")

            st.write(
                "Here's how sentiment varies with rank for all your search results. You miss out on the blue region."
            )

            plot_corr = (
                alt.Chart(df[df["sentiment"].notna()])
                .mark_circle(size=300, opacity=0.8)
                .encode(
                    x=alt.X("search_rank:Q", title="Search result rank"),
                    y=alt.Y("sentiment:Q", title="Sentiment"),
                    tooltip=["title", "search_rank", "sentiment"],
                    color=alt.condition(
                        alt.datum.sentiment >= 0,
                        alt.value("#0ec956"),  # The positive color
                        alt.value("#ff1717"),  # The negative color
                    ),
                )
                .properties(height=450)
            )
            rule_corr = (
                alt.Chart(pd.DataFrame({"y": [0]}))
                .mark_rule(strokeDash=[10, 10], size=1.5)
                .encode(y="y")
            )

            cutoff = pd.DataFrame({"start": [10, 10], "stop": [df_size, df_size]})

            areas = (
                alt.Chart(cutoff.reset_index())
                .mark_rect(opacity=0.2)
                .encode(x="start", x2="stop")
            )

            st.altair_chart(areas + rule_corr + plot_corr, use_container_width=True)

            st.write("\n")
            st.write(
                "Your first page of search results misses out on "
                + str(sentiment_bias)
                + "% of the population sentiment (blue regions in the chart below)."
            )
            st.write("\n")

            df_plot1 = df[df["sentiment"].notna()]
            df_plot1["Source"] = "All results"

            df_plot2 = df[df["sentiment"].notna()].head(n_top)
            df_plot2["Source"] = "Top " + str(n_top) + " results"

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
                .properties(height=450)
            )

            st.altair_chart(plot_dist_all, use_container_width=True)
            st.markdown("\n")

            st.markdown("&nbsp;")

    with expander2:
        with st.spinner("Geolocating your search results..."):
            df["domain"] = df.apply(lambda row: row["parsed_url"][1], axis=1)
            df["ip_address"] = df.apply(lambda row: get_ip(row["domain"]), axis=1)
            df = df[df["ip_address"].notnull()]
            df["map_result_tuple"] = df.apply(
                lambda row: map_result(row["ip_address"]), axis=1
            )
            df = df[df["map_result_tuple"].notnull()]
            df["country"] = df.apply(lambda row: row["map_result_tuple"][0], axis=1)
            df["latitude"] = df.apply(lambda row: row["map_result_tuple"][1], axis=1)
            df["longitude"] = df.apply(lambda row: row["map_result_tuple"][2], axis=1)
            df["city"] = df.apply(lambda row: row["map_result_tuple"][3], axis=1)
            df["country_name"] = df.apply(
                lambda row: row["map_result_tuple"][4], axis=1
            )
            df["cctld"] = df.apply(lambda row: row["domain"].split(".")[-1], axis=1)

            # correcting locations based on cctld
            df = pd.merge(
                df,
                pd.read_csv(Path("cctld/capitals.csv")),
                on="cctld",
                how="left",
            )
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "latitude",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "cap_lat",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "longitude",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "cap_long",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "city",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "capital",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "country_name",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "country_cctld",
            ]

            df_prop1 = (
                df.groupby("country_name")
                .count()[["url"]]
                .reset_index()
                .rename(columns={"url": "total_all"})
            )
            df_prop1["prop_all"] = df_prop1["total_all"] / df_prop1["total_all"].sum()

            df_prop2 = (
                df.head(n_top)
                .groupby("country_name")
                .count()[["url"]]
                .reset_index()
                .rename(columns={"url": "total_top"})
            )
            df_prop2["prop_top"] = df_prop2["total_top"] / df_prop2["total_top"].sum()

            df_prop = df_prop1.merge(df_prop2, on="country_name", how="left")
            df_prop["total_top"] = df_prop["total_top"].fillna(0)
            df_prop["prop_top"] = df_prop["prop_top"].fillna(0)
            df_prop["diff"] = (
                np.sqrt(
                    (df_prop["prop_all"] - df_prop["prop_top"])
                    / (1 - (n_top / df_size))
                )
                * 100
            )
            df_prop.loc[(df_prop["diff"] < 0), "diff"] = 0
            df_prop["diff"].fillna(0, inplace=True)
            # st.write(df_prop)
            if len(df_prop) > 1:
                spatial_bias_full = round(df_prop["diff"].sum() / (len(df_prop) - 1), 2)
            else:
                spatial_bias_full = 0

            df_prop = (
                df_prop[["country_name", "total_all", "total_top", "diff"]]
                .sort_values(by=["diff"], ascending=False)
                .reset_index(drop=True)
            )

            df_prop["diff"] = df_prop["diff"].round(2).astype(str) + "%"
            df_prop.columns = [
                "Country",
                "Total Results",
                "First Page Results",
                "Invisibility",
            ]

            countries = ", ".join(sorted(df["country_name"].unique()))

            # Replace sonder_host_country with appropriate value if your Sonder server is hosted in another country
            # sonder_host_country = "United States"
            # spatial_bias_adjusted = round(
            #     rmad(
            #         df_tabulated[
            #             df_tabulated["country_name"] != sonder_host_country
            #         ][["spatial_score"]].values
            #     )
            #     * 100,
            #     2,
            # )
            st.error("Invisibility: __" + str(spatial_bias_full) + "%__")

            st.write("\n")
            st.write(
                "Your first page of search results misses out on "
                + str(spatial_bias_full)
                + "% geographic diversity. Here is a country-wise breakdown:"
            )

            st.write("\n")
            st.table(df_prop.assign(hack="").set_index("hack"))

            st.write("\n")
            st.write("Zoom in below to see where your results are hosted.")
            st.write("\n")
            map = folium.Map(location=[0, 0], zoom_start=1.49, tiles="cartodb positron")
            for i in range(0, len(df)):
                folium.Marker(
                    location=[df.iloc[i]["latitude"], df.iloc[i]["longitude"]],
                    tooltip="Search rank "
                    + str(df.iloc[i]["search_rank"])
                    + ": "
                    + str(df.iloc[i]["title"]),
                ).add_to(map)
            folium_static(map, width=620, height=500)

            st.markdown("&nbsp;")
            # IDEA: Add average rank per country plot.

    with expander3:
        df["domain"] = df.apply(lambda row: row["parsed_url"][1], axis=1)
        df["is_green"] = np.where(df["domain"].isin(green_list), "Green", "Red")

        green_prop_all = len(df[df["is_green"] == "Green"]) / len(df)
        green_prop_top = len(
            df.head(n_top)[df.head(n_top)["is_green"] == "Green"]
        ) / len(df.head(n_top))

        carbon_cost = round(
            np.sqrt(max((green_prop_all - green_prop_top) / (0.9), 0)) * 100, 2
        )
        green_prop_all = round(green_prop_all * 100, 2)
        green_prop_top = round(green_prop_top * 100, 2)

        st.error("Invisibility: __" + str(carbon_cost) + "%__")
        st.write("\n")
        st.write(
            str(green_prop_all)
            + "% of _all_ search results come from domains using renewable energy sources."
        )
        st.write("\n")

        df_eco = pd.DataFrame(
            [green_prop_all, 100 - green_prop_all],
            columns=["value"],
        )
        df_eco["Source"] = ["Renewable", "Non-renewable"]
        df_eco["Energy"] = ["Energy", "Energy"]  # dummy column for plot
        plot_eco = (
            alt.Chart(df_eco)
            .mark_bar(opacity=0.75)
            .encode(
                x=alt.X("sum(value)", title="All search results (%)"),
                y=alt.Y("Energy", title=""),
                tooltip=["value"],
                color=alt.Color(
                    "Source",
                    scale=alt.Scale(
                        domain=["Renewable", "Non-renewable"],
                        range=["#0ec956", "#ff1717"],
                    ),
                ),
            )
            .properties(
                height=125,
            )
            .configure_title(fontSize=18)
            .configure_axis(labelFontSize=15, titleFontSize=15)
        )
        st.altair_chart(plot_eco, use_container_width=True)

        st.write("\n")
        st.write(
            str(green_prop_top)
            + "% of _top_ search results come from domains using renewable energy sources."
        )
        st.write("\n")
        df_eco = pd.DataFrame(
            [green_prop_top, 100 - green_prop_top],
            columns=["value"],
        )
        df_eco["Source"] = ["Renewable", "Non-renewable"]
        df_eco["Energy"] = ["Energy", "Energy"]  # dummy column for plot
        plot_eco = (
            alt.Chart(df_eco)
            .mark_bar(opacity=0.75)
            .encode(
                x=alt.X("sum(value)", title="Top search results (%)"),
                y=alt.Y("Energy", title=""),
                tooltip=["value"],
                color=alt.Color(
                    "Source",
                    scale=alt.Scale(
                        domain=["Renewable", "Non-renewable"],
                        range=["#0ec956", "#ff1717"],
                    ),
                ),
            )
            .properties(
                height=125,
            )
            .configure_title(fontSize=18)
            .configure_axis(labelFontSize=15, titleFontSize=15)
        )
        st.altair_chart(plot_eco, use_container_width=True)

        st.markdown("&nbsp;")
        st.markdown("---")
        st.markdown(
            "<span style='color:gray'>_Details on metric calculation algorithms can be seen [here](https://github.com/sonder-labs/sonder#-algorithms)_</span>",
            unsafe_allow_html=True,
        )

    # Summary data frame
    df_summary = pd.DataFrame(
        [carbon_cost, spatial_bias_full, sentiment_bias],
        columns=["value"],
    )
    df_summary["label"] = [
        "Latent Carbon Cost",
        "Latent Geographies",
        "Latent Sentiment",
    ]

    plot_summary = (
        alt.Chart(df_summary)
        .mark_bar(cornerRadiusBottomRight=10, cornerRadiusTopRight=10, opacity=0.70)
        .encode(
            x=alt.X("value", title="Invisibility (%)"),
            y=alt.Y("label", title="", sort="-x"),
            tooltip=["value"],
            color=alt.condition(
                alt.datum.value < 50,
                alt.value("#ff8000"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
        .properties(
            height=300,
            title="Overview for " + str(df_size) + " search results",
        )
    )
    threshold_line = (
        alt.Chart(pd.DataFrame({"x": [50]}))
        .mark_rule(color="red", strokeDash=[10, 10], size=1.5)
        .encode(x="x")
    )
    summary_chart.altair_chart(
        alt.layer(plot_summary, threshold_line)
        .configure_title(fontSize=18)
        .configure_axis(labelFontSize=15, titleFontSize=15),
        use_container_width=True,
    )
    st.markdown("&nbsp;")

    st.markdown("&nbsp;")
    if st.button("Add more search results to analysis"):
        st.markdown("_STILL COOKING!_ :spaghetti:")
        st.markdown(
            "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
        )
