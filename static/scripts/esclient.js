/**
 * THE CLIENT SIDE SPECIFIC LIBRARY FOR E-SKOLASTIK.
 * IT MOSTLY ADDRESSES INTEGRATION OF CITEPROC-JS LIBRARY.
 * 
 * THE CODE IN THIS SCRIPT IS SELF EXPLANATORY WHEN READ STARTING FROM THE
 * FUNCTION AT THE BOTTOM!
 */


/**
 * Once retrieved, the profile data (which includes publications) is cached as an attribute of "pageDiv" HTML element
 * This method reuses that cache to select and return the data for the publication whose id is given 
 */   
  function getPub(id){
      gkc=document.getElementById("pageDiv").LAST_GK_CONTEXT;
      //esdebug("Looking for id:"+id+" in context:"+gkc);
      skey=parseInt(id.split("-")[0]);
      pkey=parseInt(id.split("-")[1]);
      //esdebug("Looking for sec:"+skey);
      for(var s in gkc["sections"])
         if (gkc["sections"][s]["sectionKey"]==skey)
            var sec=gkc["sections"][s];
      for(var p in sec["publications"])
         if (sec["publications"][p]["publicationKey"]==pkey)
            var pub=sec["publications"][p];
      return pub;
   }
 
 /**
   * Given a list of author names, parses and builds a list of dictionaries suitable for citeproc  
   * See http://gsl-nagoya-u.net/http/pub/citeproc-test.html for details of the structure used by citeproc
   */ 
 function makeCiteprocAuthors(authors) {
    retval=[];
    esdebug("IE-DEBUG authors:"+authors);
    for (var i=0;i<authors.length;i=i+1) {
       author=authors[i]||"";
       esdebug("IE-DEBUG i:"+i);
       esdebug("Author:"+author);
       if (author.length==0)
         continue;
       esdebug("IE-DEBUG Parsing author:"+author);
       aparts=author.split(" ");
       given=[];
       family=[];
       family.push(aparts.pop());
       now=family;
       while (aparts.length>0 ) {
          a=aparts.pop();
          if (a.length>0) {
             if(a[0]!=a[0].toUpperCase())
               family.push(a);
            else
               given.push(a);
          }
       }
       given.reverse();
       family.reverse();
       retval.push({"family":family.join(" "),"given":given.join(" ")});
    }
    //retval.reverse();
    //esdebug("Returning citeproc authors:"+JSON.stringify(retval));
    return retval;
 }
 /**
  * Type of a publication sometimes have different names in bibtex/e-skolastik and citeproc
  * This function handles this mapping (to my best knowledge) 
  * when called from within getCiteprocItem().
  */ 
 function mapType(t) {
   typemap={
      "article":"article-journal",
      "inbook":"chapter",
      "inproceedings":"paper-conference",
      "masterthesis":"thesis",
      "phdthesis":"thesis",
      "unpublished":"manuscript"
      };
   if (typemap[t])
      return typemap[t];
   else
      return t;
}

/**
 * This is the function which takes the e-skolastic data representation of a publication with given id
 * and returns the corresponding citeproc data representation.
 * Please consult http://citationstyles.org/downloads/specification-csl10-20100530.html#appendix-i-variables
 * For (unfortunately incomplete) documentation of citeproc variables for bibliographic entities.
 * 
 * E-skolastik's data representation follow bibtex standard field names for the most part. However
 * citeproc has its own naming of variables, as well as different means of representing, for example, dates.
 * Also citeproc expects a more elaborate data structure for author and editor names (compared to bibtex which
 * parses them as needed)
 */
 function getCiteprocItem(id){
   pub=getPub(id);
   esdebug("getting citeproc item: pub:"+JSON.stringify(pub));
   authors=[];
   for (var i in pub["authors"])
      authors.push(pub["authors"][i]["name"])
   editors=pub["pubinfo"]["editor"].split(",");
   esdebug("editors:"+editors);
   esdebug("and authors:"+authors);
   retval= {
		"id": id,
		"type":mapType(pub["pubtype"]),
		"title":pub["title"],
		//"container-title":(pub["pubtype"]=="unpublished") ?  pub["pubinfo"]["note"] : pub["pubinfo"]["booktitle"],
		"author": makeCiteprocAuthors(authors),
		"editor":makeCiteprocAuthors(editors),
		"container-title":{"unpublished":pub["pubinfo"]["note"],"article":pub["pubinfo"]["journal"],"inproceedings":pub["pubinfo"]["booktitle"]}[pub["pubtype"]],
		//"DOI":pub["pubinfo"]["DOI"],
		//"ISBN":pub["pubinfo"]["ISBN"],
		"URL":pub["pubinfo"]["howpublished"],
		//"publisher": pub["pubinfo"]["publisher"],
		"page":pub["pubinfo"]["pages"],
		//"event":pub["pubinfo"]["note"],
		//"authority":pub["pubinfo"]["school"],
		"issued": {
			"date-parts":[
				[pub["pubinfo"]["year"]]
			]
		}
	  };	    
	//the following variables have the same name and type/structure in both e-skolastik/bibtex and citeproc-js, 
	//  so they are directly copied
	parts=["journal","volume","note","publisher","DOI","ISBN"];
	for (var i in parts)
	  retval[parts[i]]=pub["pubinfo"][parts[i]];
	esdebug("Returning citeprocitem:"+JSON.stringify(retval));
	return retval;
 }
 
 /**
  * The following definition links all application specific logic to citeproc mechanism
  * TODO: currently language is not actually chosen properly, abbreviations are not used at all (which does not seem necessary)
 */
 citeprocsys={ 
   retrieveLocale:
      function(lang){
         return locale["en-US"];
      },
   retrieveItem:
      function(id){
         return getCiteprocItem(id);
      },
   getAbbreviation : function(dummy, obj, jurisdiction, vartype, key){
     obj["default"][vartype][key] = "";
    },
    setAbbreviations : function (abbrevsname) {
        this.abbrevsname = abbrevsname;
    }
 };
 
 /**
  * This is the function which is triggered when you use citeproc tag in dust.js template. 
  * It triggers (through citeproc machinery) the getCiteprocItem(id) method to retrieve content.
  */
 function escoreCiteproc(chunk, context, bodies, params){
   //skey=params["sectionKey"];
   skey=context.get("sectionKey");
   //pkey=params["publicationKey"];
   pkey=context.get("publicationKey");
   var pub=getPub(skey+"-"+pkey);
   if (!pub["ispub"]) {
      chunk.write(pub["desc"]);
      return chunk;
   } else {
      citeproc = new CSL.Engine(citeprocsys, chicago_author_date,"en-us");
      citeproc.updateUncitedItems( [skey+"-"+pkey] );
      var mybib = citeproc.makeBibliography();
      esdebug("mybib:"+JSON.stringify(mybib));
      chunk.write(mybib[1][0]);
      return chunk;
   }
 }
