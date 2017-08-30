import requests
import sys

headers = {
    'Authorization': 'Bearer 7dc9015af922a5260f91538b7d51da027b83f0b0',
}

data_private = [
        ('private', False),
]

private_count = 0
page_count = 1

while page_count > 0:
    data = [
        ('page', page_count),
    ]
    print "In page: " + str(page_count)
    r = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, data=data)
    if r.status_code == 200:
        resp = r.json()
        if len(resp) > 0:
            for p in resp:
                if p['private'] == True:
                    private_count += 1
                    mark_public = requests.put('https://www.strava.com/api/v3/activities/%s' % str(p['id']), headers=headers, data=data_private)
                    if mark_public.status_code == 200:
                        print str(private_count) + " - Marked " + str(p['id']) + " as Public"
        else:
            sys.exit()
    page_count += 1