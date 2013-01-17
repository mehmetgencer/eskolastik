# -*- coding: utf8 -*-
#See
#app   https://appengine.google.com 
#help  https://developers.google.com/appengine/docs/python/gettingstarted/introduction
from __future__ import with_statement
import os,json, logging, mimetypes, sys
import datetime
import urllib
import wsgiref.handlers
from google.appengine.ext import db, blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from esbibtex import  ESBibtex
MAXNUM_PUBLICATIONS=200
MAXNUM_FILES=300
MAXNUM_SECTIONS=20
MAXNUM_DESIGNS=10
MAXFILESIZEMB=5
def _(msg):
    return msg

def _fixDisplayOrder(oset):
    i=1
    for x in oset.order("displayOrder"):
        if x.displayOrder!=i:
            x.displayOrder=i
            x.save()
        i+=1
def displayOrderSorted(oset):
    def cmp(x,y):
        if x.displayOrder==y.displayOrder:return 0
        elif x.displayOrder<y.displayOrder:return -1
        else:return 1
    return sorted(oset,cmp=cmp)
class EskolastikException(Exception):
    pass
class Profile(db.Model):
  usernick = db.StringProperty() #user.nickname
  name = db.StringProperty()
  code=db.StringProperty(default="")
  title = db.StringProperty(default=_(u"Başlıksız profil"))
  desc = db.TextProperty(default=_(u"Profil açıklaması yok"))
  associations= db.StringListProperty(default=["none","none","none","none","none"])
  chosenDesign=db.StringProperty(default="")
  translations=db.TextProperty(default=_(u"""/*Bölüm başlıklarınızın (ve kullanıyorsanız tasarımlarınızın) gerektirdiği tercümeleri bir Javascript sözlüğü olarak giriniz*/\n{"\n  terim":{"en":"İngilizcesi","de":"Almancası","vs":"vs"},\n}"""))
  def getFiles(self):
      """Return directly profile related files """ 
      return PublicationFile.all().ancestor(self.key())
  def getAllFiles(self):
      """
      Return all files in the profile (i.e. publication files)
      This is probably used to inject file links to profile page, so that 
      the whole profile can be downloaded locally.
      """
      sections=[s for s in self.getSections()]
      pubs=reduce(list.__add__, [[p for p in s.getPublications()] for s in sections],[])
      files=reduce(list.__add__, [[f for f in p.getFiles()] for p in pubs],[])
      return [self.getProfilePicture()] + files 
        
  def asJson(self):
      return {
              "usernick":self.usernick,
              "name":self.name,
              "code":self.code,
              "profilePicture":self.getProfilePictureJson(),
              "title":self.title,
              "profiledesc":self.desc,
              "associations":[{"name":a} for a in self.associations],
              "sections":[s.asJson() for s in displayOrderSorted(self.getSections())],
              "files":[f.asJson() for f in self.getFiles()],
              "designs":[d.asJson() for d in self.getDesigns()],
              "chosenDesign":self.chosenDesign,
              "chosenDesignName":self.getChosenDesignName(),
              "translations":self.translations,
              }
  @staticmethod
  def ensureProfile(user):
      q=Profile.all().filter("usernick =", user.nickname()).get()
      #logging.info("user count for nick '"+user.nickname()+":"+str(len(q)))
      if q is None:
          profile = Profile(usernick=user.nickname(),code=user.nickname())
          profile.put()
      else:
          profile=q
      return profile
  
  def getSections(self):
      return Section.all().ancestor(self.key())
  def getSectionCount(self):
      return self.getSections().count()
  def getDesignCount(self):
      return self.getDesigns().count()
  def getPublicationCount(self):
      return sum([s.getPublications().count() for s in self.getSections()])
  def getPubFileCount(self):
      return sum([s.getPubFileCount() for s in self.getSections()])
  def getDesigns(self):
      return ProfileDesign.all().ancestor(self.key())
  def getProfilePicture(self):
      if ProfilePicture.all().ancestor(self.key()).count():
          return ProfilePicture.all().ancestor(self.key()).get()
      else:
          return None
  def getProfilePictureJson(self):
      if ProfilePicture.all().ancestor(self.key()).count():
          return ProfilePicture.all().ancestor(self.key()).get().asJson()
      else:
          return {}
  def removeExistingPicture(self):
      if ProfilePicture.all().ancestor(self.key()).count():
          ProfilePicture.all().ancestor(self.key()).get().delete()
  def getChosenDesignName(self):
      if self.chosenDesign and db.get(self.chosenDesign):
          return db.get(self.chosenDesign).name
      else:
          return ""
  def getChosenDesign(self):
      if self.chosenDesign:
          d= db.get(self.chosenDesign)
          if d is not None:return d
          else:return None
      else:
          return None
      
class ProfilePicture(db.Model):  
    fileName=db.StringProperty()
    file = db.BlobProperty()
    thumbnail = db.BlobProperty()
    def fileIsBlob(self):
        return False
    def asJson(self):
        return {"fileKey":str(self.key()),"fileUrl":"/files/%s?%s"%(self.fileName, self.key()),
                "fileName":self.fileName}

#  def getPublications(self):
#      return Publication.all().ancestor(self.key())#filter("profileKey =", self.key())

class Section(db.Model):
  #profileKey=db.StringProperty()
  #sid=db.StringProperty()
  title = db.StringProperty()
  desc = db.TextProperty(default=_(u"Bölüm açıklaması yok"))
  displayOrder=db.IntegerProperty()
  def getPublications(self):
      return Publication.all().ancestor(self.key())
  def getPubFileCount(self):
      return sum([p.getFileCount() for p in self.getPublications()])
  def asJson(self):
      return {"title":self.title,"secdesc":self.desc,"sectionKey":self.key().id_or_name(),"publications":[p.asJson() for p in displayOrderSorted(self.getPublications())]}

class Publication(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  isPub = db.BooleanProperty(default=True)
  isSep = db.BooleanProperty(default=False)
  title = db.StringProperty()
  description=db.TextProperty(default=_(u"Yayın açıklaması yok"))
  authors = db.StringListProperty(default=[])
  displayOrder=db.IntegerProperty()
  tstamp = db.DateTimeProperty(auto_now_add=True)  
  pubtype = db.StringProperty(default="article")
  info = db.TextProperty(default=json.dumps(ESBibtex().defaultValues()))
  def getFiles(self):
      return PublicationFile.all().ancestor(self.key())
  def getFileCount(self):
      return self.getFiles().count()
  def asJson(self):
      return {"title":self.title,"publicationKey":self.key().id_or_name(),
              "desc":self.description,
              "pfiles":[f.asJson() for f in displayOrderSorted(self.getFiles())], 
              "pubtype":self.pubtype,
              "pubinfo":json.loads(self.info),
              "ispub":self.isPub,
              "issep":self.isSep,
              "authors":[{"name":a} for a in self.authors],
              }

class PublicationFile(db.Model):
    fileName=db.StringProperty()
    file = db.BlobProperty()
    displayOrder=db.IntegerProperty()
    description=db.TextProperty(default="")
    isBlob=db.BooleanProperty(default=False)
    blobkey=blobstore.BlobReferenceProperty(required=False)
    def fileIsBlob(self):
        return self.isBlob
    def getBlobInfo(self):
        blob_info = blobstore.BlobInfo.get(self.blobkey)
        return blob_info
    def asJson(self):
        if self.isBlob:
            return {"fileKey":str(self.key()),"fileUrl":"/bigfiles/%s?%s"%(self.fileName, self.key()),
                "fileName":self.fileName,"displayOrder":self.displayOrder,
                "description":self.description}
        else:
            return {"fileKey":str(self.key()),"fileUrl":"/files/%s?%s"%(self.fileName, self.key()),
                "fileName":self.fileName,"displayOrder":self.displayOrder,
                "description":self.description}
class ProfileDesign(db.Model):
    name=db.StringProperty()
    desc=db.TextProperty()
    template = db.TextProperty(default="")
    style = db.TextProperty(default="")
    info = db.TextProperty(default="{}")
    #files = db.TextProperty(default="[]")
    def getParentTranslations(self):
        p=self.parent()
        return p.translations
    def briefJson(self):
        return {"designKey":str(self.key()),
                "name":self.name,
                "desc":self.desc,
                "owner":self.parent().usernick
                }
    def asJson(self):
        return {"designKey":str(self.key()),
                "name":self.name,
                "desc":self.desc,
                "template":self.template,
                "style":self.style,
                "info":json.loads(self.info),
                #"files":json.loads(self.files),
                }
#class ProfileDesignUser(db.Model):
#    design=db.StringProperty() #key of actual design
#    infos = db.TextProperty(default="[]")
#    files = db.TextProperty(default="[]")
class MainPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        pcodes=[p.code for p in Profile.all()]
        self.response.out.write(template.render(path, {"pcodes":pcodes}))
class ServeProfileFastTrack(webapp.RequestHandler):
    def get(self,pid):
        q=buildQuery(self.request.query_string)
        designChoice=None
        if "designKey" in q:designChoice=ProfileDesign.get(q["designKey"])
        self.response.out.write(getProfile(pid,designChoice=designChoice))
class ServeProfile(webapp.RequestHandler):
    def get(self):
        pid=self.request.query_string.split("&")[0]
        self.response.out.write(getProfile(pid))
def buildQuery(q):
    d={}
    for x in q.split("&"):
        try:k,v=x.split("=")
        except:k,v=x,""
        d[k]=v
    return d
def getProfile(pid,designChoice=None):
        logging.info("Serving profile"+pid)
        p=Profile.all().filter("usernick =", pid).get()
        if not p:
            p=Profile.all().filter("code =", pid).get()
      #logging.info("user count for nick '"+user.nickname()+":"+str(len(q)))
        if p is None:
            return "No such profile."
        else:
            pid=p.usernick
            if designChoice:design=designChoice
            else:design=p.getChosenDesign()
            if design:
                hasDesign=True
                dtemplate=design.template
                dstyle=design.style
                dtrans=design.getParentTranslations()
            else:
                hasDesign=False
                dtemplate=None
                dstyle=None
                dtrans=None
            logging.info("Serving profile-has design?"+str(hasDesign))
            path = os.path.join(os.path.dirname(__file__), 'templates/show.html')
            #self.response.out.write(template.render(path, {"pid":pid,"hasDesign":hasDesign,"template":dtemplate,"style":dstyle}))
            return template.render(path, {"pid":pid,"hasDesign":hasDesign,"template":dtemplate,"style":dstyle,"translations":p.translations,"designTranslations":dtrans,"profileJson":json.dumps(p.asJson()), "allFiles":p.getAllFiles(),})
class ServeFile(webapp.RequestHandler):
#    def getALT(self,fk,fname):
#        logging.info("Serving file:"+str(fk))
#        blob_info = blobstore.BlobInfo.get(blobstore.BlobKey(fk))
#        type = blob_info.content_type
#        self.response.headers['Content-Type'] = type
#        self.send_blob(blob_info)
    def get(self,fname):
        fk=self.request.query_string
        logging.info("Serving file:"+str(fk))
        pfile=db.get(fk)
        ctype=mimetypes.guess_type(pfile.fileName)[0]
        self.response.headers['Content-Type'] = ctype
        logging.info("content type:"+ctype)
        if not pfile.fileIsBlob():
            self.response.out.write(pfile.file)
        else:
            #h=blobstore_handlers.BlobstoreDownloadHandler(self)
            #h.send_blob(pfile.blobkey)
            blobstore_handlers.BlobstoreDownloadHandler.send_blob(self,BlobInfo.get(pfile.blobkey))
class ServeBlob(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, fname):
        fk=self.request.query_string
        logging.info("Serving file:"+str(fk))
        pfile=db.get(fk)
        ctype=mimetypes.guess_type(pfile.fileName)[0]
        self.response.headers['Content-Type'] = ctype
        logging.info("content type:"+ctype)
        self.send_blob(pfile.blobkey)

class AdminPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        profile=Profile.ensureProfile(user) 
#        for p in profile.getPublications():
#            logging.info("pub:"+str(p.asJson()))
        template_values = {
            "user":user,
            "profile":profile,
            "sections":profile.getSections(),
            #"pubs":profile.getPublications(),
            "esbibtex":ESBibtex(),
            "logoutUrl":users.create_logout_url("/"),
            "profileJson":profile.asJson(),
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
        self.response.out.write(template.render(path, template_values))
class ESAPIBase(webapp.RequestHandler):
    def hasMethod(self,cmd):
        return cmd in self.__class__.methods
    def getMethod(self,cmd):
        return getattr(self,cmd)
    def returnJsonResponse(self,status,errmsg,jresp={}):
        retval={"status":status,"message":errmsg,"result":jresp}
        rstr=json.dumps(retval)
        #debug("Returning API result:"+rstr)
        return rstr
    def getQuery(self):
        r={}
        qs=self.request.query_string.split("&")
        for q in qs:
            logging.info("query:"+str(q))
            k,v=q.split("=")
            if not k in r:
                r[k]=[]
            r[k].append(v)
        return r
    def getPostJson(self):
        return json.loads(self.request.body)
class ESAPIPublic(ESAPIBase):
    methods=["getProfile"]
    def getProfile(self):
        nick=self.getQuery()["profile"][0]
        profile=Profile.all().filter("usernick =", nick).get()
        return profile.asJson()
    def get(self,fn):
        if self.hasMethod(fn):
            try:
                result=self.getMethod(fn)()
                rv=self.returnJsonResponse(0,"OK",jresp=result)
            except EskolastikException:
                rv=self.returnJsonResponse(1,str(sys.exc_info()[0]))
        else:
            rv= self.returnJsonResponse(1,"No such function")
        self.response.headers['Content-Type'] = 'text/plain'
        print("Returning API:",rv)
        self.response.out.write(rv)
    def post(self,fn):
        return self.get(fn)
class ESAPI(ESAPIBase):
    methods=["getProfile","createSection","createPub","deletePub",
             "deleteSec","updatePub","updateSec","addPublicationFiles",
             "deletePubFile","getPublication","updateProfile","createDesign",
             "deleteDesign","updateDesign", "setProfilePicture","getDesignAlternatives",
             "chooseDesign","updateProfileCode"]
    def getProfile(self):
        profile=Profile.ensureProfile(users.get_current_user())
        return profile.asJson()
    def getPublication(self):
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",self.getPostJson()["sectionKey"],
                           "Publication",self.getPostJson()["publicationKey"])
        pub=Publication.get(k)
        return pub.asJson()
#    def getSection(self):
#        s=Section.all().filter("sid =",self.getPostJson()["section"]).get()
#        return s.asJson()
    def createSection(self):
        profile=Profile.ensureProfile(users.get_current_user())
        if profile.getSectionCount()>=MAXNUM_SECTIONS:
            raise EskolastikException(_(u"Bolum sayisi maksimum siniri asiyor"))
        section=Section(parent=profile.key(),title=_(u"Başlıksız bölüm"), displayOrder=profile.getSections().count()+1)
        section.put()
        return {}
    def deleteSec(self):
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",self.getPostJson()["sectionKey"])
        sec=Section.get(k)
        sec.delete()
        _fixDisplayOrder(profile.getSections())
        return {}
    def updateSec(self):
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",self.getPostJson()["sectionKey"])
        sec=Section.get(k)
        sec.title=self.getPostJson()["title"]
        sec.desc=self.getPostJson()["secdesc"]
        sec.save()
        neworder=self.getPostJson()["puborder"]
        o=1
        for pkey in neworder:
            k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",sec.key().id(),
                           "Publication",pkey)
            pub=Publication.get(k)
            if pub.displayOrder!=o:
                pub.displayOrder=o
                pub.save()
            o+=1
        return {}
    def updateProfile(self):
        profile=Profile.ensureProfile(users.get_current_user())
        profile.title=self.getPostJson()["profileName"]
        profile.name=self.getPostJson()["username"]
        profile.desc=self.getPostJson()["profileDesc"]
        profile.associations=self.getPostJson()["associations"]
        profile.translations=self.getPostJson()["translations"]
        profile.save()
        neworder=self.getPostJson()["sectionOrder"]
        o=1
        for skey in neworder:
            k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                               "Section",skey)
            sec=Section.get(k)
            if sec.displayOrder!=o:
                sec.displayOrder=o
                sec.save()
            o+=1
        return {}
    def updateProfileCode(self):
        profile=Profile.ensureProfile(users.get_current_user())
        if not self.getPostJson()["code"].isalnum():
            raise EskolastikException(_(u"Profil kodunda gecersiz karakter veya bosluk kullanmissiniz"))
        if len(self.getPostJson()["code"])<3:
            raise EskolastikException(_(u"Cok kisa bir profil kodu kullanmissiniz"))
        try:
            self.getPostJson()["code"].decode('ascii')
        except UnicodeError:
            raise  EskolastikException(_(u"Web linklerinde kullanilamayacak karakterler (Turkce vb.) kullanmissiniz"))
        pf=Profile.all().filter("code =",self.getPostJson()["code"]).get()
        if pf and pf.usernick!=profile.usernick:
            raise EskolastikException(_(u"Bo kod başkası tarafından kullanılmış"))
        profile.code=self.getPostJson()["code"]
        profile.save()
    def setProfilePicture(self):
        profile=Profile.ensureProfile(users.get_current_user())
        profile.removeExistingPicture()
        for fname in self.request.get(".fnames").split("###"):
            pfile=ProfilePicture(parent=profile.key(),fileName=fname)
            f=self.request.get(fname)
            pfile.file=db.Blob(f)
            img = images.Image(pfile.file)
            img.resize(width=80, height=100)
            img.im_feeling_lucky()
            thumbnail = img.execute_transforms(output_encoding=images.JPEG)
            pfile.thumbnail=thumbnail
            pfile.put()
            logging.info("SAVED FILE:"+fname)
        return {}
    def getDesignAlternatives(self):
        profile=Profile.ensureProfile(users.get_current_user())
        l=[]
        for d in ProfileDesign.all():
            b=d.briefJson()
            if profile.chosenDesign==d.key():
                b["chosen"]=True
            else:
                b["chosen"]=False
            l.append(b)
        return {"designAlternatives":l}
    def chooseDesign(self):
        profile=Profile.ensureProfile(users.get_current_user())
        profile.chosenDesign=self.getPostJson()["designKey"]
        profile.save()
        return {}
    def createPub(self):
        logging.info("will create pub in section request body:"+self.request.body)
        logging.info("will create pub in section:"+str(self.getPostJson()["sectionKey"]))
        #return {}
        ptype=self.getPostJson()["ptype"]
        profile=Profile.ensureProfile(users.get_current_user())
        if profile.getPublicationCount()>=MAXNUM_PUBLICATIONS:
            raise EskolastikException(_(u"Yayin sayisi maksimum siniri asiyor"))
        section=Section.get(db.Key.from_path(profile.key().kind(),profile.key().id(),"Section",self.getPostJson()["sectionKey"]))
        if profile.name:
            authors=[profile.name]
        else:
            authors=[]
        if ptype=="academic":
            publication=Publication(parent=section.key(),title=_(u"Başlıksız yayın"),displayOrder=section.getPublications().count()+1,authors=authors)
        elif ptype=="non-academic":
            publication=Publication(parent=section.key(),title=_(u"Başlıksız yayın"),displayOrder=section.getPublications().count()+1,authors=authors,isPub=False)
        else:#"sep"
            publication=Publication(parent=section.key(),title=_(u"Başlıksız yayın"),displayOrder=section.getPublications().count()+1,authors=authors,isPub=False,isSep=True)
        publication.put()
        return {}
    def deletePub(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",self.getPostJson()["sectionKey"],
                           "Publication",self.getPostJson()["publicationKey"])
        pub=Publication.get(k)
        pub.delete()
        
        section=Section.get(db.Key.from_path(profile.key().kind(),profile.key().id(),"Section",self.getPostJson()["sectionKey"]))
        _fixDisplayOrder(section.getPublications())
        #logging.info("Found section title:"+section.title)
        #k=db.Key.from_path("Publication",self.getPostJson()["publicationKey"],parent=section)
        #pub=Publication.get(k)
        #pub.remove()
        return {}
    def updatePub(self):
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",self.getPostJson()["sectionKey"],
                           "Publication",self.getPostJson()["publicationKey"])
        pub=Publication.get(k)
        pub.info=json.dumps(self.getPostJson()["pubinfo"])
        pub.title=self.getPostJson()["title"]
        pub.description=self.getPostJson()["desc"]
        pub.pubtype=self.getPostJson()["pubtype"]
        pub.isPub=self.getPostJson()["ispub"]
        pub.authors=self.getPostJson()["authors"]
        logging.info("authors:"+str(self.getPostJson()["authors"]))
        pub.save()
        filedesc=self.getPostJson()["filedesc"]
        for fkey in filedesc:
            if not fkey:continue
            pfile=db.get(fkey)
            pfile.description=filedesc[fkey]
            pfile.save()
        newfileorder=self.getPostJson()["fileorder"]
        o=1
        for fkey in newfileorder:
            if not fkey:continue
#            k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
#                           "Section",self.getPostJson()["sectionKey"],
#                           "Publication",self.getPostJson()["publicationKey"],
#                           "PublicationFile",fkey
#                           )
            pfile=db.get(fkey)#PublicationFile.get(k)
            if pfile.displayOrder!=o:
                pfile.displayOrder=o
                pfile.save()
            o+=1
        return {}
    def addPublicationFiles(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        profile=Profile.ensureProfile(users.get_current_user())
        k=db.Key.from_path(profile.key().kind(), profile.key().id(), 
                           "Section",int(self.request.get("sectionKey")),
                           "Publication",int(self.request.get("publicationKey")))
        pub=Publication.get(k)
        logging.info("pkey:"+self.request.get("sectionKey")+","+self.request.get("publicationKey"))
        logging.info(self.request.get(".fnames"))
        for fname in self.request.get(".fnames").split("###"):
            if profile.getPubFileCount()>=MAXNUM_FILES:
                raise EskolastikException(_(u"Dosya sayisi maksimum siniri asiyor"))
            pfile=PublicationFile(parent=pub.key(),fileName=fname,displayOrder=pub.getFiles().count()+1)
            f=self.request.get(fname)
            logging.info("UPLOADED FILE LENGTH:"+str(len(f)))
            if (len(f)>=MAXFILESIZEMB*1024*1024):
                 raise EskolastikException(_(u"Dosya boyutu maksimum siniri (5MB) asiyor"))
            elif (len(f)>=2*1024*1024):# see https://developers.google.com/appengine/docs/python/blobstore/overview
                pfile.isBlob=True
                mtype=mimetypes.guess_type(fname)[0]
                file_name = files.blobstore.create(mime_type=mtype)
                with files.open(file_name, 'a') as bf:
                    bf.write(f)
                files.finalize(file_name)
                pfile.blobkey = files.blobstore.get_blob_key(file_name)
            else:
                pfile.isBlob=False
                pfile.file=db.Blob(f)
            pfile.put()
            logging.info("SAVED FILE:"+fname)
        return {}
    def deletePubFile(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        profile=Profile.ensureProfile(users.get_current_user())
        pfile=db.get(self.getPostJson()["fkey"])
        if pfile.fileIsBlob():
            pfile.blobkey.delete()
        pfile.delete()
        return {}
    def createDesign(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        DESIGNTEMPLATE=u"""
<div class="estemplate" tid="default">
Profile: {title} <br/>
{#sections}
  Bölüm: {.title}<br/>
  Açıklama: {.descdesc}<br/>
  {#publications}
    {.title}
  {/publications}
{/sections}
</div>"""
        profile=Profile.ensureProfile(users.get_current_user())
        if profile.getDesignCount()>=MAXNUM_DESIGNS:
            raise EskolastikException(_(u"Tasarim sayisi siniri asiyor"))
        design=ProfileDesign(parent=profile,name=_(u"Unnamed design"),desc=_(u"No design description"),template=DESIGNTEMPLATE)
        design.put()
        return {}
    def deleteDesign(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        profile=Profile.ensureProfile(users.get_current_user())
        design=db.get(self.getPostJson()["designKey"])
        design.delete()
        return {}
    def updateDesign(self):
        #logging.info("Will delete pub:"+self.getPostJson()["sectionKey"]+" / "+self.getPostJson()["publicationKey"])
        profile=Profile.ensureProfile(users.get_current_user())
        design=db.get(self.getPostJson()["designKey"])
        design.name=self.getPostJson()["name"]
        design.desc=self.getPostJson()["desc"]
        design.template=self.getPostJson()["template"]
        design.style=self.getPostJson()["style"]
        design.save()
        return {}
    def get(self,fn):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        if self.hasMethod(fn):
            try:
                result=self.getMethod(fn)()
                rv=self.returnJsonResponse(0,"OK",jresp=result)
            except EskolastikException as e:
                rv=self.returnJsonResponse(1,str(e))
        else:
            rv= self.returnJsonResponse(1,"No such function")
        self.response.headers['Content-Type'] = 'text/plain'
        print("Returning API:",rv)
        self.response.out.write(rv)
    def post(self,fn):
        return self.get(fn)
    
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/files/(?P<fname>.+)', ServeFile),
                                      ('/bigfiles/(?P<fname>.+)', ServeBlob),
                                      ('/admin', AdminPage),
                                      ("/api/(?P<fn>\w+)$",ESAPI),
                                      ("/apipublic/(?P<fn>\w+)$",ESAPIPublic),
                                      #('/profile', ServeProfile),
                                      ('/(?P<pid>[\w@.]+)/?', ServeProfileFastTrack),
                                      ],
                                     debug=True)

def main():
#    for p in Profile.all():
#        logging.info("init person:"+str(p.asJson()))
#    for p in Publication.all():
#        logging.info("init pub:"+str(p.asJson()))
    run_wsgi_app(application)

if __name__ == "__main__":
    main()