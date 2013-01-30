import logging

from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from chronam.core.management.commands import configure_logging

configure_logging('bag_bib_records.config', 'bag_bib_records.log')
_logger = logging.getLogger(__name__)

class Command(BaseCommand):
    data = make_option('--data', 
                       dest='data',
                       default=settings.BIB_STORAGE + '/worldcat_titles',
                       help='Pass directory of data to bag & receive to cts.')
    
    option_list = BaseCommand.option_list + (data,)
    args = ''
    help = ''

    def handle(self, *args, **options):
        data = options['data']

        # cp bib append date to bib
            # mkdir bib-$date (date should be 20130128 format)
            # cp -r bib bib-$date/data
        
        # hit cts to bag & receive content
            # create a new process instance using the "workflow web API"
            # post to /workflow/process_instances and the process instance ID to use is receive1

        # when complete delete bib-$date dir, but leave bib dir
