# -*- coding: utf-8 -*-
translations={
              "in":{"tr":u"içinde"},
              "and":{"tr":"ve"},
              "article":{"tr":u"Dergi Makalesi"},
              "inproceedings":{"en":"Conference Proceedings","tr":u"Konferans Bildiri Kitabı"},
              "inbook":{"en":"Book Chapter","tr":u"Kitap Bölümü"},
              "masterthesis":{"en":"Master Thesis","tr":u"Yüksek Lisans Tezi"},
              "phdthesis":{"en":"PhD Thesis","tr":u"Doktora Tezi"},
              "unpublished":{"tr":u"Yayınlanmamış"},
              "techreport":{"en":"Technical Report","tr":"Teknik Rapor"},
              "manual":{"tr":u"Kullanım Kılavuzu"},
              "howpublished":{"en":"link","tr":"link",}
              }
class ESBibtex(object):
    typeFields={
        "article":{
            "required":["journal","year"],
            "optional":["ISSN","DOI","volume", "number", "pages", "month", "note","howpublished"]
            },
        "book":{
            "required":["publisher","year"],
            "optional":["DOI","ISBN","editor","volume","series","edition", "note","howpublished"]
            },
        "booklet":{
            "required":[],
            "optional":["howpublished", "month", "year", "note","howpublished"]
            },
        "inbook":{
            "required":["editor","booktitle","publisher","year"],
            "optional":["DOI","ISBN","volume", "series", "edition","pages", "note","howpublished"]
            },
        "inproceedings":{
            "required":["booktitle","publisher","year"],
            "optional":["DOI","ISBN","editor","volume", "series", "edition","pages","organization", "note","howpublished"]
            },
        "manual":{
            "required":[],
            "optional":["ISBN", "organization", "address", "edition", "month", "year", "note","howpublished"]
            },
        "masterthesis":{
            "required":["school", "year"],
            "optional":[ "address", "note","howpublished"]
            },
        "misc":{
            "required":[],
            "optional":[ "howpublished", "year", "note"]
            },
        "phdthesis":{
            "required":["school", "year"],
            "optional":[ "address", "note","howpublished"]
            },
        "techreport":{
            "required":["institution","year"],
            "optional":["ISBN", "address", "note","howpublished"]
            },
        "unpublished":{
            "required":["year"],
            "optional":[ "note","howpublished"]
            },
    }
    def allFields(self):
        r=[]
        for k,v in self.typeFields.items():
            for x in v["required"]+v["optional"]:
                if not x in r:r.append(x)
        return r
    def makeStyle(self,btype):
        s="";
        parentType="espubfields-"+btype
        all=self.allFields()
        required=self.typeFields[btype]["required"]
        optional=self.typeFields[btype]["optional"]
        allowed=required+optional
        for x in filter(lambda x:x in allowed,all):
            s+=".%s >"%parentType+" ."+x+"{display:inline-block}\n"
        for x in filter(lambda x:x not in allowed,all):
            s+=".%s>"%parentType+" ."+x+"{display: none !important}"       
        return s
    def makeStyles(self):
        s=""
        for k in self.typeFields:
            s+=self.makeStyle(k)
        return s 
    def typeList(self):
        return [k for k in self.typeFields]
    def defaultValues(self):
        r={}
        for x in self.allFields():
            r[x]=""
        return r
    def translate(self,m,lang="en",capitalize=True):
        if m.lower() in translations:
            x=translations[m.lower()]
            if lang in x:
                r=x[lang]
            else:
                r=m.lower()
        else:
            r=m
        if capitalize:
            if r[0]==r.capitalize()[0]:pass
            else:r=r.capitalize()
        return r
    def render(self,pubtype,title,authors,info):
        r="<strong>(%s)</strong> "%self.translate(pubtype)
        for i in range(len(authors)):
            if i>0:
                r+=", "
                if i==len(authors)-1:r+=self.translate("and",capitalize=False)+" "
            r=r+authors[i]
        r+=". <strong><em>"+title+"</em></strong>"
        if info["booktitle"]:
            r+=". "+self.translate("In")+" <em>\"%s\"</em>"%info["booktitle"]
            if info["editor"]:r+=", "+self.translate("ed.")+" "+info["editor"]
        if info["journal"]:r+=". "+info["journal"]
        for x in self.allFields():
            if x in ["booktitle","editor","journal","year"]:continue
            if info[x]:
                r+=". "
                r+=self.translate(x)+": "
                if x=="DOI":
                    r+="<a href='http://dx.doi.org/%s' target='_blank'>%s</a>"%(info[x],info[x])
                elif x=="howpublished":
                    r+="<a href='%s' target='_blank'>%s</a>"%(info[x],info[x])
                else:r+=info[x]
        r+=". <strong>"+info["year"]+"</strong>."
        return r