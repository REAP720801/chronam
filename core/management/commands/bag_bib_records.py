import logging
from datetime import date
from optparse import make_option

from chronam.core.cts import CTS
#from cts.inventory import Bag
from fabric.api import (env, run, sudo)
from fabric.contrib.files import exists

from django.core.management.base import BaseCommand
from django.conf import settings

from chronam.core.management.commands import configure_logging

configure_logging('bag_bib_records.config', 'bag_bib_records.log')
_logger = logging.getLogger(__name__)

env.host_string = 'localhost'



class Command(BaseCommand):
    source_help = 'Pass directory of data to bag & receive to cts.'
    source = make_option('--source', dest='source',
                         default=settings.BIB_STORAGE,
                         help=source_help)

    option_list = BaseCommand.option_list + (source,)
    args = ''
    help = ''

    def copy_dir(self, source=settings.BIB_STORAGE):
        # cp bib dir to new directory w/ the date attached.
        bag_date = date.isoformat(date.today()).replace('-', '')
        abs_location = run('file -b %s' % source)
        abs_location = abs_location.strip("'").split("`")[1]
        destination = '-'.join((abs_location, bag_date))
    
        if not exists(destination):
            sudo('mkdir %s' % destination)
            sudo('mkdir %s' % destination + '/data')
            sudo('cp -r %s/* %s' % (source, destination + '/data'))
    
        chronam_bag_id = '-'.join((settings.BIB_DIR, bag_date))
        if chronam_bag_id == destination.split('/')[-1]:
            return chronam_bag_id, destination
        else:
            warn_text = 'Bag id: %s and content path %s do not match.'
            warning = warn_text % (bag_id, destination)
            _logger.warning(warning)
    

    def load_variables(self, source, dest):
        for variable_name in source.keys():
            dot_name = "variable.%s" % variable_name
            dest[dot_name] = source[variable_name]        
   
    def handle(self, *args, **options):
        #data = options['data']

        # Make copy of bib directory
        #chronam_bag_id, bag_source = self.copy_dir()
        chronam_bag_id, bag_source = ('bib-dev-20130208', '/vol/ndnp/chronam/bib-dev-20130208') 
        
        # Make bag in placed
        if bag_source:

            bag_note = "Some awesome note."

            cts = CTS(settings.CTS_USERNAME, settings.CTS_PASSWORD,
                      settings.CTS_URL)

            process_variables = settings.CTS_BIB_DEFAULT_VARIABLES 
            process_variables.update({ 
                "bagId" : chronam_bag_id,
                "stagingFilepath" : bag_source,
                "bagNote" : bag_note,
                "performDeleteStagingCopy" : "false",
            })
            data_payload = {"processDefinitionId" : "receive1"}
            self.load_variables(process_variables, data_payload)
            
            url = 'workflow/process_instances'
            method = 'post'
            data = data_payload
            response = cts._request(url, method, params={}, data=data)
            print response
