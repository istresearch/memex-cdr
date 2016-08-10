To install the `memex-domains` index template:

    curl -XPUT -u username:password --data @template.json https://cdr-es.istresearch.com:9200/_template/memex-domains

Creation of a new monthly index and updating aliases is handled by `monthly_index.sh`. To manually create a new
`memex-domains_YYYY.MM` monthly index:

    curl -XPUT -u username:password https://cdr-es.istresearch.com:9200/memex-domains_YYYY.MM

To switch the `memex-domains_current` alias from `memex-domains_YYYY.M0` to `memex-domains_YYYY.M1`:

    curl -XPOST -u username:password https://cdr-es.istresearch.com:9200/_aliases -d '
    {
        "actions" : [
            { "remove" : { "index" : "memex-domains_YYYY.M0", "alias" : "memex-domains_current" } },
            { "add" : { "index" : "memex-domains_YYYY.M1", "alias" : "memex-domains_current" } }
        ]
    }'
