# CDR Validation Script
The `cdr_validation.py` script processes a set of JSON lines which have been `gzip`d. It expects that each line within the `gzip`d file contains one CDR formatted object as a string so that it can load it with `json.loads()`. 

## Crawl Documents
For crawl pages, it checks that each object contains the following keys:

* `_id`
* `timestamp`,
* `content_type`
* `crawler`,
* `extracted_metadata`
* `extracted_text`
* `raw_content`
* `team`
* `url`
* `version`

which are defined as required fields per the [CDR Schema wiki page](https://memexproxy.com/wiki/display/MPM/CDR+Schema).

## Media Documents
For media documents, it checks that each object's `obj_parent` exists within the given dataset. For example, if the media's `obj_parent` is `A12DVKD12478Z` then `A12DVKD12478Z` must exist as the `_id` within a crawl document contained within the same dataset. Additionally, it verifies that each object contains the following keys:

* `_id`
* `timestamp`
* `content_type`
* `obj_original_url`
* `obj_parent`
* `obj_stored_url`
* `team`
* `version`

which are defined as required fields per the [CDR Schema wiki page](https://memexproxy.com/wiki/display/MPM/CDR+Schema).

## Executing `cdr_validation.py`
This script requires Python 2.7. To execute it you must provide the path to the input file (`input_file`) and the desired path of the output (`result_file`).

```
python cdr_validation.py --input_file=input.gz --result_file=output
```

The script returns the number of documents that passed, the number that failed, and the time to execute the script. For example:

```
1006 documents passed.
994 documents failed.
Took 0:00:02.337122
```

## Interpreting the `result_file`
The script also writes an output file which is a CSV where the first column is the `_id`, the second column is either `Passed` or `Failed` and if `Failed` there is a third column providing a rationale which is either:

1. `Missing parent document`
2. `Missing required field`