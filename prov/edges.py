from prov.nodes import *


class Relation(Record):

    def __init__(self, identifier=None, attributes=None, account=None):
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


# E to E relations

class wasDerivedFrom(Relation):

    def __init__(self, generatedentity, usedentity, identifier=None, activity=None, generation=None, usage=None,
                 attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.generatedentity = generatedentity
        self.usedentity = usedentity
        self.activity = activity
        self.generation = generation
        self.usage = usage
        self._attributelist.extend([self.generatedentity, self.usedentity, self.activity, self.generation, self.usage])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['generated'] = self.generatedentity
        record_attributes['used'] = self.usedentity
        if self.activity is not None:
            record_attributes['activity'] = self.activity
        if self.generation is not None:
            record_attributes['generation'] = self.generation
        if self.usage is not None:
            record_attributes['usage'] = self.usage
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:generated'] = self.generatedentity._idJSON
        self._json[self._idJSON]['prov:used'] = self.usedentity._idJSON
        if self.activity is not None:
            self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        if self.generation is not None:
            self._json[self._idJSON]['prov:generation'] = self.generation._idJSON
        if self.usage is not None:
            self._json[self._idJSON]['prov:usage'] = self.usage._idJSON
        self._P_cont['wasDerivedFrom'] = self._json
        return self._P_cont


class wasRevisionOf(Relation):

    def __init__(self, newer, older, responsibility=None, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.newer = newer
        self.older = older
        self.responsibility = responsibility
        self._attributelist.extend([self.newer, self.older])
        if self.responsibility is not None:
            self._attributelist.extend([self.responsibility])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['newer'] = self.newer
        record_attributes['older'] = self.older
        if self.responsibility is not None:
            record_attributes['responsibility'] = self.responsibility
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:newer'] = self.newer._idJSON
        self._json[self._idJSON]['prov:older'] = self.older._idJSON
        if self.responsibility is not None:
            self._json[self._idJSON]['prov:responsibility'] = self.responsibility._idJSON
        self._P_cont['wasRevisionOf'] = self._json
        return self._P_cont


class wasQuotedFrom(Relation):

    def __init__(self, quote, quoted, quoterAgent=None, quotedAgent=None, identifier=None, attributes=None,
                 account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.quote = quote
        self.quoted = quoted
        self.quoterAgent = quoterAgent
        self.quotedAgent = quotedAgent
        self._attributelist.extend([self.quote, self.older])
        if self.quoterAgent is not None:
            self._attributelist.extend([self.quoterAgent])
        if self.quotedAgent is not None:
            self._attributelist.extend([self.quotedAgent])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['quote'] = self.quote
        record_attributes['quoted'] = self.quoted
        if self.quoterAgent is not None:
            record_attributes['quoterAgent'] = self.quoterAgent
        if self.quotedAgent is not None:
            record_attributes['quotedAgent'] = self.quotedAgent
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:quote'] = self.quote._idJSON
        self._json[self._idJSON]['prov:quoted'] = self.quoted._idJSON
        if self.quoterAgent is not None:
            self._json[self._idJSON]['prov:quoterAgent'] = self.quoterAgent._idJSON
        if self.quotedAgent is not None:
            self._json[self._idJSON]['prov:quotedAgent'] = self.quotedAgent._idJSON
        self._P_cont['wasQuotedFrom'] = self._json
        return self._P_cont


class hadOriginalSource(Relation):

    def __init__(self, entity, source, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.entity = entity
        self.source = source
        self._attributelist.extend([self.entity, self.source])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['source'] = self.source
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._json[self._idJSON]['prov:source'] = self.source._idJSON
        self._P_cont['hadOriginalSource'] = self._json
        return self._P_cont


class alternateOf(Relation):

    def __init__(self, subject, alternate, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.subject = subject
        self.alternate = alternate
        self._attributelist.extend([self.subject, self.alternate])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['subject'] = self.subject
        record_attributes['alternate'] = self.alternate
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:subject'] = self.subject._idJSON
        self._json[self._idJSON]['prov:alternate'] = self.alternate._idJSON
        self._P_cont['alternateOf'] = self._json
        return self._P_cont


class specializationOf(Relation):

    def __init__(self, subject, specialization, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.subject = subject
        self.specialization = specialization
        self._attributelist.extend([self.subject, self.specialization])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['subject'] = self.subject
        record_attributes['specialization'] = self.specialization
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:subject'] = self.subject._idJSON
        self._json[self._idJSON]['prov:specialization'] = self.specialization._idJSON
        self._P_cont['specializationOf'] = self._json
        return self._P_cont


# E to Ac relations

class wasGeneratedBy(Relation):

    def __init__(self, entity, activity, identifier=None, time=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.entity = entity
        self.activity = activity
        self.time = time
        self._attributelist.extend([self.entity, self.activity, self.time])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['activity'] = self.activity
        if self.time is not None:
            record_attributes['time'] = self.time
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        if self.time is not None:
            self._json[self._idJSON]['prov:time'] = self._convert_value_JSON(self.time, gendxnry)
        self._P_cont['wasGeneratedBy'] = self._json
        return self._P_cont


class wasInvalidatedBy(Relation):

    def __init__(self, entity, activity, identifier=None, time=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.entity = entity
        self.activity = activity
        self.time = time
        self._attributelist.extend([self.entity, self.activity, self.time])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['activity'] = self.activity
        if self.time is not None:
            record_attributes['time'] = self.time
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        if self.time is not None:
            self._json[self._idJSON]['prov:time'] = self._convert_value_JSON(self.time, gendxnry)
        self._P_cont['wasInvalidatedBy'] = self._json
        return self._P_cont


# E to Ag relation

class wasAttributedTo(Relation):

    def __init__(self, entity, agent, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.entity = entity
        self.agent = agent
        self._attributelist.extend([self.entity, self.agent])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['agent'] = self.agent
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._json[self._idJSON]['prov:agent'] = self.agent._idJSON
        self._P_cont['wasAttributedTo'] = self._json
        return self._P_cont


# Ac to E relation

class Used(Relation):

    def __init__(self, activity, entity, identifier=None, time=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.entity = entity
        self.activity = activity
        self.time = time
        self._attributelist.extend([self.entity, self.activity, self.time])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['activity'] = self.activity
        if self.time is not None:
            record_attributes['time'] = self.time
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        if self.time is not None:
            self._json[self._idJSON]['prov:time'] = self._convert_value_JSON(self.time, gendxnry)
        self._P_cont['used'] = self._json
        return self._P_cont


class wasStartedBy(Relation):

    def __init__(self, activity, entity, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.activity = activity
        self.entity = entity
        self._attributelist.extend([self.entity, self.activity])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['activity'] = self.activity
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._P_cont['wasStartedBy'] = self._json
        return self._P_cont


class wasEndedBy(Relation):

    def __init__(self, activity, entity, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.activity = activity
        self.entity = entity
        self._attributelist.extend([self.entity, self.activity])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['entity'] = self.entity
        record_attributes['activity'] = self.activity
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        self._json[self._idJSON]['prov:entity'] = self.entity._idJSON
        self._P_cont['wasEndedBy'] = self._json
        return self._P_cont


# Ac to Ac relations

class wasStartedByActivity(Relation):

    def __init__(self, started, starter, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.started = started
        self.starter = starter
        self._attributelist.extend([self.started, self.starter])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['started'] = self.started
        record_attributes['starter'] = self.starter
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:started'] = self.started._idJSON
        self._json[self._idJSON]['prov:starter'] = self.starter._idJSON
        self._P_cont['wasStartedByActivity'] = self._json
        return self._P_cont


# Ac to Ag relation

class wasAssociatedWith(Relation):

    def __init__(self, activity, agent, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.activity = activity
        self.agent = agent
        self._attributelist.extend([self.agent, self.activity])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['agent'] = self.agent
        record_attributes['activity'] = self.activity
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:activity'] = self.activity._idJSON
        self._json[self._idJSON]['prov:agent'] = self.agent._idJSON
        self._P_cont['wasAssociatedWith'] = self._json
        return self._P_cont


# Ag to Ag relation

class actedOnBehalfOf(Relation):

    def __init__(self, subordinate, responsible, identifier=None, attributes=None, account=None):
        Relation.__init__(self, identifier, attributes, account)
        self.subordinate = subordinate
        self.responsible = responsible
        self._attributelist.extend([self.subordinate, self.responsible])

    def get_record_attributes(self):
        record_attributes = {}
        record_attributes['subordinate'] = self.subordinate
        record_attributes['responsible'] = self.responsible
        return record_attributes

    def to_JSON(self, gendxnry):
        Relation.to_JSON(self, gendxnry)
        self._json[self._idJSON]['prov:subordinate'] = self.subordinate._idJSON
        self._json[self._idJSON]['prov:responsible'] = self.responsible._idJSON
        self._P_cont['actedOnBehalfOf'] = self._json
        return self._P_cont
