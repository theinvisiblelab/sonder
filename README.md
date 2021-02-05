# Sonder

![AGPL3 License](https://img.shields.io/github/license/saurabh-khanna/sonder)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/saurabh-khanna/sonder)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)

> *sonder (n.)*
>
>> the realization that each random passerby is living a life as vivid and complex as your own—populated with their own ambitions, friends, routines, worries and inherited craziness—an epic story that continues invisibly around you like an anthill sprawling deep underground, with elaborate passageways to thousands of other lives that you’ll never know existed, in which you might appear only once, as an extra sipping coffee in the background, as a blur of traffic passing on the highway, as a lighted window at dusk.
>
> &mdash; John Koenig, The Dictionary of Obscure Sorrows


## tl;dr

Our access to knowledge carries biases inherent in algorithms _trained_ to ~~promote understanding~~ maximize consumption. This robs us of the _choice_ to understand those who learn, think, and grow differently. `Sonder` is an attempt to make this choice explicit. To at least be conscious of our knowledge bubbles, if not break them.

We are working on two projects:
+ `Bias`: An attempt to understand how fair our search for web knowledge is. At present, we assess _sentiment bias_, _spatial bias_, and _lingual bias_ in web search results.
+ `Balance`: An attempt to enable fairer knowledge access. Affirmative action for knowledge search per se.


## Vision

_`Sonder` is an open-source metasearch engine dynamically assessing bias in our internet search results_. `Sonder` assesses search result `bias` along three dimensions. First, `Sonder` assesses _sentiment bias_ to understand if a particular sentiment or viewpoint occurs higher up or lower down our search results. Second, we assess _spatial bias_ to spotlight variance in coordinates for websites hosting our search results. Third, we assess _lingual bias_ to see linguistic representation in the entire internet knowledge base triggered by our search results. The code for `Sonder` is fully open-sourced and available under the GNU Affero General Public License.

As an open-source knowledge platform, `Sonder` is bound to be a community owned work-in-progress. We have three clear next steps towards which we need feedback and support. First, `Sonder` is currently hosted on a Heroku hobby dyno I have access to as a graduate student. Support in the form of grants or sponsorships will help us move the platform to a stronger server, hence increasing the platform performance. Second, we intend to add to the dimensions of assessing bias (e.g. bias by gender, ranking algorithm), as well as use more robust algorithms to assess this bias. Third, as a long-term goal, we intend to implement `Balance` &ndash; an attempt at fairer knowledge access by minimizing bias along different dimensions (affirmative action for knowledge search per se). Of course, we rely heavily on support from the open-source community towards achieving these goals.

The internet accounts for a large proportion of our access to knowledge, with effects bolstered further due to minimal in-person interaction in the current pandemic. Understanding the dynamics of modern knowledge access bears strong implications for sustaining inclusive learning environments built on top of a diverse knowledge base, and consequently an equitable evolution of society.

## Algorithms

`Sonder` curates meta-search results from a locally hosted [Searx](https://github.com/searx/searx) instance. Bias is calculated on three dimensions:

* __Sentiment Bias__: As a first step, `Sonder` evaluates the sentiment of search results using the polarity metric implemented in [TextBlob](https://github.com/sloria/TextBlob) &ndash; a Python library for processing textual data. As a second step, sentiment bias (_bias<sub>sent</sub>_) is assessed as the scaled absolute magnitude of the correlation between search result sentiment _sent<sub>i</sub>_ and search result rank _rank<sub>i</sub>_, where _i_ is an index corresponding to _n_ search results obtained from first ten meta-search web pages. The correlation sign is used to define the direction of the bias. A positive correlation indicates that results with negative sentiment are seen first (and vice versa for a negative correlation).

<p align="center">
  <img src="images/equation_sentiment.svg" />
</p>


* __Spatial Bias__: As a first step, `Sonder` geolocates search results obtained from the first ten meta-search web pages using free [GeoLite2](https://github.com/maxmind/GeoIP2-python) databases. As a second step, for each country, we divide the search result count (_total<sub>country</sub>_) by the mean result rank to obtain a country level spatial score (_cscore_). As a third step, we calculate the spatial bias as the relative mean absolute difference and scale it to a value between 0 and 100. Further, in order to differentiate out spatial bias arising out of the location initiating a web search, an adjusted spatial bias is also calculated by excluding the country in which `Sonder` is hosted from the relative mean absolute difference.

<p align="center">
  <img src="images/equation_spatial.svg" />
</p>

* __Lingual Bias__: As a first step, `Sonder` processes the search query to calculate the total count of results (_total<sub>lang</sub>_) obtained for the top ten languages by the number of internet users ([ref](https://en.wikipedia.org/wiki/Languages_used_on_the_Internet#Internet_users_by_language)). Then, the unadjusted lingual bias (_lscore_) is calculated as the relative mean absolute difference in these counts scaled to a value between 0 and 100. An adjusted lingual bias (_lscore<sub>adj</sub>_) is also calculated by using weights inversely proportional to content language distribution (_usage<sub>lang</sub>_) on the internet ([ref](https://en.wikipedia.org/wiki/Languages_used_on_the_Internet#Content_languages_for_websites)).

<p align="center">
  <img src="images/equation_lingual.svg" />
</p>


### Setting up your own `Sonder` instance

1. Clone this git repo to your local machine

```
git clone https://github.com/saurabh-khanna/sonder.git
cd sonder
```

2. Install dependencies

If `pipenv` is installed (recommended for dependency management):

```
pipenv install # assuming pipenv is installed locally
```

If `pipenv` is not installed:

```
pip3 install -r requirements.txt
```

3. [Optional] Set up your own [Searx](https://searx.github.io/searx/admin/installation.html) instance and [GeoLite2](https://dev.maxmind.com/geoip/geoip2/geolite2/) data accounts

4. Run `Sonder`

```
streamlit run scripts/sonder.py
```
