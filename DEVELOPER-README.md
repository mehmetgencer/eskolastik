citeproc-js
--------------------------------------------------
citeproc-js is used with an adaptation layer. Such adaptation were, for the most part, necessary since
e-Skolastik data model uses BibTex for bibliographic information about publications. 
While BibTex is mature and capable data model, it is not the best one for presentation, where
citeproc-js excels. Thus the code contained in client.js does most of the heavy-lifting to
translate BibTex data mode to citeproc-js (in the blient browser). However, citeproc-js 
is not very well documented and some aspects of this translation is shaky.

See the following resources about citeproc-js whenever necessary:
* http://gsl-nagoya-u.net/http/pub/citeproc-doc.html
* http://citationstyles.org/downloads/specification-csl10-20100530.html#appendix-i-variables
* Note the citeproc links at: http://xbiblio-devel.2463403.n2.nabble.com/Citeproc-json-data-input-specs-td5135372.html
* The input object - the list of references - is modelled on the CSL list of variables: http://bitbucket.org/bdarcus/csl-schema/src/tip/csl-variables.rnc
* The cs-names object (author, etc) is documented in the citeproc-js documentation: http://gsl-nagoya-u.net/http/pub/citeproc-doc.html#id25
* Dates are documented here: http://gsl-nagoya-u.net/http/pub/citeproc-doc.html#input-dates
* The type object (a string) can have the value listed here: http://bitbucket.org/bdarcus/csl-schema/src/tip/csl-types.rnc

Other
------
Following are some open technologies worth considering for future:
* OAI search interface http://www.base-search.net/

