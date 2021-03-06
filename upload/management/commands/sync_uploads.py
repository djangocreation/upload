"""
Uploads backup utility

Sync down uploads referenced in the local database
that aren't present on the local disk.

Speed tips:
 - Set start to PK of the last synced file to save on local file system lookups.
 - Run 2nd terminal tab increasing the start to half way end.

$ ./manage.py sync_uploads [START_PK]
"""
from django.core.management.base import NoArgsCommand
from dashboard.management.commands import spoonfeed
from upload.models import File, make_dir
from django.conf import settings
import urllib.request
import urllib.error
import urllib.parse
import time
import os
import os.path

def download(file):
    """Download files from live server, delete recerds of those that 404.
    """
    url = 'https://www.' + settings.DOMAIN.partition('.')[2] + file.url()
    try:
        print(url)
        return urllib.request.urlopen(url, timeout=15).read()
    except urllib.error.HTTPError as e:
        print(e.code, url)
        file.delete()
        time.sleep(.5)
    except urllib.error.URLError as e:
        print(e.args, url)
    return ''

def get_missing(file):
    """Check file exists, download if not.
    """
    path = file.path()
    if file.ad_id and not os.path.exists(path):
        make_dir(path)
        data = download(file)
        if data:
            f = open(path, 'wb')
            f.write(data)
            f.close()

class Command(NoArgsCommand):
    def handle(self, *args, **options):
        start=0
        if args:
            start=int(args[0])
        print("Syncing uploads from the live to dev starting at PK:%s." % start)
        if settings.DEBUG:
            spoonfeed(File.objects, get_missing, start=start)
        else:
            print("Only run on local dev with DEBUG=True.")
