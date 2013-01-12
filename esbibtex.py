
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
