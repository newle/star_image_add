import redis
import sys
from scrapy.utils.request import request_fingerprint 
from scrapy.http import Request



r = redis.StrictRedis(host="10.134.77.90", port=6379, db=0)

for line in sys.stdin:
    fp = request_fingerprint(Request(line.strip(), callback='parse_page')) 
    r.sadd("manfen:dupefilter", fp) 

#fp = request_fingerprint(Request(sys.argv[1], callback='parse_page')) 
#print fp
