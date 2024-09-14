import sys
import json
import requests

attack_keys = {"id", "description", "phase name", "name", "platform", "detection"}
encryption_types = {"md5", "sha1", "sha256", "sha512", "bcrypt", "aes", "rsa"}
url_like_words = {"url", "website", "link"}
ip_address_like_words = {"ip", "ipaddress"}
file_hash_words = {"hash", "checksum", "filehash"}


all_keys = attack_keys | encryption_types | url_like_words | ip_address_like_words | file_hash_words

def extract_key_value(sentence):
    results = {}
    found_attack_keys = set()
    words = sentence.lower().split()

    i = 0
    while i < len(words):
        word = words[i]
        if word in all_keys:
            if word in attack_keys:
                found_attack_keys.add(word)
            elif found_attack_keys:
                return "Only one request at a time"
            
            if word in attack_keys:
                results['type'] = 'database search'

            elif word not in attack_keys and word in all_keys:
                results['type'] = 'online search'

            j = i + 1
            while j < len(words) and words[j] in {"value", "is", "for", "the", "with", "of"}:
                j += 1
            if j < len(words):
                results[word] = words[j].strip("'\"")
                i = j
        i += 1

    if found_attack_keys:
        if not results:
            return "Only one request at a time"
        missing_data_keys = found_attack_keys - results.keys()
        if missing_data_keys:
            return f"Not enough data for: {', '.join(missing_data_keys)}"
    elif not results:
        return "Unable to process your request"

    return results

def getVirustotalResults(results: dict[str, str]):
    apikey: str = '3704563ee024370204fca6814514fe33d0713f10b4385bbd9d4d8f552fd2fec0'
    for key, value in results.items():
        if key not in attack_keys:
            url = 'https://www.virustotal.com/vtapi/v2/file/report'
            params = {
                'apikey': apikey,
                'resource': value
            }

            response = requests.get(url, params=params)
            data = response.json()

            return data.get('positives', 0) == 0
    
    return False

def main():
    #args = sys.argv
    #if len(args) > 1:
        #args = args[1:]
    try:
        #if not args or len(args) <= 1:
            #sentence = args[0]

            #raise ValueError("No input sentence provided")
        
        sentence = 'md5 5d41402abc4b2a76b9719d911017c592'
        results = extract_key_value(sentence)
        with open('output.txt', 'w') as file:
            result = str(getVirustotalResults(results))
            print(result)
            file.write('results')

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        with open('output.txt', 'w') as file:
            file.write(error_message)

if __name__ == "__main__":
    main()
