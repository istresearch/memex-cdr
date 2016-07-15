from __future__ import print_function
import argparse
import gzip as gz
import json
import hashlib
import datetime

def hash_pair(doc):
    '''
    Takes in CDR document, hashes the raw content
    then hashes the url plus the raw content hash
    '''
    
    # gather raw content
    raw_content = doc.get('raw_content')
    
    # remove leading http(s):// and trailing /
    url = doc.get('url').split("://")[-1]
    if url[-1] == '/':
        url = url[:-1]
    
    # take sha1 hash of raw_content
    try:
        content_hash = hashlib.sha1(raw_content).hexdigest()

    # in case of a unicode encoding error, encode as 'utf-8'
    except UnicodeEncodeError:
        content_hash = hashlib.sha1(raw_content.encode('utf-8')).hexdigest()
    
    # generate hash using url and content hash
    hash_pair = hashlib.md5(url+content_hash).hexdigest()
    
    return (hash_pair, url, content_hash)


def write_output(doc, result_file):
    '''
    Takes in CDR document and writes it
    into the result file
    '''

    # write output
    with gz.open(result_file, 'a') as out:
        out.write(json.dumps(doc) + '\n')
    out.close()


if __name__ == '__main__':

    desc='CDR Deduplication'
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=desc)

    parser.add_argument("--input_file", help="path to the gzip file for testing")    
    parser.add_argument("--result_file", help="path to the deduped output file")    
    
    args = parser.parse_args()

    # parsed argument for input/result file
    input_file = args.input_file
    result_file = args.result_file

    # generate input _ids dictionary
    unique_set = set()

    # capture start time
    start = datetime.datetime.now()
    input_count = 0

    # iterate over input file to generate identify uniques
    with gz.open(input_file,'r') as fp:
        for line in fp:
            doc = json.loads(line)

            # ensure the document is a crawl, not media
            if 'raw_content' in doc: 

                # iterate counter
                input_count += 1

                # generate hash objects
                doc_hash_obj = hash_pair(doc)
                doc_hash = doc_hash_obj[0]
                cleaned_url = doc_hash_obj[1]
                content_hash = doc_hash_obj[2]

                # if not in unique set, add to set and write to file
                if doc_hash not in unique_set:

                    # add to set
                    unique_set.add(doc_hash)

                    # add hash and cleaned URL to doc
                    doc['content_hash'] = content_hash
                    doc['cleaned_url'] = cleaned_url

                    # write output
                    write_output(doc, result_file)
            # write media
            else:
                # write output
                write_output(doc, result_file)
        fp.close()

    deduped_count = len(unique_set)
    total_dupes = input_count - deduped_count
    end = datetime.datetime.now()
    total_time = end - start
    
    print(str(total_dupes) + ' duplicates found')
    print('Took ' + str(total_time))