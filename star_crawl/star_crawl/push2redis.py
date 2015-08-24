import redis
import sys



r = redis.StrictRedis(host="10.134.77.90", port=6379, db=0)

for line in open(sys.argv[1], "r"):
    r.lpush("idoldaily:start_urls", line.strip()) 
