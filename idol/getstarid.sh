


if [ -s start.list ]; then
    mv star.list oldstar.list
fi

rm -f star.list
wget "http://static.mobile.idol001.com/index/star_info_list.json" -O star.list
grep -o -P '(?<="sid":)\d+' star.json > star.id


cat start.id | while read line; do 
    starturl="http://data.android.idol001.com/api_moblie_idol.php?action=star_tuji_list&starid="$line"&page=1&channelId=S002&version=68"
    wget $starturl -O $line"_1.json"
    totalgroup=`grep -o -P '(?<="allcount":)\d+' $line"_1.json" | tail -n 1`
    return
done
