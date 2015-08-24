


source /search/wangzhen/.bashrc
cd /search/wangzhen/picsearch/task/star_image_add/star_crawl/star_crawl

idoldaily_run=`ps aux | grep "scrapy crawl idoldaily" | grep -v grep | wc -l`

if [ $idoldaily_run -eq 0 ]; then
    workon env27
    scrapy crawl idoldaily > idoldaily.log 2>&1  &
fi

#add seed
python push2redis.py idoldaily.lst




