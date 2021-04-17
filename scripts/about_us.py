'''
> *sonder (n.)*
>
>> the realization that each random passerby is living a life as vivid and complex as your own—populated with their own ambitions, friends, routines, worries and inherited craziness—an epic story that continues invisibly around you like an anthill sprawling deep underground, with elaborate passageways to thousands of other lives that you’ll never know existed, in which you might appear only once, as an extra sipping coffee in the background, as a blur of traffic passing on the highway, as a lighted window at dusk.
>
> &mdash; John Koenig, The Dictionary of Obscure Sorrows

&nbsp;
'''

with st.beta_expander("⚡ TL;DR", expanded=True):
    st.markdown(
    '''
    Our access to knowledge is biased by ~~open-source~~ proprietary algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~understanding~~ consumption. This robs us of the _choice_ to understand those who learn, think, and grow differently. `Sonder` is an attempt to make this _choice_ explicit. To at least be conscious of our knowledge bubbles, if not break them.

    We are working on three projects (see left pane):
    + `Balance`: Enabling fairer knowledge search by balancing relevance with diversity.
    + `Trends`: Showcasing global trends around fairness of knowledge access on the internet.
    + `Unsung`: Spotlighting untold stories from around the planet.

    &nbsp;
    '''
    )

with st.beta_expander("🧭 ️Mission"):
    st.markdown(
    '''
    Our access to knowledge on the internet carries biases inherent in algorithms trained to maximize consumption, rather than to promote understanding. This robs us of the _choice_ to understand those who learn, think, and grow differently. Sonder &ndash; a nonprofit open-source platform enabling access to diverse knowledge &ndash; is an attempt to make this choice explicit. To at least be conscious of our knowledge bubbles, if not break them.

    Sonder is an open-source search platform dynamically assessing and tackling bias in our internet search results. Sonder assesses search result bias along three dimensions. First, Sonder assesses _sentiment bias_ to understand if a particular sentiment or viewpoint occurs higher up or lower down our search results. Second, we assess _spatial bias_ to spotlight variance in coordinates for websites hosting our search results. Third, we assess _environmental bias_ to highlight the proportion of our search results consuming non-renewable sources of energy. The code for Sonder is fully open-sourced and available under the GNU Affero General Public License on [GitHub](https://github.com/sonder-labs/sonder).

    As an open-source knowledge platform, Sonder is bound to be a community owned work-in-progress. We have four clear next steps towards which we need feedback and support. First, Sonder is currently hosted on a Heroku hobby dyno we have access to as graduate students. Support in the form of grants or sponsorships will help us move the platform to a stronger server, hence increasing the platform performance. Second, we intend to add to the dimensions of assessing bias (e.g. bias by gender, ranking algorithm), as well as use more robust algorithms to assess this bias. Third, we intend to implement Balance &ndash; an attempt at fairer knowledge access by minimizing bias along different dimensions (affirmative action for knowledge search per se). Fourth, we intend to run Unsung &ndash; a platform publishing stories that would otherwise go unheard. Of course, we rely heavily on support from the open-source community towards achieving these goals.

    The internet accounts for a large proportion of our access to knowledge, with effects bolstered further due to minimal in-person interaction in the current pandemic. Understanding the dynamics of modern knowledge access bears strong implications for sustaining inclusive learning environments built on top of a diverse knowledge base, and consequently an equitable evolution of society.

    &nbsp;
    '''
    )

with st.beta_expander("🎯 Impact"):
    st.markdown(
    '''
    _STILL COOKING!_ :spaghetti:

    Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates.

    &nbsp;
    '''
    )

with st.beta_expander("🧮 Algorithms"):
    st.markdown(
    '''
    `Sonder` curates meta-search results from a locally hosted Searx instance. Bias is calculated on three dimensions:

    * __Sentiment Bias__: As a first step, Sonder evaluates the sentiment of search results using the polarity metric implemented in TextBlob &ndash; a Python library for processing textual data. As a second step, sentiment bias ($bias_{sent}$) is assessed as the scaled absolute magnitude of the correlation between search result sentiment $sent_i$ and search result rank $rank_i$, where $i$ is an index corresponding to $n$ search results obtained from first ten meta-search web pages. The correlation sign is used to define the direction of the bias. A positive correlation indicates that results with negative sentiment are seen first (and vice versa for a negative correlation).

    $$
    bias_{sent} = \left\|\frac{{}\sum_{i=1}^{n} (sent_i - \overline{sent})(rank_i - \overline{rank})}
    {\sqrt{\sum_{i=1}^{n} (sent_i - \overline{sent})^2(rank_i - \overline{rank})^2}} \right\| \times 100
    $$

    * __Spatial Bias__: As a first step, Sonder geolocates search results obtained from the first ten meta-search web pages using public GeoLite2 databases. As a second step, for each country, we divide the search result count ($total_{country}$) by the mean result rank ($\overline{rank}_{country}$) to obtain a country level spatial score ($cscore$). As a third step, we calculate the spatial bias as the relative mean absolute difference and scale it to a value between 0 and 100. Further, in order to differentiate out spatial bias arising out of the location initiating a web search, an adjusted spatial bias is also calculated by excluding the country in which Sonder is hosted from the relative mean absolute difference.

    $$
    cscore = total_{country} \div \overline{rank}_{country}
    $$

    $$
    bias_{spatial} = \frac{\sum_{i=1}^{n}\sum_{j=1}^{n} \left\|cscore_i - cscore_j\right\|}
      {2n^2 \overline{cscore}}
    $$

    * __Environmental Bias__: We query the public database of green domains hosted by the The Green Web Foundation to flag if a given search result is hosted on a domain running on renewable sources of energy. Environmental bias is reflected in the proportion of overall search results hosted on domains running on non-renewable sources of energy.

    &nbsp;
    '''
    )
