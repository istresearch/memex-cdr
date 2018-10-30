import json
import argparse
import gzip as gz
import datetime
import unicodedata

def is_media(doc):
    ''' Checks whether item is media '''
    if 'obj_parent' in doc.keys():
        return True
    else:
        return False

def test_media(doc, _ids, media_fields):
    ''' Checks media fields exist as keys in doc '''    
    parent = doc.get('obj_parent')
    if parent not in _ids:
        return (False, "Missing parent document (field: obj_parent)")
    else:
        return check_required_fields(doc, media_fields)

def test_crawl(doc, crawl_fields):
    return check_required_fields(doc, crawl_fields)

def check_required_fields(doc, crawl_fields):
    ''' Checks crawl fields exist as keys in doc '''
    missing_fields = []
    for field in crawl_fields:
        if field not in doc:
            missing_fields.append(field)
    if missing_fields:
        return (False, "Missing required fields: "+" ".join(missing_fields))
    else:
        return (True, "Passed")

def remove_punctuation(text):
    punctutation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
    return ''.join(x for x in text if unicodedata.category(x) not in punctutation_cats)

def fail_check(doc, termlists):
    content = doc.get('raw_content')
    result = (True, "Passed")
    length = len(content)
    if length < 150:
        result = (False, "Crawl content less than 150 characters")
    elif length >= 150:
        content_nopunct = remove_punctuation(content)
        content_list = content_nopunct.split(" ")
        for list in termlists:
            counter = 0
            listlen = len(list)
            for item in list:
                if item in content_list:
                    counter += 1
            if counter >= listlen:
                result = (False, "Crawl content indicates failed crawl")
        if "requested ad could not be" in content_nopunct:
            result = (False, "Crawl content indicates failed crawl")
    else:
        result = (False, "Crawl content has no length")
    return result

media_fields = ['_id','timestamp','content_type','obj_original_url','obj_parent','obj_stored_url','team','version']
crawl_fields = ['_id','timestamp','content_type','crawler','extracted_metadata','extracted_text','raw_content','team','url','version']
fail_keys = ["warning","return","string"],["error","404"],["domain","expired"],["annonse","ble","ikke","funnet"],["no","se","pudo","encontrar","el","anuncio","solicitado"]

if __name__ == '__main__':

    desc='CDR Validation'
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=desc)

    parser.add_argument("--input_file", help="path to the gzip file for testing")    
    parser.add_argument("--result_file", help="path to the gzip file for testing")    
    
    args = parser.parse_args()

    # parsed argument for input/result file
    input_file = args.input_file
    result_file = args.result_file

    # generate input _ids dictionary
    _ids = set()

    # capture start time
    start = datetime.datetime.now()

    # iterate over input file to generate dictionary of _id's
    with gz.open(input_file,'r') as fp:
        for line in fp:
            _id = json.loads(line).get('_id')
            _ids.add(_id)
        fp.close()
    
    _ids = frozenset(_ids)

    passed = 0
    failed = 0

    # using _ids dictionary, iterate over input and test fields
    with gz.open(input_file,'r') as fp:
        for line in fp:
            doc = json.loads(line)
            _id = doc.get('_id')
            if is_media(doc):
                result = test_media(doc, _ids, media_fields)
            else:
                result = fail_check(doc,fail_keys)
                if result[0]:
                    result = test_crawl(doc, crawl_fields)
                # write output file
            with open(result_file, 'a') as fp:
                if result[0]:
                    res = 'Passed'
                    fp.write(str(_id) + ',' + res + '\n')
                    passed += 1
                else:
                    res = 'Failed'
                    reason = result[1]
                    fp.write(str(_id) + ',' + res + ',' + reason + '\n')
                    failed +=1
            fp.close()                    
    fp.close()

    end = datetime.datetime.now()
    total_time = end - start
    
    print str(passed) + ' documents passed.'
    print str(failed) + ' documents failed.'
    print 'Took ' + str(total_time)