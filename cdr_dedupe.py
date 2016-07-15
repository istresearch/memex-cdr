#!/usr/bin/env python
from __future__ import print_function
import argparse
import gzip as gz
import json
import hashlib
import datetime
import contextlib

try:
    import redis
except ImportError:
    print("redis is not available")
    pass

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


def get_content_hash(doc):
    """ Return hash of a raw content """
    raw_content = doc.get('raw_content')
    return hashlib.sha1(raw_content.encode('utf8')).hexdigest()


def get_cleaned_url(doc):
    """
    Return a cleaned version of document URL. Currently
    It removes http(s):// and trailing slash.
    """
    url = doc.get('url').strip().split("://", 1)[-1]
    if url[-1:] == '/':
        url = url[:-1]
    return url

def write_output(doc, result_file):
    '''
    Takes in CDR document and writes it
    into the result file
    '''

    # write output
    with gz.open(result_file, 'a') as out:
        out.write(json.dumps(doc) + '\n')
    out.close()

def get_doc_hash(url, content_hash):
    """ Return document hash. It is composed from URL and document hash. """
    h = hashlib.sha1(url.encode('utf8') + content_hash.encode('ascii'))
    return h.hexdigest()


class RedisChecker(object):
    def __init__(self, redis, namespace='dedupe:'):
        self.r = redis
        self.namespace = namespace

    def is_new(self, key):
        """ Return True if key is not seen; add key to seen keys. """
        return bool(r.setnx(self.namespace + key, 1))


class InMemoryChecker(object):
    def __init__(self):
        self.seen = set()

    def is_new(self, key):
        if key in self.seen:
            return False
        self.seen.add(key)
        return True


def deduplicate(input_path, result_path, dupe_checker):
    """
    Iterate over input file, check for duplicates using
    dupe_checker, write unique lines to the result file.
    """
    total_dupes = 0

    with gz.open(input_path, 'rb') as fp:
        with gz.open(result_path, 'ab', compresslevel=4) as out:
            for line in tqdm(fp):
                doc = json.loads(line.decode('utf8'))
                if 'raw_content' not in doc:
                    # document is media, not a crawl
                    continue

                # generate hash objects
                cleaned_url = get_cleaned_url(doc)
                content_hash = get_content_hash(doc)
                doc_hash = get_doc_hash(cleaned_url, content_hash)

                if dupe_checker.is_new(doc_hash):
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

                    out.write(json.dumps(doc).encode('utf8'))
                    out.write(b'\n')
                else:
                    total_dupes += 1

    return total_dupes


@contextlib.contextmanager
def log_time():
    start = datetime.datetime.now()
    yield
    end = datetime.datetime.now()
    total_time = end - start
    print('Took ' + str(total_time))


if __name__ == '__main__':

    desc = 'CDR Deduplication'
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=desc)

    parser.add_argument("--input_file",
                        help="path to the gzip file for testing",
                        required=True)
    parser.add_argument("--result_file",
                        help="path to the deduped output file",
                        required=True)
    parser.add_argument("--redis_prefix",
                        help="Redis key prefix to use for deduplication "
                             "(a string). When not set, Redis is not used.")
    parser.add_argument("--redis_host", help="Redis host", default="localhost")
    parser.add_argument("--redis_port", help="Redis port",
                        default=6379, type=int)
    args = parser.parse_args()

    if args.redis_prefix is not None:
        r = redis.StrictRedis(args.redis_host, args.redis_port)
        r.ping()
        namespace = "dedupe:" + args.redis_prefix + ":"
        dupe_checker = RedisChecker(r, namespace=namespace)
    else:
        dupe_checker = InMemoryChecker()

    # parsed argument for input/result file
    input_file = args.input_file
    result_file = args.result_file

    with log_time():
        total_dupes = deduplicate(input_file, result_file, dupe_checker)
        print(str(total_dupes) + ' duplicates found')
