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


def copy_dir(source=settings.BIB_STORAGE):
    # cp bib dir to new directory w/ the date attached.
    bag_date = date.isoformat(date.today()).replace('-', '')
    abs_location = run('file -b %s' % source)
    abs_location = abs_location.strip("'").split("`")[1]
    destination = '-'.join((abs_location, bag_date))

    if not exists(destination):
        sudo('mkdir %s' % destination)
        sudo('mkdir %s' % destination + '/data')
        sudo('cp -r %s/* %s' % (source, destination + '/data'))

    bag_id = '-'.join(settings.BIB_DIR, bag_date)
    if bag_id == destination.split('/')[-1]:
        return bag_id, destination
    else:
        warn_text = 'Bag id: %s and content path %s do not match.'
        warning = warn_text % (bag_id, destination)
        _logger.warning(warning)


#TODO: MOVE ALL CTS FUNCTIONS into cts.py when complete.
def bag_in_place(cts, directory, bag_id):
    print bag_id
    print directory
    #url = 'service_requests/bag_in_place/can_perform'
    url = 'console/operation/baginplace'
    params = {'bagInstanceKey': bag_id,
              'filepath': directory}
    method = 'post'
    response = cts._request(url, method, params)
    print response
    return response


def receive_bag(cts, cts_host, project_id, directory, bag_id):
    url = 'service_requests/receive_bag/can_perform'
    params = {'projectId': project_id,
              'bagId': bag_id,
              'storageSystemId': cts_host,
              'filepath': directory,
              'description': 'This is a test bag'}
    method = 'get'
    response = cts._request(url, method, params)
    if response['result']:
        method = 'post'
        url = 'service_requests/receive_bag'
        response = cts._request(url, method, params)
    return response


def get_sr_info(cts, sr_key):
    url = 'service_request/%s' % sr_key
    return cts._request(url)


def get_bag_key(cts, project_id, bag_id):
    url = 'bag/%s/%s' % (project_id, bag_id)
    return cts._request(url)


class Command(BaseCommand):
    source_help = 'Pass directory of data to bag & receive to cts.'
    source = make_option('--source', dest='source',
                         default=settings.BIB_STORAGE,
                         help=source_help)

    option_list = BaseCommand.option_list + (source,)
    args = ''
    help = ''

    def handle(self, *args, **options):
        project_id = 'ndnp'
        cts_host = 'terbium'
        #data = options['data']

        # Make copy of bib directory
        bag_id, destination = copy_dir()

        # Make bag in placed
        if destination:
            cts = CTS(settings.CTS_USERNAME, settings.CTS_PASSWORD,
                      settings.CTS_URL)
            #response = receive_bag(cts, cts_host, project_id, destination, bag_id)
            bag_id = 'bib-rec-test9'
            response = get_bag_key(cts, project_id, bag_id)
            bag_key = response['key']
            response = bag_in_place(cts, destination, bag_key)
            print response
            # post to /workflow/process_instances and the process instance ID to use is receive1

        # when complete delete bib-$date dir, but leave bib dir
