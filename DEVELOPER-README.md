Summary of system architecture
================================
The server side is quite plain. Communication between client browser and server is mostly
through Ajax/JSON. Even the admin interface is a single html page which, once loaded, does the 
rest of its job via Ajax/JSON calls, and refreshing the page with dust.js. Responses to Ajax calls are cached
in the client side whenever appropriate (e.g. in profile display but now in admin page).

Dust.js templates are compiled on the client side to keep the server side and control logic clean 
(which works fairly fast). This also makes it easier to design mechanisms which allow user created designs.

Web server uses Google account infrastructure for loggin in users.

The profiles displayed at the client uses the same system. However the academic profile display page
is rendered with the profile info JSON is embedded into its javascript. This allows users to take a
copy of this html page (and all publication file attachments) and host it anywhere they like. No
Ajax calls are necessary to display profiles. Thus 
people can use e-skolastik to manage their academic profile page, but do not have to use it for hosting these
pages. Although it is probably much easier to do so.

Every client page must have a JQuery.ready() function to trigger compilation of dust.js templates (see below), and 
making the first Ajax call. e.g.:
    $(function() {
         autoLoadTemplates();
         callAPIAndRenderToElement("/apipublic/getProfile?profile={{pid}}",{},"default","pageDiv",function(result){
         },true);
     });

where {{pid}} is filled in by Django template at the server during rendering of the page.

Internalization is not addressed very well at this point. All pages share a simple system which allows i18n
to be used from within dust.js templates, and it is backed by a simple JSON datastructure (in translations.js). 
This does the job for the admin interface.

i18n of profiles is not addressed at all. 

Notes on libraries used
========================
dust.js
----------
It is stable and very well documented. The gktemplating.js contains code to automatically discover dust.js templates
in an html page, and compile them prior to their use (to speed up the process, e.g. while the page is awaiting 
Ajax response the dust.js templates are compiled, etc.). Following is a typical html fragment:

    <div class='templateContainer'>
        <div class="estemplate" tid="default">
            ...
        </div>
    </div>

The class 'templateContainer' is discovered by autoLoadTemplates(), and  each div of class 'estemplate' is compiled
as a separate dust.js template whose name, for future reference, is given in 'tid' attribute. In the example above
callAPIAndRenderToElement(..., "default",...) function uses this reference name. This call will take the Ajax response
and fed it to the chosen dust.js template.


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
I have used pandoc for compiling help content from markdown to html. The make target 'make docs' does it 
if you have pandoc installed via cabal-install. Please let me know if you have problems with that.

Following are some open technologies worth considering for future:
* OAI search interface http://www.base-search.net/

