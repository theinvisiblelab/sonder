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
from plotnine import *

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

# st.write("Bias is an attempt to understand how fair our search for web knowledge is.")

query = st.text_input("Seek fairer human knowledge...").strip()

st.markdown("&nbsp;")

if query != "":
    search_type = st.radio("", ["Balanced results [Under development]", "Unbalanced results"], 1)

    if search_type == "Balanced results [Under development]":
        st.markdown("&nbsp;")
        st.markdown("&nbsp;")
        st.markdown("_STILL COOKING!_ :spaghetti:")
        st.markdown(
            "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
        )

    col1, col2 = st.beta_columns(2)

    if search_type == "Unbalanced results":

        with st.spinner("Assessing bias in your search..."):
            df = load_searx_data(query)
            green_list = pd.read_csv(Path("green/greendomain.txt"))["url"].tolist()

        with col1:
            st.markdown("### Search results")
            st.markdown("---")
            # st.markdown("\n\n")
            # presently printing out top 20 search results
            for index, row in df.iterrows():
                with st.beta_container():
                    # st.write("Sentiment: ", row["polarity"])
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

        col2.markdown("### Bias in search results")
        col2.markdown("---")
        summary_chart = col2.empty()

        expander1 = col2.beta_expander("🔥 Eco Hazard: Are my results coming from eco-friendly domains?", expanded=True)
        expander2 = col2.beta_expander("🗣️ Sentiment Bias: Do I see more positive (or more negative) sentiment in my results?", expanded=True)
        expander3 = col2.beta_expander("🌍 Spatial Bias: Are my results hosted in geographically diverse locations?", expanded=True)
        # expander3 = col2.beta_expander("🦜 Lingual Bias", expanded=True)

        with expander1:
            df["domain"] = df.apply(lambda row: row["parsed_url"][1], axis=1)
            df["is_green"] = np.where(df["domain"].isin(green_list), "Green", "Red")
            green_count = len(df[df["is_green"] == "Green"])
            eco_hazard = round((1 - (green_count / len(df))) * 100, 2)

            st.success(
                str(eco_hazard)
                + "% of your search results come from domains using _non-renewable_ sources of energy."
            )

            df_eco = pd.DataFrame(
                [eco_hazard, 100 - eco_hazard],
                columns=["value"],
            )
            df_eco["label"] = ["Red", "Green"]
            df_eco["Energy"] = ["Energy", "Energy"]  # dummy column for plot
            # Summary plot
            plot_eco = (
                ggplot(df_eco, aes("Energy", "value", fill="label"))
                + geom_col(alpha=0.75, color="black")
                + scale_y_continuous(
                    labels=lambda l: ["%d%%" % v for v in l], limits=[0, 100]
                )
                + scale_fill_manual(values=["#0ec956", "#ff1717"])
                + theme_minimal()
                + theme(legend_position="none", figure_size=(8, 2))
                + coord_flip()
                + labs(x="", y="")
            )
            st.pyplot(ggplot.draw(plot_eco))
            st.markdown("&nbsp;")

        with expander2:
            with st.spinner("Assessing sentiment in your search results..."):
                df["search_rank"] = df.reset_index().index + 1
                df["pol_title"] = df.apply(lambda row: sentiment_calc(row["title"]), axis=1)
                df["pol_content"] = df.apply(
                    lambda row: sentiment_calc(row["content"]), axis=1
                )
                df["polarity"] = ((2 * df["pol_title"]) + df["pol_content"]) / 3
                df["polarity"] = df["polarity"].apply(lambda x: round(x, 4))
                sentiment_mean = round(df["polarity"].mean(), 4)
                sentiment_median = round(df["polarity"].median(), 4)
                sentiment_min = df["polarity"].min()
                sentiment_max = df["polarity"].max()
                df_size = len(df.index)

                correlation = df["search_rank"].corr(df["polarity"])
                sentiment_bias = round(abs(correlation * 100), 2)

                line1 = "Bias magnitude: _" + str(sentiment_bias) + " /100_"
                if correlation < 0:
                    line2 = "Bias direction: Results with _positive_ sentiment are likely to be seen _first_."
                elif correlation > 0:
                    line2 = "Bias direction: Results with _negative_ sentiment are likely to be seen _first_."
                else:
                    line2 = "Bias direction: No sentiment in bias in results!"
                # df['new_score'] = df['score'] + abs(df['polarity'])
                st.success(line1 + "  \n" + line2)
                st.write("\n")
                if sentiment_mean <= -0.1:
                    sentiment_text = "negative"
                if sentiment_mean > -0.1 and sentiment_mean < 0.1:
                    sentiment_text = "neutral"
                if sentiment_mean >= 0.1:
                    sentiment_text = "positive"

                st.write(
                    "The overall sentiment in your search results is "
                    + sentiment_text
                    + ", with a mean sentiment score of "
                    + str(sentiment_mean)
                    + ". The distribution of sentiment in these results is shown below, with the red line highlighting the distribution median."
                )
                plot_dist = (
                    ggplot(df, aes("polarity"))
                    + geom_density(
                        fill="blue", alpha=0.25, na_rm=True
                    )  # Idea: fill by sentiment
                    + geom_vline(
                        xintercept=sentiment_median, linetype="dashed", color="red"
                    )
                    + theme_bw()
                    + xlim(sentiment_min, sentiment_max)
                    + labs(x="Sentiment", y="Density")
                )
                st.pyplot(ggplot.draw(plot_dist))
                st.markdown("\n")

                st.write(
                    "Here's a scatter plot of search result rank versus sentiment for your top "
                    + str(df_size)
                    + " search results."
                )
                plot_corr = (
                    ggplot(df, aes("search_rank", "polarity"))
                    + geom_hline(yintercept=0, linetype="dashed")
                    + annotate(
                        "rect",
                        xmin=-np.Inf,
                        xmax=np.Inf,
                        ymin=0,
                        ymax=np.Inf,
                        alpha=0.1,
                        fill="green",
                    )
                    + annotate(
                        "rect",
                        xmin=-np.Inf,
                        xmax=np.Inf,
                        ymin=-np.Inf,
                        ymax=0,
                        alpha=0.1,
                        fill="red",
                    )
                    + geom_jitter(fill="blue", alpha=0.5, size=3)
                    + theme_bw()
                    + labs(x="Search Result Rank", y="Sentiment")
                )
                st.pyplot(ggplot.draw(plot_corr))

                st.markdown("&nbsp;")

        with expander3:
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
                    rmad(df_tabulated[["spatial_score"]].values) * 100, 2
                )
                # Replace sonder_host_country with appropriate value if your Sonder server is hosted in another country
                sonder_host_country = "United States"
                spatial_bias_adjusted = round(
                    rmad(
                        df_tabulated[df_tabulated["country_name"] != sonder_host_country][
                            ["spatial_score"]
                        ].values
                    )
                    * 100,
                    2,
                )
                st.success(
                    "Bias magnitude (Unadjusted): _"
                    + str(spatial_bias_full)
                    + "/100_"
                    + "  \n"
                    + "Bias magnitude (excluding country where `Sonder` is hosted): _"
                    + str(spatial_bias_adjusted)
                    + "/100_"
                )
                st.write("\n")
                st.write(
                    "You can zoom in to see where your search results come from. :telescope:"
                )
                map = folium.Map(location=[0, 0], zoom_start=1.49, tiles="cartodb positron")
                for i in range(0, len(df)):
                    folium.Marker(
                        location=[df.iloc[i]["latitude"], df.iloc[i]["longitude"]],
                        popup=df.iloc[i]["city"],
                    ).add_to(map)
                folium_static(map, width=665, height=500)
                st.write("\n")
                st.write(
                    "Your top "
                    + str(df_size)
                    + " search results come from websites hosted in "
                    + str(df["country_name"].nunique())
                    + " countries. The host country for `Sonder` is highlighted in a separate color."
                )
                country_list = df["country_name"].value_counts().index.tolist()[::-1]
                df["country_cat"] = pd.Categorical(
                    df["country_name"], categories=country_list
                )
                df["sonder_host_country"] = "True"
                df.loc[
                    df["country_name"] != "United States", "sonder_host_country"
                ] = "False"
                plot_country = (
                    ggplot(df, aes("country_cat"))
                    + geom_bar(
                        aes(fill="sonder_host_country"),
                        color="black",
                        alpha=0.25,
                        na_rm=True,
                    )
                    + scale_fill_manual(values=["blue", "red"])
                    + theme_bw()
                    + theme(legend_position="none")
                    + coord_flip()
                    + labs(x="Country", y="Results")
                )
                st.pyplot(ggplot.draw(plot_country))
                st.markdown("&nbsp;")
                # IDEA: Add average rank per country plot.
                st.markdown("---")
                st.markdown(
                    "<span style='color:gray'>_Details on bias calculation algorithms can be seen [here](https://github.com/sonder-labs/sonder#-algorithms)_</span>",
                    unsafe_allow_html=True,
                )
        # with expander3:
        #     with st.spinner("Assessing lingual bias in your search results..."):
        #         df_lang = pd.DataFrame(load_lang_data(query))
        #         df_lang.columns = ["language", "count"]
        #         df_lang = df_lang.sort_values(by=["language"])
        #         df_lang["web_usage"] = [1.1, 1.4, 60.5, 2.7, 2.3, 0.7, 2.1, 1.1, 8.5, 3.9]
        #         df_lang["lingual_score"] = df_lang["count"] / df_lang["web_usage"]
        #
        #         lingual_bias_full = round(rmad(df_lang[["count"]].values) * 100, 2)
        #         lingual_bias_adjusted = round(
        #             rmad(df_lang[["lingual_score"]].values) * 100, 2
        #         )
        #
        #         st.success(
        #             "Bias magnitude (Unadjusted): _"
        #             + str(lingual_bias_full)
        #             + "/100_"
        #             + "  \n"
        #             + "Bias magnitude (adjusted for language distribution on the internet): _"
        #             + str(lingual_bias_adjusted)
        #             + "/100_"
        #         )
        #         st.write("\n")
        #         st.write(
        #             "The distribution of your _total search results_ among the top 10 internet languages (based on number of users) can be seen below."
        #         )
        #         df_lang = df_lang.sort_values(by=["count"])
        #         lang_list = df_lang["language"].tolist()
        #         df_lang["language_cat"] = pd.Categorical(
        #             df_lang["language"], categories=lang_list
        #         )
        #         plot_lang = (
        #             ggplot(df_lang, aes("language_cat", "count"))
        #             + geom_col(fill="blue", color="black", alpha=0.25, na_rm=True)
        #             + theme_bw()
        #             + coord_flip()
        #             + labs(x="Language", y="Total Results")
        #         )
        #         st.pyplot(ggplot.draw(plot_lang))

        # Summary data frame
        df_summary = pd.DataFrame(
            [spatial_bias_full, sentiment_bias, eco_hazard],
            columns=["value"],
        )
        df_summary["label"] = ["Spatial Bias", "Sentiment Bias", "Eco Hazard"]
        df_summary["label_cat"] = pd.Categorical(
            df_summary["label"], categories=df_summary["label"].tolist()
        )
        df_summary.loc[df_summary["value"] <= 33, "bias_level"] = "1"
        df_summary.loc[df_summary["value"] > 33, "bias_level"] = "2"
        df_summary.loc[df_summary["value"] > 66, "bias_level"] = "3"
        df_summary = df_summary.sort_values(by=["value"])
        # Summary plot
        plot_summary = (
            ggplot(df_summary, aes("label_cat", "value"))
            + geom_col(
                aes(fill="bias_level"),
                alpha=0.70,
                na_rm=True,
            )
            + geom_hline(yintercept=33, linetype="dashed")
            + geom_hline(yintercept=66, linetype="dashed")
            + scale_y_continuous(labels=lambda l: ["%d%%" % v for v in l], limits=[0, 100])
            + scale_fill_manual(values=["#0ec956", "#ffbf00", "#ff1717"])
            + theme_light()
            + theme(legend_position="none", legend_title_align="left")
            + coord_flip()
            + labs(x="", y="")
        )
        summary_chart.pyplot(ggplot.draw(plot_summary))
        st.markdown("&nbsp;")

        st.markdown("&nbsp;")
        if st.button("Add more search results to analysis"):
            st.markdown("_STILL COOKING!_ :spaghetti:")
            st.markdown(
                "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
            )
