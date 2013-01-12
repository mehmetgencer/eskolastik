/**
  * Function to display debug messages, independent of browser type or capability
  */
function esdebug(msg) {
   if (!window.console) {
   } else
      window.console.log(msg);
}
/**
 * Function to display a yes/no confirm message
 */
function esconfirm(msg) {
	return confirm(msg);
}

/**
 * Following chunks of code determine user/browser language preference
 * The determined language code (e.g. "tr" or "en" is stored in the variable 'lang'
 */
var langfull = window.navigator.language || window.navigator.userLanguage;
var lang=langfull.split("-")[0];
esdebug("Useragetn:"+navigator.userAgent);

var lang;
if (navigator
         && navigator.userAgent
         && (lang = navigator.userAgent
                 .match(/android.*\W(\w\w)-(\w\w)\W/i))) {
     lang = lang[1];
}

if (!lang && navigator) {
     if (navigator.language) {
         lang = navigator.language;
     } else if (navigator.browserLanguage) {
         lang = navigator.browserLanguage;
     } else if (navigator.systemLanguage) {
         lang = navigator.systemLanguage;
     } else if (navigator.userLanguage) {
         lang = navigator.userLanguage;
     }
     lang = lang.substr(0, 2);
}
esdebug("current language is"+ lang);
esdebug("Language is:"+lang);
/////////////////////////////////////////////////////

/**
 * The data structures and function to enable translation capability in dust templates
 * userTranslations and designTranslations are maps which are likely to be overridden later
 * Their structure is 
 *   {
 *     "msg": {"lang1":"translation1", "lang2":"translation2"},
 *     "another-msg": ...
 *   }
 */ 
var userTranslations=null;
var designTranslations=null;

function _dust(chunk, context, bodies, params){
	//gkdebug("chunk:"+chunk);
	//gkdebug("params:"+JSON.stringify(params));
	msg=params["msg"]
	tr=msg;
	if (translations.hasOwnProperty(params["msg"])) {
	  trs=translations[msg];
	  if (trs.hasOwnProperty(lang))
	     tr=trs[lang]; 
  } else if (designTranslations) {
   	if (designTranslations.hasOwnProperty(params["msg"])) {
   	  trs=designTranslations[msg];
   	  if (trs.hasOwnProperty(lang))
   	     tr=trs[lang]; 
   	}
  }else if (userTranslations) {
   	if (userTranslations.hasOwnProperty(params["msg"])) {
   	  trs=userTranslations[msg];
   	  if (trs.hasOwnProperty(lang))
   	     tr=trs[lang]; 
   	}
  }
  chunk.write(tr);
  return chunk;
}

/**
 * Functions which display/hide a wait cursor/visual
 * These are triggered when API calls started and complete, respectively
 */
function waitStart() {
	esdebug("wait start");
	$("html").css("cursor", 'wait');
	$("#loading-div-background").show();
	// $("#loading-div-background").css({ opacity: 0.8 });
	// $("#loading-div-background").show(); //See http://blog.lavgupta.com/2011/12/jquery-modal-waiting-dialog.html
}

function waitEnd() {
	esdebug("wait end");
	$("html").css("cursor", 'default');
	$("#loading-div-background").hide();
}

/** Toggle an element's (with given DOM id) visibility
*/
function toggleElement(elid){
   if ($("#"+elid).hasClass("hidden"))
      $("#"+elid).removeClass("hidden");
   else
      $("#"+elid).addClass("hidden");
}

/** Prevent Enter in single line input boxes*/
function preventEnter(e){ 
   //esdebug("preventing enter:"+e.which);
   return e.which != 13; 

}

/**Produce sortable order from Jquery UI sortable lists*/
function getSortableOrder(elementid,nullok,serexpression,noint){
   if (nullok) {
      if (document.getElementById(elementid)) {}
      else return [];
   }
   $("#"+elementid).sortable();
   if (serexpression){
      var re=new RegExp("(.+)"+serexpression+"(.+)","");
 	 rawOrder= $("#"+elementid).sortable('serialize',{expression:re});
 	}
   else
 	 rawOrder= $("#"+elementid).sortable('serialize');
 	tmp=rawOrder.split("&");
	esdebug("serialized "+elementid+":*"+rawOrder+"*");
   newOrder=new Array();
   for(i=0;i<tmp.length;i++) {
      x=tmp[i];
      //console.log("item:"+x.split("=")[1]);
      if (noint)
         newOrder.push(x.split("=")[1]);
      else
         newOrder.push(parseInt(x.split("=")[1]));
   }
   esdebug("serialized order:"+newOrder);
   return newOrder;
}

/**
  * This is an elementary function which makes a call to HTTP/JSON API
  * the appdata is sent as JSON payload.  callbackSuccess, callbackFailure
  * functions will be called depending on the returned status. 
  */
function makeAPICall(url, appdata, callbackSuccess, callbackFailure) {
	esdebug("Making API call:"+url+"\n  "+JSON.stringify(appdata));
	waitStart();
   $.ajax({
      type: "POST",
      url: url,
      data: JSON.stringify(appdata),
      contentType: "application/json; charset=utf-8",
      //headers:  {'X-CSRFToken': gkutil_allCookies.getItem('csrftoken')},
      dataType: "json",
      success: function(data) {
      	waitEnd();
         if (data["status"]!=0)
            if (callbackFailure==null)
              alert("Bir işlem hatası oluştu:"+data["message"]);
            else
              callbackFailure(data["status"], data["message"]);
         else
            callbackSuccess(data["result"]); 
          },
      failure: function(errMsg) {
      	waitEnd();
           alert("Bir bağlantı hatası oluştu:"+errMsg);
      }
   });
}


/**
 * Compiles each of the children of a given element (possibly an iframe)
 * as dust templates and registers them with theire ids.
 * If prefix is not nul, the ids are prefixed with it, can be used to
 * protect namespaces.
 */
function ensureTemplate(templateContainer,prefix) {
	//console.log("Container id:"+templateContainer.id+templateContainer.innerHTML);
	if (prefix==null)
		prefix="";
	$(templateContainer).find(".estemplate").each(function(i,v) {
	     tid=prefix+$(v).attr("tid");
			//console.log("child:"+v.id+", html:"+$(v).html());
			//console.log("compiling template:"+tid);
			if (dust.cache[prefix+tid]!=null)
				esdebug("Dust cache already contains the template:"+tid);
			else {
				compiled=dust.compile($(v).html(), tid);
   			dust.loadSource(compiled);
   			$(v).remove(); //Otherwise ids get duplicated!
   			//dustBase[tid]=dust.cache[tid];
   			//dustBase.push({prefix+v.id:
   		}
		});
}

/**
 * When called on page load, finds all toplevel elements of indicated containerClass
 * (default "gk_templateContainer") and compiles them by calling ensure template for each
 */
function autoLoadTemplates(containerClass) {
   if (containerClass==null)
      containerClass="templateContainer";
   $("."+containerClass).each(function(i,v) {
         esdebug("Loaded template Container:"+v.id);
         ensureTemplate(v);
      });
   dust.helpers.count = function(chunk, context, bodies) {
      return bodies.block(chunk, context.push(context.stack.index + 1));
      };
   dust.helpers.gkcount = function(chunk, context, bodies) {
      if (context.stack.index!=null)
         return bodies.block(chunk, context.push(context.stack.index + 1));
      else
         return bodies.block(chunk, context.push(context.get("displayOrder")));
      };
}

//The function which provides citeproc-js rendering of bibliographic data is later to be 
// registered as the actual value of the following variable
var escoreCiteproc=null;

/**
 * Renders the named template (already compiled, e.g by autoLoadTemplates above)
 * with given context and replaces it as the new content of the element
 * with id elementid.
 * Callback is called with element id as parameter, once all is finished.
 */
function renderToElement(templateName,context,elementid,callback) {
	context["i18n"]=_dust;
	if (escoreCiteproc)
	  	context["citeproc"]=escoreCiteproc;
	document.getElementById(elementid).LAST_GK_CONTEXT=context;
	dust.render(templateName,context, function(err, out) {
  		$("#"+elementid).html(out);
  		document.getElementById(elementid).LAST_GK_CONTEXT=context;
  		esdebug("rendered into:"+elementid);
  		if (callback!=null)
  		  callback(context,elementid);
		});
}

//The following map is prepared here and used in the following function
// to cache return values of API calls to prevent
//unnecessary re-calls
var escache={};

/**
 * A shortcut function to make an API call with given data to given URL
 * On its callback, render the result with named template and put the result into
 * element with given id (by calling gktemplating_renderToElement).
 * Callback is passed on to gktemplating_renderToElement.
 */
function callAPIAndRenderToElement(url,data,templateName,elementid,callback,usecache) {
   key=url+JSON.stringify(data);
   if (escache[key]==undefined || !usecache) {
	  makeAPICall(url,data,
       		function(result) {
       		   escache[key]=result;
       			esdebug("API result :"+JSON.stringify(result, undefined, 2));
       			renderToElement(templateName,result,elementid,callback);
       		});
   } else {
      esdebug("Using from cache");
      renderToElement(templateName,escache[key],elementid,callback);
   }
}

/**
 * This is a convenience function which prepares and initiates an ajax call
 * whose payload is to contain file elements.
 */   
function postFiles(url, data, files, callbackSuccess, callbackFailure) {
	var fdata = new FormData();
	fnames="";
	for (i=0;i<files.length;i++) {
      fdata.append(files[i].name, files[i]);
      if (fnames.length>0)
         fnames=fnames+"###";
      fnames=fnames+files[i].name;
   }
   fdata.append(".fnames",fnames);
   for (var k in data)
      fdata.append(k,data[k]);
   esdebug("posting files data:"+JSON.stringify(data));
   waitStart();
	$.ajax({
	         type: "POST",
	         url: url,
	         data: fdata,
	         dataType:"json",
	        	cache: false,
    			contentType: false,
    			//contentType: "application/json; charset=utf-8",
    			processData: false,
    			//headers:  {'X-CSRFToken': gkutil_allCookies.getItem('csrftoken')},
	         success: function(data) {
	            waitEnd();
	            //console.log("Call result data:"+data);
               if (data["status"]!=0) {
                  //console.log("Call to "+url+" resulted in http success but app failure");
                  if (callbackFailure==null)
   	              alert("Bir işlem hatası oluştu:"+data["status"]+","+data["message"]);
   	            else
   	              callbackFailure(data["status"], data["message"]);
   	         } else {
                  //console.log("Call to "+url+" resulted in bot http success and app success");
                  callbackSuccess(data["result"]);
               } 
	          },
	         failure: function(errMsg) {
	              waitEnd();
	              alert("Bir bağlantı hatası oluştu:"+errMsg);
	         }
         });
}