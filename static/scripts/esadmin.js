/**
 * Reload the admin page
 */
function adminReload(skey,pkey) {
   /*if (skey && pkey) {
      callAPIAndRenderToElement("/api/getPublication",{"sectionKey":skey,"publicationKey":pkey},"publication","publi-"+skey+"-"+pkey,function(result){
            adjustElements(result,skey,pkey);         
         });
   } else*/
  //    window.location.reload();
      callAPIAndRenderToElement("/api/getProfile",{},"admin","profile",function(result,elementid){
            adjustElements(result,elementid); 
            Aloha.ready( function() {
                            var $ = Aloha.jQuery;
                            $('.es-editable-aloha').aloha();
                     });  
            if (skey && pkey) {
               esdebug("expanding pub"); 
               togglePubEdit(skey,pkey);
            }  
            //$(".ui-icon").css("display","inline-block !important");     
         });
}

/**
 * This function captures a cumbersome series of adjustments to adjust properties, eventhandlers, etc.
 * of page elements. It exists since these cannot be done with CSS or by other means.
 */
function adjustElements (context,elementid,skey,pkey) {
   $(".peditdropper").each(function(i,v){
         e=document.getElementById(v.id);
         e.sid=v.id.split("-")[1];
         e.pid=v.id.split("-")[2];
         if (e.addEventListener) {
         	e.addEventListener("dragenter",noopHandler,false);
         	e.addEventListener("dragover",noopHandler,false);
         	e.addEventListener("drop",onDropHandler,false);
         } else { //Windows IE
         	e.attachEvent("dragenter",noopHandler,false);
         	e.attachEvent("dragover",noopHandler,false);
         	e.attachEvent("drop",onDropHandler,false);
         }
   });
   $(".publist").each(function(i,v){
         var vid=v.id.split("-")[1];
         $(v).sortable({handle:".dragHandle",stop: function(){
               sectionNeedsSave(vid);//$("#ssave"+vid).removeClass("hidden"); 
            }});
   });
   $(".pubfilelist").each(function(i,v){
         var sid=v.id.split("-")[1];
         var pid=v.id.split("-")[2];
         esdebug("Making pubfilelist sortable:"+sid+"-"+pid+":"+v.id);
         $(v).sortable({handle:".dragHandle",stop: function(){
               publicationNeedsSave(sid,pid);//$("#ssave"+vid).removeClass("hidden"); 
            }});
   });
   $("#seclist").sortable({handle:".dragHandle",stop: function(){
               profileNeedsSave();//$("#ssave"+vid).removeClass("hidden"); 
            }});
   context=document.getElementById(elementid).LAST_GK_CONTEXT;
   //esdebug("adjustment got context from:"+elementid+","+JSON.stringify(context));
   for (var i in context["sections"])  {
      skey=context["sections"][i]["sectionKey"];
      for (var j in context["sections"][i]["publications"]) {
         p=context["sections"][i]["publications"][j];
         pkey=p["publicationKey"]
         pubtype=p["pubtype"]
         //esdebug(JSON.stringify(p));
         document.getElementById("peditptypeoption-"+skey+"-"+pkey+"-"+pubtype).selected="selected";
         if (p["ispub"])
            document.getElementById("peditispub-"+skey+"-"+pkey).checked="true";
      }
   }
   $(".peditispub").each(function(i,v){$(v).trigger("change");});
   $(".peditptype").each(function(i,v){$(v).trigger("change");});
   $(".psaveicon").addClass("hidden");
   esdebug("adjustment finished.");
}

/**
 * Following are handlers for drag-drop elements
 */
function noopHandler(e) {
	//alert("noop");
	esdebug("noop handler");
   e.stopPropagation();
   e.preventDefault();
   //return false;
   };	              

function onDropHandler(e) {
	esdebug("Dropped");
   e.stopPropagation();
   e.preventDefault(); 
   var dt = e.dataTransfer;
   var files = dt.files;
   if (files.length==0) {
   	if (e.dataTransfer.getData("URL").length!=0)
   		found=e.dataTransfer.getData("URL");
   	else
   		found=e.dataTransfer.getData("Text");
   	esdebug("No files dropped! items:"+found);
   } else {
   	addDroppedFiles(this.sid,this.pid,files);
   }
   return false;
   };	              

/**
  * Called when drag-drop of file(s) completed
  */
function addDroppedFiles(sid,pid,pfiles) {
   esdebug("adding dropped files:"+pid+"   ,"+pfiles+ ", number of dropped files:"+pfiles.length);
	postFiles("/api/addPublicationFiles",{"sectionKey":sid,"publicationKey":pid}, pfiles,function(data) {adminReload(sid,pid);});
}

/**
 * Following two functions activates a hidden input-file element
 * then uploads file when file selection is completed
 */
function initAddPubFile(sid,pid) {
   $("#pubfileAdderElem-"+sid+"-"+pid).click();
}

function addPubFile(sid,pid) {
   files=document.getElementById("pubfileAdderElem-"+sid+"-"+pid).files;
   postFiles("/api/addPublicationFiles",{"sectionKey":sid,"publicationKey":pid}, files,function(data) {adminReload(sid,pid);});
}

function createSection(){
	makeAPICall("/api/createSection",{},function(){adminReload();});
}

function createPublicationInSection(skey,ptype){
	//esdebug("Create pub in section:"+section);
	//return;
	makeAPICall("/api/createPub",{"sectionKey":skey,"ptype":ptype},function(){adminReload(skey);});
}

function deletePub(skey,pkey){
   if (!esconfirm("Really delete this publication?"))
      return;
   makeAPICall("/api/deletePub",{"sectionKey":skey,"publicationKey":pkey},function(){adminReload(skey,pkey);});
}
function deleteSec(skey){
   if (!esconfirm("Really delete this section?"))
      return;
   makeAPICall("/api/deleteSec",{"sectionKey":skey},function(){adminReload();});
}

function profileNeedsSave(){
   esdebug("section order changed");
   $("#profilesave").removeClass("hidden");
}
function sectionNeedsSave(skey){
   esdebug("section changed");
   $("#ssave-"+skey).removeClass("hidden");
}

function saveProfile(){
   pname=document.getElementById("profileName").innerHTML;
   pusername=$("#userName").text();
   pdesc=document.getElementById("profiledesc").innerHTML;
   ptrans="{}";//document.getElementById("translations").value;
   assocs=[];
	esdebug("Finding associations:");
	$("#associations .association").each(function(i,v){
	   esdebug("assoc:"+$(v).text());
	   assocs.push($(v).text());
	   });
   makeAPICall("/api/updateProfile",{"profileName":pname,"username":pusername,"profileDesc":pdesc,"associations":assocs,"sectionOrder":getSortableOrder("seclist",true),"translations":ptrans},function(){adminReload();});
}
function saveSection(skey){
   esdebug("New value:"+$("#stitle-"+skey).html());
   makeAPICall("/api/updateSec",{"sectionKey":skey,"title":$("#stitle-"+skey).html(),"secdesc":$("#secdesc-"+skey).html(),"puborder":getSortableOrder("publist-"+skey,true)},function(){adminReload();});
}

/**
  * Called when "is this an academic publication" checkbox is clicked.
  * Needs to hide/show bibliography fields appropriately
  */
function setIsPub(checkbox,skey,pkey) {
      esdebug("ispub:"+checkbox.checked);
      if (checkbox.checked) {
         $("#forpub-"+skey+"-"+pkey).removeClass("hidden");
         $("#nonpub-"+skey+"-"+pkey).addClass("hidden");
      } else {
         $("#forpub-"+skey+"-"+pkey).addClass("hidden");
         $("#nonpub-"+skey+"-"+pkey).removeClass("hidden");
      } 
}
function publicationNeedsSave(skey,pkey){
   esdebug("pub changed:"+skey+"-"+pkey);
   $("#psave-"+skey+"-"+pkey).removeClass("hidden");
}
function togglePubEdit(skey,pkey){
   toggleElement("pedit-"+skey+"-"+pkey);
   }
function savePublication(skey,pkey){
	pubinfo={};
	$("#espubfields-"+skey+"-"+pkey+" .espubfield").each(function (i,v) {
		esdebug("field:"+v.id);
		fname=v.id.split("-")[2];
		esdebug("field:"+v.id+", field:"+fname+",html:"+v.innerHTML);
		pubinfo[fname]=$(v).text();//v.innerHTML;
		});
	pubtype=$("#peditptype-"+skey+"-"+pkey).val();
	pubispub=$("#peditispub-"+skey+"-"+pkey).is(":checked");
	esdebug("pubinfo:"+JSON.stringify(pubinfo));
	esdebug("pubtype:"+pubtype);
	esdebug("pubispub:"+pubispub);
	title=$("#ptitle-"+skey+"-"+pkey).text();
	desc=$("#pdesc-"+skey+"-"+pkey).html();
	authors=[];
	esdebug("Finding authors:");
	$("#pubauthors-"+skey+"-"+pkey+" .pubauthor").each(function(i,v){
	   esdebug("author:"+$(v).text());
	   if ($(v).text().length>0) //Filter out empty authors
	     authors.push($(v).text());
	   });
	esdebug("Finding file descriptions:");
	filedesc={}
	$("#pubfilelist-"+skey+"-"+pkey+" .pfdesc").each(function(i,v){
	   esdebug("file desc:"+$(v).text());
	   filedesc[v.id.split("_____")[1]]=v.innerHTML;
	   });
	makeAPICall("/api/updatePub",{"sectionKey":skey,"publicationKey":pkey,"pubinfo":pubinfo,"pubtype":pubtype,"ispub":pubispub,"title":title,"desc":desc,"fileorder":getSortableOrder("pubfilelist-"+skey+"-"+pkey,true,"_____",true),"authors":authors,"filedesc":filedesc},function(){adminReload(skey,pkey);});
}


function deletePubFile(skey,pkey,fkey){
   makeAPICall("/api/deletePubFile",{"fkey":fkey},function(){adminReload(skey,pkey);});
   return false;
}
function addPubAuthor(skey,pkey){
   $("#authorInserter-"+skey+"-"+pkey).before("<span class='pubauthor es-editable' contenteditable='true'>new author</span>");
   publicationNeedsSave(skey,pkey);
}
function createDesign(){
   makeAPICall("/api/createDesign",{},function(){adminReload();});
   return false;
}
function designNeedsSave(dkey){
	$("#designsave-"+dkey).removeClass("hidden");
	}
function addDesignInfoField(dkey){
   makeAPICall("/api/addDesignInfoField",{"designKey":dkey},function(){adminReload();});
   return false;
}

function saveDesign(dkey){
   makeAPICall("/api/updateDesign",{
   	"designKey":dkey,
   	"name":$("#designname-"+dkey).text(),
   	"desc":$("#designdesc-"+dkey).html(),
   	"template":$("#designtemplate-"+dkey).val(),
   	"style":$("#designstyle-"+dkey).val()
   	},function(){adminReload();});
   return false;
	}
function deleteDesign(dkey){
   if (!esconfirm("Really delete this design?"))
      return;
   makeAPICall("/api/deleteDesign",{"designKey":dkey},function(){adminReload();});
}
function setProfilePicture(){
	postFiles("/api/setProfilePicture",{}, document.getElementById("profilePictureFile").files,function(data) {adminReload();});
	}
function deleteProfilePicture(){
   makeAPICall("/api/deleteProfilePicture",{},function(){adminReload();});
}
	
function showAdvanced(show){
    if (show) 
      $(".advancedSetting").removeClass("hidden");
    else
      $(".advancedSetting").addClass("hidden");
}
function showDesignChoices(){
 callAPIAndRenderToElement("/api/getDesignAlternatives",{},"designChoices","designAlternatives",function(result){
 	toggleElement("designChoices");
	/*$( "#designChoices" ).dialog( {
   	autoOpen:true,
   	height: 500,
      width: 500,
      modal: true,
      closeOnEscape:true,
      title:"Design choices"
      });*/
    });
 }
 function chooseDesign(dkey){
 	makeAPICall("/api/chooseDesign",{"designKey":dkey},function(result){adminReload();});
 }
 function updateProfileCode(){
 	makeAPICall("/api/updateProfileCode",{"code":$("#profileCode").val()},function(result){adminReload();});
 }
 function preview(designkey) {
    $("#previewDiv").removeClass('hidden');
    if (designkey)
      $("#previewDiv").load("/"+username+"?designKey="+designkey);      
    else
      $("#previewDiv").load("/"+username);
    esdebug("Loaded profile: "+username);
 }
 function togglePreview() {
    if ($("#previewDiv").hasClass('hidden')) {
       $("#previewDiv").removeClass('hidden');
       $("#previewDiv").load("/"+username);
       esdebug("Loaded profile: "+username);
    } else 
       $("#previewDiv").addClass('hidden');       
 }
 
 function showProfileSettingsTab() {
    toggleElement("profileSettings");
 }