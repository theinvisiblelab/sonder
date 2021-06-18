## PARAMETERS ##
import requests
import io
import yaml
import socket
import numpy as np
import pandas as pd
import scipy

from textblob import TextBlob
import geoip2.database
import folium
from streamlit_folium import folium_static
import altair as alt
# from transformers import pipeline

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
    return df


def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return None

# @st.cache(allow_output_mutation=True, show_spinner=False)
# def sentiment_calc(text):
#     try:
#         result = classifier(text)[0]
#         if result["label"] == "POSITIVE":
#             return result["score"]
#         elif result["label"] == "NEGATIVE":
#             return -result["score"]
#         else:
#             return 0
#     except:
#         return None


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


# @st.cache(allow_output_mutation=True, show_spinner=False)
# def load_lang_data(query):
#     count_list = []
#     for lang in language_codes:
#         querystring = {
#             "q": query,
#             "categories": "general",
#             "engines": ["google"],
#             "format": "json",
#             "language": lang[0],
#         }
#         response = requests.request("GET", url, params=querystring)
#         text = yaml.safe_load(response.text)
#         count = int(text["number_of_results"])
#         count_list.append((lang[3], count))
#     return count_list


# Calculate RMAD coefficient
def rmad(x):
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # RMAD (Relative mean absolute difference)
    rmad = mad / np.mean(x)
    # Scaling
    return 0.5 * rmad


# Language codes
# language_codes = (
#     ("ar-EG", "العربية", "", "Arabic"),
#     ("de", "Deutsch", "", "German"),
#     ("en", "English", "", "English"),
#     ("es", "Español", "", "Spanish"),
#     ("fr", "Français", "", "French"),
#     ("id-ID", "Indonesia", "", "Indonesian"),
#     ("ja-JP", "日本語", "", "Japanese"),
#     ("pt", "Português", "", "Portuguese"),
#     ("ru-RU", "Русский", "", "Russian"),
#     ("zh", "中文", "", "Chinese"),
# )

## CONTENT ##

# st.markdown(Path("markdown/bias.md").read_text(), unsafe_allow_html=True)

st.markdown("## ⚖️ Balance")
st.write("Evaluate representation as you search the web.")

st.markdown("&nbsp;")

query = st.text_input("Seek fairer human knowledge...").lower().strip()

st.markdown("&nbsp;")

if query != "":
    search_type = st.radio(
        "", ["Balanced results [🚧 Under development]", "Unbalanced results"], 1
    )

    if search_type == "Balanced results [🚧 Under development]":
        st.markdown("&nbsp;")
        st.markdown("&nbsp;")
        st.markdown("_STILL COOKING!_ :spaghetti:")
        st.markdown(
            "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
        )

    col2, col1 = st.beta_columns(2)

    if search_type == "Unbalanced results":

        with st.spinner("Assessing representation in your search..."):
            df = load_searx_data(query)
            df["search_rank"] = df.reset_index().index + 1
            df_size = len(df.index)
            green_list = pd.read_csv(Path("green/greendomain.txt"))["url"].tolist()
            # sentiment analyzer loading
            # classifier = pipeline("sentiment-analysis")

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
                            + "<br/><br/>"
                            + row["title"]
                            + ". "
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

        expander1 = col2.beta_expander(
            "🗣️ Sentiment Representation: Do I see more positive (or more negative) sentiment in my results?"
        )
        expander2 = col2.beta_expander(
            "🌍 Spatial Representation: Are my results hosted in geographically diverse locations?"
        )
        expander3 = col2.beta_expander(
            "🔥 Eco-friendliness: Are my results coming from eco-friendly domains?"
        )

        with expander1:
            with st.spinner("Assessing sentiment in your search results..."):

                df["pol_title"] = df.apply(
                    lambda row: sentiment_calc(row["title"]), axis=1
                )
                df["pol_content"] = df.apply(
                    lambda row: sentiment_calc(row["content"]), axis=1
                )
                df["sentiment"] = ((2 * df["pol_title"]) + df["pol_content"]) / 3
                df["sentiment"] = df["sentiment"].apply(lambda x: round(x, 4))
                sentiment_mean = round(df["sentiment"].mean(), 4)
                sentiment_median = round(df["sentiment"].median(), 4)
                sentiment_min = df["sentiment"].min()
                sentiment_max = df["sentiment"].max()

                correlation = 1 - abs(df["search_rank"].corr(df["sentiment"]))
                sentiment_bias = round((correlation * 100), 2)

                line1 = "Representation: __" + str(sentiment_bias) + "/100__"
                if correlation < 0:
                    line2 = "Results with _positive_ sentiment are likely to be seen _first_"
                elif correlation > 0:
                    line2 = "Results with _negative_ sentiment are likely to be seen _first_"
                else:
                    line2 = "Direction: No sentiment bias in results!"
                # df['new_score'] = df['score'] + abs(df['sentiment'])
                st.success(line1 + " (" + line2 + ").")
                st.write("\n")
                if sentiment_mean < 0:
                    sentiment_text = "negative"
                elif sentiment_mean == 0:
                    sentiment_text = "neutral"
                elif sentiment_mean > 0:
                    sentiment_text = "positive"

                st.write(
                    "The overall sentiment in your search results is _"
                    + sentiment_text
                    + "_, with a median sentiment score of "
                    + str(sentiment_median)
                    + ". Here's how sentiment varies with rank for your top "
                    + str(df_size)
                    + " search results. Results with positive and negative sentiment are highlighted in green and red respectively."
                )
                st.write("\n")

                plot_dist = (
                    alt.Chart(df[df["sentiment"].notna()])
                    .transform_density(
                        "sentiment",
                        as_=["sentiment", "density"],
                    )
                    .mark_area(opacity=0.75)
                    .encode(
                        x="sentiment:Q",
                        y="density:Q",
                        tooltip=["sentiment"],
                    )
                    .encode(
                        x=alt.X("sentiment:Q", title="Sentiment"),
                        y=alt.Y("density:Q", title=""),
                    )
                    .properties(height=450)
                )
                rule_dist = (
                    alt.Chart(df[df["sentiment"].notna()])
                    .mark_rule(color="red", strokeDash=[10, 10], size=2)
                    .encode(x="median(sentiment):Q")
                )
                st.altair_chart(plot_dist + rule_dist, use_container_width=True)
                st.markdown("\n")

                plot_corr = (
                    alt.Chart(df[df["sentiment"].notna()])
                    .mark_circle(size=300)
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
                st.altair_chart(rule_corr + plot_corr, use_container_width=True)

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
                df["latitude"] = df.apply(
                    lambda row: row["map_result_tuple"][1], axis=1
                )
                df["longitude"] = df.apply(
                    lambda row: row["map_result_tuple"][2], axis=1
                )
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

                counts = (
                    df.groupby("country_name")
                    .count()[["url"]]
                    .reset_index()
                    .rename(columns={"url": "count"})
                )
                ranks = df.groupby("country_name").mean()[["search_rank"]].reset_index()
                df_tabulated = counts.merge(ranks)
                df_tabulated["spatial_score"] = (
                    df_tabulated["count"] / df_tabulated["search_rank"]
                )
                spatial_bias_full = round(
                    (1 - rmad(df_tabulated[["spatial_score"]].values)) * 100, 2
                ) # this is representation as of now, not bias

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
                st.success("Representation: __" + str(spatial_bias_full) + "/100__")
                st.write("\n")

                st.write(
                    "Your top "
                    + str(df_size)
                    + " search results come from websites hosted in "
                    + str(df["country_name"].nunique())
                    + " countries - "
                    + countries
                    + ". Zoom in to see more below. :telescope:"
                )
                st.write("\n")
                map = folium.Map(
                    location=[0, 0], zoom_start=1.49, tiles="cartodb positron"
                )
                for i in range(0, len(df)):
                    folium.Marker(
                        location=[df.iloc[i]["latitude"], df.iloc[i]["longitude"]],
                        tooltip=df.iloc[i]["title"],
                    ).add_to(map)
                folium_static(map, width=620, height=500)

                st.markdown("&nbsp;")
                # IDEA: Add average rank per country plot.

        with expander3:
            df["domain"] = df.apply(lambda row: row["parsed_url"][1], axis=1)
            df["is_green"] = np.where(df["domain"].isin(green_list), "Green", "Red")
            green_count = len(df[df["is_green"] == "Green"])
            eco_hazard = round((green_count / len(df)) * 100, 2)

            st.success("Eco-friendliness: __" + str(eco_hazard) + "/100__")
            st.write("\n")
            st.write(
                str(round(eco_hazard, 2))
                + "% of your search results come from domains using renewable sources of energy."
            )
            st.write("\n")

            df_eco = pd.DataFrame(
                [eco_hazard, 100 - eco_hazard],
                columns=["value"],
            )
            df_eco["Source"] = ["Renewable", "Non-renewable"]
            df_eco["Energy"] = ["Energy", "Energy"]  # dummy column for plot
            plot_eco = (
                alt.Chart(df_eco)
                .mark_bar(opacity=0.75)
                .encode(
                    x=alt.X("sum(value)", title="Search results (%)"),
                    y=alt.Y("Energy", title="", sort="x"),
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
            [eco_hazard, spatial_bias_full, sentiment_bias],
            columns=["value"],
        )
        df_summary["label"] = [
            "Eco-friendliness",
            "Spatial Representation",
            "Sentiment Representation",
        ]

        plot_summary = (
            alt.Chart(df_summary)
            .mark_bar(cornerRadiusBottomRight=10, cornerRadiusTopRight=10, opacity=0.80)
            .encode(
                x=alt.X("value", title="Score (0-100)"),
                y=alt.Y("label", title="", sort="-x"),
                tooltip=["value"],
                color=alt.condition(
                    alt.datum.value > 50,
                    alt.value("#0ec956"),  # The positive color
                    alt.value("#ff1717"),  # The negative color
                ),
            )
            .properties(
                height=300,
                title="Representation Overview for " + str(df_size) + " search results",
            )
            .configure_title(fontSize=18)
            .configure_axis(labelFontSize=15, titleFontSize=15)
        )
        # threshold_line = (
        #     alt.Chart(pd.DataFrame({"x": [50]}))
        #     .mark_rule(strokeDash=[10, 10], size=1.5)
        #     .encode(x="x")
        # )
        summary_chart.altair_chart(plot_summary, use_container_width=True)
        st.markdown("&nbsp;")

        st.markdown("&nbsp;")
        if st.button("Add more search results to analysis"):
            st.markdown("_STILL COOKING!_ :spaghetti:")
            st.markdown(
                "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
            )

st.write("&nbsp;")
st.write("&nbsp;")
st.write("&nbsp;")
st.write("&nbsp;")
st.write("&nbsp;")
st.write("&nbsp;")
st.info("💡 De-centralized search is the future! Host Sonder locally for added control. Details [forthcoming](https://github.com/sonder-labs/sonder).")
