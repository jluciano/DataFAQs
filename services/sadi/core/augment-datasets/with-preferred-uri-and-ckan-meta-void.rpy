#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.rpy> .
#
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/augment-datasets/with-preferred-uri-and-ckan-meta-void>
#3>    a datafaqs:FAqTService .
#3> []
#3>   a prov:Activity;
#3>   prov:hadQualifiedAttribution [
#3>      a prov:Attribution;
#3>      prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/core/augment-datasets/with-preferred-uri-and-ckan-meta-void.rpy>;
#3>      prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/augment-datasets/with-preferred-uri-and-ckan-meta-void.rpy>;
#3>   ];
#3> .

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
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class WithPreferredURIAndCKANMetaVoid(sadi.Service):

   # Service metadata.
   label                  = 'with-preferred-uri-and-ckan-meta-void'
   serviceDescriptionText = 'Augment void:Datasets with references to other resources that describe the dataset.'
   comment                = 'References CKAN extra "preferred_uri" and resource "meta/void".'
   serviceNameText        = 'with-preferred-uri-and-ckan-meta-void' # Convention: Match 'name' below.
   name                   = 'with-preferred-uri-and-ckan-meta-void' # This value determines the service URI relative to http://localhost:9090/
                                                                    # Convention: Use the name of this file for this value.
   dev_port = 9099

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
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['WithReferences']

   def process(self, input, output):
   
      # Dereference (e.g., from thedatahub.org)
      store   = surf.Store(reader = 'rdflib', writer = 'rdflib', rdflib_store = 'IOMemory')
      session = surf.Session(store)
      store.load_triples(source = input.subject)
      print str(store.size()) + ' triples from ' + input.subject

  
      # TODO: add in directly asserted PreferredURIs, now that we are accepting any dcat:Dataset
 
      # Dereference the preferred URI (denoted via a CKAN "extra")
      Thing = session.get_class(surf.ns.OWL.Thing)
      prefixes = "prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
      query = 'select ?uri where { <'+input.subject+'> <http://semantic.ckan.net/schema#extra> [ rdf:value ?uri; rdfs:label "preferred_uri"; ] }'
      for row in store.execute_sparql(prefixes+query)['results']['bindings']:
         preferred_uri = row['uri']['value']
         print '  preferred uri: ' + preferred_uri
         output.rdfs_seeAlso.append(Thing(preferred_uri))


      # Include the CKAN "resource" with "format" "meta/void"
      prefixes = 'prefix dc: <http://purl.org/dc/terms/> prefix dcat: <http://www.w3.org/ns/dcat#> prefix moat: <http://moat-project.org/ns#> '
      query = 'select ?uri where { <'+input.subject+'> dcat:distribution [ dcat:accessURL ?uri; dc:format [ moat:taggedWithTag [ moat:name "meta/void" ]]] }'
      for row in store.execute_sparql(prefixes+query)['results']['bindings']:
         void_uri = row['uri']['value']
         print '  void uri: ' + void_uri
         output.rdfs_seeAlso.append(Thing(void_uri))

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = WithPreferredURIAndCKANMetaVoid()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
