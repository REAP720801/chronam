import logging
import os
import subprocess

from datetime import date, datetime
from optparse import make_option

from cts.inventory import Bag
from fabric.api import (env, run, settings, sudo,)
from fabric.contrib.files import exists

from django.core.management.base import BaseCommand
from django.conf import settings

from chronam.core.management.commands import configure_logging

configure_logging('bag_bib_records.config', 'bag_bib_records.log')
_logger = logging.getLogger(__name__)

env.host_string = 'localhost'
def get_client(client_parameters=None):
    if client_parameters is not None:
        parms.update(client_parameters)

    return TransferClient(endpoint=settings.CTS_BASE_URL, **parms)

def copy_dir(data=settings.BIB_STORAGE):
    # cp bib dir to new directory w/ the date attached.
    bag_date = date.isoformat(date.today()).replace('-','')
    abs_location = run('file -b %s' % data)
    #abs_location = "symbolic link to `/vol/ndnp/chronam/bib-dev'"
    abs_location = abs_location.strip("'").split("`")[1]
    destination = '-'.join((abs_location, bag_date))

    if not exists(destination):
       
        sudo('mkdir %s' % destination)
        sudo('cp -r %s/. %s' % (data, destination))
        # TODO: Add check to make sure file sizes are the same
        # & everything transferred correctly.
        # du --max-depth=0 %s % data
    else:
        return None

    return destination

def bag_in_place(directory):
    client = get_client()
    client.add_credentials(name=settings.CTS_EDEPOSIT_APPLICATION_USER,
                           password=settings.CTS_EDEPOSIT_APPLICATION_PASSWORD)
    request_params = {'bagInstanceKey': datetime.isoformat(),
                    # TODO: Figure out what path variable is & set it.
                        }
    request_params = urllib.urlencode(request_params)
    request_url = '%sservice_requests/bag_in_place' 
    return


class Command(BaseCommand):
    data = make_option('--data', 
                       dest='data',
                       default=settings.BIB_STORAGE + '/worldcat_titles',
                       help='Pass directory of data to bag & receive to cts.')
    
    option_list = BaseCommand.option_list + (data,)
    args = ''
    help = ''

    def handle(self, *args, **options):
        #data = options['data']
    
        # Make copy of bib directory
        destination = copy_dir()

        # Make bag in place
        if destination:
            bag_in_place(destination)        
        
        # hit cts to bag & receive content
            # create a new process instance using the "workflow web API"
            # post to /workflow/process_instances and the process instance ID to use is receive1

        # when complete delete bib-$date dir, but leave bib dir
