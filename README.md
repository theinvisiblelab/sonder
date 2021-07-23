# S🎈nder

![AGPL3 License](https://img.shields.io/github/license/saurabh-khanna/sonder)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/saurabh-khanna/sonder)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4536014.svg)](https://doi.org/10.5281/zenodo.4536014)


> *son$\cdot$der (n.)*
>
>> the realization that each random passerby is living a life as vivid and complex as your own
>
> &mdash; John Koenig, The Dictionary of Obscure Sorrows


## ⚡ TL;DR

Internet search shows you what you consume. Sonder shows you what you miss out on. We assess the opportunity cost of internet search.

Our access to knowledge is biased by ~~public~~ private algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~understanding~~ consumption. This robs us of the choice to understand those who think and learn differently. Sonder is an attempt to make our lack of choice explicit. To at least be mindful of our filter bubbles, if not break them.

We are working along two dimensions:

+ ⚖️ Balance: Assess latent/hidden knowledge as you search the web. Balance relevance with diversity.
+ 📣 Trends: Highlight fairness in web, news, wiki, and social media trends.


<br/>

## 👀 Glimpses

Latent knowledge summary for search query:

<p align="center">
  <img src="images/1.png" />
</p>

<br/>

Latent sentiment:

<p align="center">
  <img src="images/2.png" />
</p>

<br/>

Latent geographies:

<p align="center">
  <img src="images/3.png" />
</p>

<br/>

Latent carbon cost:

<p align="center">
  <img src="images/4.png" />
</p>

<br/>

Global sentiment trends (Web search):

<p align="center">
  <img src="images/5.png" />
</p>

<br/>

Global sentiment trends (News search):

<p align="center">
  <img src="images/6.png" />
</p>


## 🧭 ️Mission

Our access to knowledge on the internet carries biases inherent in algorithms trained to maximize consumption, rather than to promote understanding. This robs us of the _choice_ to understand those who learn, think, and grow differently. Sonder &ndash; a nonprofit open-source platform enabling access to diverse knowledge &ndash; is an attempt to make this choice explicit. To at least be conscious of our knowledge bubbles, if not break them.

Sonder is an open-source search platform dynamically assessing and tackling bias in our internet search results. Sonder assesses search result bias along three dimensions. First, Sonder assesses _sentiment bias_ to understand if a particular sentiment or viewpoint occurs higher up or lower down our search results. Second, we assess _spatial bias_ to spotlight variance in coordinates for websites hosting our search results. Third, we assess _environmental bias_ to highlight the proportion of our search results consuming non-renewable sources of energy. The code for Sonder is fully open-sourced and available under the GNU Affero General Public License on [GitHub](https://github.com/sonder-labs/sonder).

As an open-source knowledge platform, Sonder is bound to be a community owned work-in-progress. We have four clear next steps towards which we need feedback and support. First, Sonder is currently hosted on a Heroku hobby dyno we have access to as graduate students. Support in the form of grants or sponsorships will help us move the platform to a stronger server, hence increasing the platform performance. Second, we intend to add to the dimensions of assessing bias (e.g. bias by gender, ranking algorithm), as well as use more robust algorithms to assess this bias. Third, we intend to implement Balance &ndash; an attempt at fairer knowledge access by minimizing bias along different dimensions (affirmative action for knowledge search per se). Fourth, we intend to run Unsung &ndash; a platform publishing stories that would otherwise go unheard. Of course, we rely heavily on support from the open-source community towards achieving these goals.

The internet accounts for a large proportion of our access to knowledge, with effects bolstered further due to minimal in-person interaction in the current pandemic. Understanding the dynamics of modern knowledge access bears strong implications for sustaining inclusive learning environments built on top of a diverse knowledge base, and consequently an equitable evolution of society.

<br/>

## 🎯 Impact

_STILL COOKING!_ :spaghetti:

Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates.

<br/>

## 🧮 Algorithms

`Sonder` curates meta-search results from a locally hosted Searx instance. Bias is calculated on three dimensions:

* __Sentiment Bias__: As a first step, Sonder evaluates the sentiment of search results using the polarity metric implemented in TextBlob &ndash; a Python library for processing textual data. As a second step, sentiment bias (_bias<sub>sent</sub>_) is assessed as the scaled absolute magnitude of the correlation between search result sentiment _sent<sub>i</sub>_ and search result rank _rank<sub>i</sub>_, where _i_ is an index corresponding to _n_ search results obtained from first ten meta-search web pages. The correlation sign is used to define the direction of the bias. A positive correlation indicates that results with negative sentiment are seen first (and vice versa for a negative correlation).

<p align="center">
  <img src="images/equation_sentiment.svg" />
</p>


* __Spatial Bias__: As a first step, Sonder geolocates search results obtained from the first ten meta-search web pages using public GeoLite2 databases. As a second step, for each country, we divide the search result count (_total<sub>country</sub>_) by the mean result rank to obtain a country level spatial score (_cscore_). As a third step, we calculate the spatial bias as the relative mean absolute difference and scale it to a value between 0 and 100. Further, in order to differentiate out spatial bias arising out of the location initiating a web search, an adjusted spatial bias is also calculated by excluding the country in which `Sonder` is hosted from the relative mean absolute difference.

<p align="center">
  <img src="images/equation_spatial.svg" />
</p>

* __Environmental Bias__: Sonder queries the public database of green domains hosted by the The Green Web Foundation to flag if a given search result is hosted on a domain running on renewable sources of energy. Environmental bias is reflected in the proportion of overall search results hosted on domains running on non-renewable sources of energy.
