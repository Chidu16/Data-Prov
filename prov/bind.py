from prov.nodes import *
from prov.edges import *


class Bind():

    def __init__(self):
        self._P_cont = {}
        self._elementlist = []
        self._relationlist = []
        self._namespacedict = {}
        self._implicitnamespace = {'prov': 'http://www.w3.org/ns/prov-dm/',
                                   'xsd': 'http://www.w3.org/2001/XMLSchema-datatypes#'}
        self._accountlist = []
        self._elementkey = 0
        self._relationkey = 0
        self._auto_ns_key = 0
        if self.identifier is None:
            self.identifier = P_qlyname("default", localname="default")
        self._idJSON = None

    def add(self, record):
        if record is not None:
            if isinstance(record, P_typ):
                if record.account is None:
                    self._elementlist.append(record)
                    record.account = self
                elif not record.account.identifier == self.identifier:
                    record.account.add(record)
                elif not record in self._elementlist:
                    self._elementlist.append(record)
            elif isinstance(record, Relation):
                if record.account is None:
                    self._relationlist.append(record)
                    record.account = self
                elif not record.account.identifier == self.identifier:
                    record.account.add(record)
                elif not record in self._elementlist:
                    self._relationlist.append(record)
            elif isinstance(record, Account):
                if record.parentaccount is None:
                    self._accountlist.append(record)
                    record.parentaccount = self
                elif not record.parentaccount.identifier == self.identifier:
                    record.account.add(record)
                elif not record in self._accountlist:
                    self._accountlist.append(record)

    def empty(self):
        self._P_cont = {}
        self._elementlist = []
        self._relationlist = []
        self._namespacedict = {}
        self._accountlist = []
        self._elementkey = 0
        self._relationkey = 0
        self._auto_ns_key = 0
        self._idJSON = None

    def to_JSON(self, gendxnry):
        self._generate_idJSON(gendxnry)
        for element in self._elementlist:
            jsondict = element.to_JSON(gendxnry)
            for key in jsondict:
                if not key in self._P_cont.keys():
                    self._P_cont[key] = {}
                self._P_cont[key].update(jsondict[key])
        for relation in self._relationlist:
            jsondict = relation.to_JSON(gendxnry)
            # print("printing jsondict")
            for key in jsondict:
                if not key in self._P_cont.keys():
                    self._P_cont[key] = {}
                self._P_cont[key].update(jsondict[key])
        for account in self._accountlist:
            if not 'account' in self._P_cont.keys():
                self._P_cont['account'] = {}
            if not account._idJSON in self._P_cont['account'].keys():
                self._P_cont['account'][account._idJSON] = {}
            self._P_cont['account'][account._idJSON].update(account.to_JSON)
        return self._P_cont

    def _generate_idJSON(self, gendxnry):
        for element in self._elementlist:
            if element.identifier is None:
                element._idJSON = self._generate_elem_identifier()
            elif isinstance(element.identifier, P_qlyname):
                # print
                # " generate idJSON for{0}".format(str(element.identifier))
                element._idJSON = element.identifier.qname(gendxnry)
            else:
                element._idJSON = str(element.identifier)
        for relation in self._relationlist:
            if relation.identifier is None:
                relation._idJSON = self._generate_rlat_identifier()
            elif isinstance(relation.identifier, P_qlyname):
                # print
                # "  generate idJSON for{0}".format(str(element.identifier))
                relation._idJSON = relation.identifier.qname(gendxnry)
            else:
                relation._idJSON = str(relation.identifier)
        for account in self._accountlist:
            # print
            # " generate idJSON for{0}".format(str(element.identifier))
            account._idJSON = account.identifier.qname(gendxnry)
            account._generate_idJSON(gendxnry)

    def add_namespace(self, prefix, uri):
        if prefix is "default":
            raise PROVGraph_Error("The namespace prefix 'default' is a reserved by provenance subsystem")
        else:
            self._namespacedict[prefix] = uri


    def get_namespaces(self):
        return self._namespacedict

    def _generate_rlat_identifier(self):
        identifier = "_:RLAT" + str(self._relationkey)
        self._relationkey = self._relationkey + 1
        if self._validate_id(identifier) is False:
            identifier = self._generate_rlat_identifier()
        return identifier

    def _generate_elem_identifier(self):
        identifier = "_:ELEM" + str(self._elementkey)
        self._elementkey = self._elementkey + 1
        if self._validate_id(identifier) is False:
            identifier = self._generate_elem_identifier()
        return identifier

    def _validate_id(self, identifier):
        valid = True
        for element in self._elementlist:
            if element._idJSON == identifier:
                valid = False
        for relation in self._relationlist:
            if relation._idJSON == identifier:
                valid = False
        return valid

    def _validate_qname(self, qname):
        pass  # Put possible Qname validation here

    def get_records(self):
        records = []
        records.extend(self._elementlist)
        records.extend(self._relationlist)
        records.extend(self._accountlist)
        # print(records)
        return records


class P_cont(Bind):

    def __init__(self, defaultnamespace=None):
        self.defaultnamespace = defaultnamespace
        self.identifier = None
        Bind.__init__(self)
        self._visitedrecord = []
        self._gendxnry = {}

    def set_default_namespace(self, defaultnamespace):
        self.defaultnamespace = defaultnamespace

    def get_default_namespace(self):
        return self.defaultnamespace

    @property
    def _create_gendxnry(self):
        # print("inside create")
        self._auto_ns_key = 0
        if not self.defaultnamespace is None:
            self._gendxnry = {'default': self.defaultnamespace}
        self._gendxnry.update(self._implicitnamespace)
        self._gendxnry.update(self._namespacedict)
        self._visitedrecord = []

        return self._gendxnry

    def _generate_prefix(self):
        prefix = "ns" + str(self._auto_ns_key)
        self._auto_ns_key = self._auto_ns_key + 1
        if prefix in self._gendxnry.keys():
            prefix = self._generate_prefix()
        return prefix

    @property
    def to_JSON(self):
        gendxnry = self._create_gendxnry
        # print("inside tojson")
        Bind.to_JSON(self, gendxnry)
        self._P_cont['prefix'] = {}
        for prefix, url in gendxnry.items():
            self._P_cont['prefix'][prefix] = url

        if self.defaultnamespace is not None:
            if not "default" in self._P_cont['prefix'].keys():
                self._P_cont['prefix']['default'] = self.defaultnamespace
        return self._P_cont


class Account(Record, Bind):

    def __init__(self, identifier, asserter, parentaccount=None, attributes=None):
        if identifier is None:
            raise PROVGraph_Error("The identifier of PROV account record must be given as a string or an P_qlyname")
        Record.__init__(self, identifier, attributes, parentaccount)

        Bind.__init__(self)

        if isinstance(asserter, P_qlyname):
            self.asserter = asserter
        elif isinstance(asserter, (str, unicode)):
            self.asserter = P_qlyname(identifier, localname=identifier)
        else:
            raise PROVGraph_Error("The asserter of PROV account record must be given as a string or an P_qlyname")

        self.asserter = asserter
        self._record_attributes = asserter
        self.parentaccount = parentaccount

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['asserter'] = self.asserter
        return record_attributes

    def get_asserter(self):
        return self.asserter

    def to_JSON(self, gendxnry):
        Bind.to_JSON(self, gendxnry)
        self._P_cont['asserter'] = self.asserter.qname(gendxnry)
        for attribute, value in self.list(attributes):
            attrtojson = attribute
            if isinstance(attribute, P_qlyname):
                attrtojson = attribute.qname(gendxnry)
            valuetojson = value
            if isinstance(value, P_qlyname):
                valuetojson = value.qname(gendxnry)
            self._P_cont[attrtojson] = valuetojson
        for attribute in self._P_cont.keys():
            if isinstance(attribute, P_qlyname):
                attrtojson = attribute.qname(gendxnry)
                self._P_cont[attrtojson] = self._P_cont[attribute]
                del self._P_cont[attribute]
        return self._P_cont
