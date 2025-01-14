#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/via-sparql-query.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/DataFAQs-Core-Services> .
#3>
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/via-sparql-query>
#3>    a datafaqs:FAqTService .
#3> []
#3>    a prov:Activity;
#3>    prov:hadQualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/via-sparql-query>;
#3>       prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/via-sparql-query.rpy>;
#3>    ];
#3> .
#3> <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/via-sparql-query.rpy>
#3>    foaf:homepage <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-faqts/via-sparql-query.rpy> .

import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')
import ckanclient

import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class FAqTsViaSPARQLQuery(sadi.Service):

   # Service metadata.
   label                  = 'via-sparql-query'
   serviceDescriptionText = 'Augment void:Datasets with references to other resources that describe the dataset.'
   comment                = 'References CKAN extra "preferred_uri" and resource "meta/void".'
   serviceNameText        = 'via-sparql-query' # Convention: Match 'name' below.
   name                   = 'via-sparql-query' # This value determines the service URI relative to http://localhost:9090/
                                               # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

      # Instantiate the CKAN client.
      key = os.environ['X_CKAN_API_Key'] # See https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
      self.ckan = ckanclient.CkanClient(api_key = key)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['QueryToApply']

   def getOutputClass(self):
      return ns.DATAFAQS['FAqTServiceCollection']

   whatQueryQuery = '''
prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix sd:       <http://www.w3.org/ns/sparql-service-description#>
prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>

SELECT ?query_string ?endpoint
WHERE {
   ?apply
      a datafaqs:QueryToApply;
      datafaqs:query   [ rdf:value ?query_string ];
      datafaqs:dataset ?dataset;
   .
   ?service
      a sd:Service;
      sd:availableGraphDescriptions ?dataset;
      sd:endpoint                   ?endpoint;
   .
}
'''

   def process(self, input, output):
  
      print input.subject

      FAqTService = output.session.get_class(ns.DATAFAQS['FAqTService'])
      for queryToApply in input.session.default_store.execute_sparql(self.whatQueryQuery)['results']['bindings']:
         query    = queryToApply['query_string']['value']
         endpoint = queryToApply['endpoint']['value']
      
         #print 'query    = ' + query
         #print 'endpoint = ' + endpoint

         faqt_catalog_store = Store(reader = "sparql_protocol", writer = "sparql_protocol", endpoint = endpoint)

         results = faqt_catalog_store.execute_sparql(query)
         for result in results['results']['bindings']:
            faqt_service = result['service']['value']
            #print '   ' + faqt_service
            faqt_service_r = FAqTService(faqt_service)
            faqt_service_r.rdf_type.append(ns.DATAFAQS['FAqtService'])
            faqt_service_r.save()
            output.dcterms_hasPart.append(faqt_service_r)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = FAqTsViaSPARQLQuery()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   port = 9101
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=port)
