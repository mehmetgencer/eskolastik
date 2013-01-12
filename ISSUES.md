WISHLIST:
----------

* (DONE)If the page caches all profile info "hardcoded", then a local copy can be used without consulting the server at all. This is an important feature for those who wish to use e-skolastik for managing content, but not for publishing it. For example by inserting the following at the head (after loading escore.js, i.e. using jquery's onload, etc.):
    escache["/api/getProfile{}"] = {...}
* Profile settings must be separated into an expandable section: code, description, name, associations, and add Person's name

BUGS:
-----------
* (DONE: now uses Aloha) Need better editing facility for contentEditable's
* On page reloads, tabs are closed, advanced settings are reset.
* (DONE) For non-default publication type (i.e. not "article"), the page needs to trigger onchange event of publication type selector so that the fields will be properly shown/hidden. Currently it shows "article" fields on load.
* (DONE) Need to hide bibtex fields for non-pub
* (DEFERRED: too small)Need picture thumbnail? 
* school info not displayed in PhD thesis

