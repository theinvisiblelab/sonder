> *sonder (n.)*
>
>> the realization that each random passerby is living a life as vivid and complex as your own—populated with their own ambitions, friends, routines, worries and inherited craziness—an epic story that continues invisibly around you like an anthill sprawling deep underground, with elaborate passageways to thousands of other lives that you’ll never know existed, in which you might appear only once, as an extra sipping coffee in the background, as a blur of traffic passing on the highway, as a lighted window at dusk.
>
> &mdash; John Koenig, The Dictionary of Obscure Sorrows

&nbsp;

## :rocket: TL;DR

Our access to knowledge is biased by algorithms trained to maximize ~~understanding~~ consumption. This robs us of the _choice_ to understand those who learn, think, and grow differently. `Sonder` is an attempt to make this _choice_ explicit. To at least be conscious of our knowledge bubbles, if not break them.

We are working on two projects:
+ `Balance`: Enabling fairer knowledge access. Affirmative action for knowledge search per se.
+ `Bias trends`: Spotlighting global trends around fairness of web search. At present, we assess sentiment bias, spatial bias, and ecological hazard in web search results.

<br/>

## 🧭 ️Mission

Our access to knowledge on the internet carries biases inherent in algorithms trained to maximize consumption, rather than to promote understanding. This robs us of the _choice_ to understand those who learn, think, and grow differently. `Sonder` &ndash; an open-source platform enabling access to diverse knowledge &ndash; is an attempt to make this choice explicit. To at least be conscious of our knowledge bubbles, if not break them.

_Sonder is an open-source metasearch engine dynamically assessing bias in our internet search results_. Sonder assesses search result `bias` along three dimensions. First, Sonder assesses _sentiment bias_ to understand if a particular sentiment or viewpoint occurs higher up or lower down our search results. Second, we assess _spatial bias_ to spotlight variance in coordinates for websites hosting our search results. Third, we assess _lingual bias_ to see linguistic representation in the entire internet knowledge base triggered by our search results. The code for Sonder is fully open-sourced and available under the GNU Affero General Public License on [GitHub](https://github.com/sonder-labs/sonder).

As an open-source knowledge platform, Sonder is bound to be a community owned work-in-progress. We have three clear next steps towards which we need feedback and support. First, Sonder is currently hosted on a Heroku hobby dyno I have access to as a graduate student. Support in the form of grants or sponsorships will help us move the platform to a stronger server, hence increasing the platform performance. Second, we intend to add to the dimensions of assessing bias (e.g. bias by gender, ranking algorithm), as well as use more robust algorithms to assess this bias. Third, as a long-term goal, we intend to implement `Balance` &ndash; an attempt at fairer knowledge access by minimizing bias along different dimensions (affirmative action for knowledge search per se). Of course, we rely heavily on support from the open-source community towards achieving these goals.

The internet accounts for a large proportion of our access to knowledge, with effects bolstered further due to minimal in-person interaction in the current pandemic. Understanding the dynamics of modern knowledge access bears strong implications for sustaining inclusive learning environments built on top of a diverse knowledge base, and consequently an equitable evolution of society.

<br/>

## 🎯 Impact

_STILL COOKING!_ :spaghetti:

Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates.

<br/>

## 🧮 Algorithms

`Sonder` curates meta-search results from a locally hosted [Searx](https://github.com/searx/searx) instance. Bias is calculated on three dimensions:

* __Sentiment Bias__: As a first step, Sonder evaluates the sentiment of search results using the polarity metric implemented in [TextBlob](https://github.com/sloria/TextBlob) &ndash; a Python library for processing textual data. As a second step, sentiment bias ($bias_{sent}$) is assessed as the scaled absolute magnitude of the correlation between search result sentiment $sent_i$ and search result rank $rank_i$, where $i$ is an index corresponding to $n$ search results obtained from first ten meta-search web pages. The correlation sign is used to define the direction of the bias. A positive correlation indicates that results with negative sentiment are seen first (and vice versa for a negative correlation).

$$
bias_{sent} = \left\|\frac{{}\sum_{i=1}^{n} (sent_i - \overline{sent})(rank_i - \overline{rank})}
{\sqrt{\sum_{i=1}^{n} (sent_i - \overline{sent})^2(rank_i - \overline{rank})^2}} \right\| \times 100
$$

* __Spatial Bias__: As a first step, Sonder geolocates search results obtained from the first ten meta-search web pages using free [GeoLite2](https://github.com/maxmind/GeoIP2-python) databases. As a second step, for each country, we divide the search result count ($total_{country}$) by the mean result rank ($\overline{rank}_{country}$) to obtain a country level spatial score ($cscore$). As a third step, we calculate the spatial bias as the relative mean absolute difference and scale it to a value between 0 and 100. Further, in order to differentiate out spatial bias arising out of the location initiating a web search, an adjusted spatial bias is also calculated by excluding the country in which Sonder is hosted from the relative mean absolute difference.

$$
cscore = total_{country} \div \overline{rank}_{country}
$$

$$
bias_{spatial} = \frac{\sum_{i=1}^{n}\sum_{j=1}^{n} \left\|cscore_i - cscore_j\right\|}
  {2n^2 \overline{cscore}}
$$

* __Lingual Bias__: As a first step, Sonder processes the search query to calculate the total count of results ($total_{lang}$) obtained for the top ten languages by the number of internet users ([ref](https://en.wikipedia.org/wiki/Languages_used_on_the_Internet#Internet_users_by_language)). Then, the unadjusted lingual bias ($lscore$) is calculated as the relative mean absolute difference in these counts scaled to a value between 0 and 100. An adjusted lingual bias ($lscore_{adj}$) is also calculated by using weights inversely proportional to content language distribution ($usage_{lang}$) on the internet ([ref](https://en.wikipedia.org/wiki/Languages_used_on_the_Internet#Content_languages_for_websites)).

$$
lscore = total_{lang}
$$
$$
lscore_{adj} = total_{lang} \div usage_{lang}
$$

$$
bias_{lingual} = \frac{\sum_{i=1}^{n}\sum_{j=1}^{n} \left\|lscore_i - lscore_j\right\|}
  {2n^2 \overline{lscore}}
$$


<hr style="border:1.5px black"> </hr>
