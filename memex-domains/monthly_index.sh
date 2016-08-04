#!/bin/bash
# Get command line arguments
if [ $# -lt 2 ]
then
    echo "Not enought arguments given!"
    echo "monthly_index USER PASSWORD"
    exit 1
fi

# Get the current date
curr_date=`date +%Y.%m`
prev_date=`date -d "-2 days" +%Y.%m`
# Create a new index
curl -XPUT "https://$1:$2@cdr-es.istresearch.com:9200/memex-domains_$curr_date"
# Update aliases
curl -XPOST "https://$1:$2@cdr-es.istresearch.com:9200/_aliases" -d "{
    \"actions\" : [
        { \"add\" : { \"index\" : \"memex-domains_$curr_date\", \"alias\" : \"memex-domains_current\" } },
        { \"remove\" : { \"index\" : \"memex-domains_$prev_date\", \"alias\" : \"memex-domains_current\" } },
        { \"add\" : { \"index\" : \"memex-domains_$curr_date\", \"alias\" : \"memex-domains\" } }
    ]
}"
