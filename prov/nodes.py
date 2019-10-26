import datetime


class P_ident(object):

    def __init__(self, name):
        self.name = name

    def uri(self):
        return self.name


class P_qlyname(P_ident):

    def __init__(self, name, prefix=None, nsname=None, localname=None):
        P_ident.__init__(self, name)
        self.nsname = nsname
        self.localname = localname
        self.prefix = prefix

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, P_qlyname):
            return False
        else:
            return self.name == other.name

    def __hash__(self):
        return id(self)

    def qname(self, gendxnry):
        rt = self.name
        for prefix, nsname in gendxnry.items():
            if self.nsname == nsname:
                if prefix != 'default':
                    if self.localname is not None:
                        rt = ":".join((prefix, self.localname))
                else:
                    rt = self.localname
        if not self.nsname in gendxnry.values():
            if self.prefix is not None:
                rt = ":".join((self.prefix, self.localname))
        return rt

    def to_JSON(self, gendxnry):
        qname = self.qname(gendxnry)
        if self.name == qname:
            rt = [qname, "xsd:anyURI"]
        else:
            rt = [qname, "xsd:QName"]
        return rt


class P_nspace(P_ident):

    def __init__(self, prefix, nsname):
        self.prefix = prefix
        self.nsname = str(nsname)

    def __getitem__(self, localname):
        return P_qlyname(self.nsname + localname, self.prefix, self.nsname, localname)


xsd = P_nspace("xsd", 'http://www.w3.org/2001/XMLSchema-datatypes#')
prov = P_nspace("prov", 'http://www.w3.org/ns/prov-dm/')
rdf = P_nspace("rdf", "http://www.w3.org/2000/01/rdf-schema#")


class Record(object):

    def __init__(self, identifier=None, attributes=None, account=None):
        if identifier is not None:
            if isinstance(identifier, P_qlyname):
                self.identifier = identifier
            elif isinstance(identifier, (str)):
                self.identifier = P_qlyname(identifier, localname=identifier)
            else:
                raise PROVGraph_Error("The identifier of PProvenance record shouold be a str")
        else:
            self.identifier = None

        self._record_attributes = {}

        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes

        self.account = account

    def __str__(self):
        if self.identifier is not None:
            return str(self.identifier)
        return None

    def _get_type_JSON(self, value):
        datatype = None
        if isinstance(value, str) or isinstance(value, bool):
            datatype = None
        if isinstance(value, float):
            datatype = xsd["float"]
        if isinstance(value, datetime.datetime):
            datatype = xsd["dateTime"]
        if isinstance(value, int):
            datatype = xsd["integer"]
        if isinstance(value, list):
            datatype = prov["array"]
        return datatype

    def _convert_value_JSON(self, value, gendxnry):
        valuetojson = value
        if isinstance(value, PROVLiteral):
            valuetojson = value.to_JSON(gendxnry)
        elif isinstance(value, P_qlyname):
            valuetojson = value.to_JSON(gendxnry)
        else:
            datatype = self._get_type_JSON(value)
            if datatype is not None:
                if not datatype == prov["array"]:
                    valuetojson = [str(value), datatype.qname(gendxnry)]
                else:
                    newvalue = []
                    islist = False
                    for item in value:
                        if isinstance(item, list):
                            islist = True
                        newvalue.append(self._convert_value_JSON(item, gendxnry))
                    if islist is False:
                        valuetojson = [newvalue, datatype.qname(gendxnry)]
        return valuetojson


class P_typ(Record):

    def __init__(self, identifier=None, attributes=None, account=None):
        if identifier is None:
            raise PROVGraph_Error("An P_typ is always required to have an identifier")
        Record.__init__(self, identifier, attributes, account)

        self._json = {}
        self._P_cont = {}
        self._idJSON = None
        self._attributelist = [self.identifier, self.account, self.attributes]

    def to_JSON(self, gendxnry):
        if isinstance(self.identifier, P_qlyname):
            self._idJSON = self.identifier.qname(gendxnry)
        elif self.identifier is None:
            if self._idJSON is None:
                self._idJSON = 'NoID'
        self._json[self._idJSON] = self.attributes.copy()
        for attribute in self._json[self._idJSON].keys():
            if isinstance(attribute, P_qlyname):
                attrtojson = attribute.qname(gendxnry)
                self._json[self._idJSON][attrtojson] = self._json[self._idJSON][attribute]
                del self._json[self._idJSON][attribute]
        for attribute, value in self._json[self._idJSON].items():
            valuetojson = self._convert_value_JSON(value, gendxnry)
            if valuetojson is not None:
                self._json[self._idJSON][attribute] = valuetojson
        return self._json


class Entity(P_typ):

    def __init__(self, identifier=None, attributes=None, account=None):
        P_typ.__init__(self, identifier, attributes, account)

    def to_JSON(self, gendxnry):
        P_typ.to_JSON(self, gendxnry)
        self._P_cont['entity'] = self._json
        return self._P_cont


class Activity(P_typ):

    def __init__(self, identifier=None, starttime=None, endtime=None, attributes=None, account=None):
        P_typ.__init__(self, identifier, attributes, account)

        self.starttime = starttime
        self.endtime = endtime
        self._attributelist.extend([self.starttime, self.endtime])

    def get_record_attributes(self):
        record_attributes = {}
        if self.starttime is not None:
            record_attributes['startTime'] = self.starttime
        if self.endtime is not None:
            record_attributes['endTime'] = self.endtime
        return record_attributes

    def to_JSON(self, gendxnry):
        P_typ.to_JSON(self, gendxnry)
        if self.starttime is not None:
            self._json[self._idJSON]['prov:starttime'] = self._convert_value_JSON(self.starttime, gendxnry)
        if self.endtime is not None:
            self._json[self._idJSON]['prov:endtime'] = self._convert_value_JSON(self.endtime, gendxnry)
        self._P_cont['activity'] = self._json
        return self._P_cont


class Agent(P_typ):

    def __init__(self, identifier=None, attributes=None, account=None):
        P_typ.__init__(self, identifier, attributes, account)

    def to_JSON(self, gendxnry):
        P_typ.to_JSON(self, gendxnry)
        self._P_cont['agent'] = self._json
        return self._P_cont


class PROVLiteral():

    def __init__(self, value, datatype):
        self.value = value
        self.datatype = datatype
        self._json = []

    def to_JSON(self, gendxnry):
        self._json = []
        if isinstance(self.value, P_qlyname):
            self._json.append(self.value.qname(gendxnry))
        else:
            self._json.append(self.value)
        if isinstance(self.datatype, P_qlyname):
            self._json.append(self.datatype.qname(gendxnry))
        else:
            self._json.append(self.datatype)
        return self._json
