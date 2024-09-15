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
    found_keys = set()
    words = sentence.lower().split()

    i = 0

    while i < len(words):
        word = words[i]
        if word in all_keys:
            if found_keys:
                return "Only one request at a time"
            
            if word in all_keys:
                found_keys.add(word)

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

    if not results:
        return "Unable to process your request"

    missing_data_keys = found_keys - results.keys()
    if missing_data_keys:
        return f"Not enough data for: {', '.join(missing_data_keys)}"

    return results

def getVirustotalResults(results: dict[str, str]):
    apikey: str = '3704563ee024370204fca6814514fe33d0713f10b4385bbd9d4d8f552fd2fec0'

    for key in results:        
        if key not in attack_keys and key in all_keys:
            url = 'https://www.virustotal.com/vtapi/v2/file/report'
            params = {
                'apikey': apikey,
                'resource': results[key]
            }

            response = requests.get(url, params=params)
            data = response.json()

            result = data.get('positives', 0)

        
            if result > 0:
                return 'Malicious'

            return 'Clean'
              
    return 'Unknown'

def main():
    args = sys.argv

    try:
        if not args or len(args) <= 1:
            raise ValueError("No input sentence provided")
        
        sentence = args[1]

        results = extract_key_value(sentence)
        with open('output.txt', 'w') as file:
            file.write(str(getVirustotalResults(results)))

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        with open('output.txt', 'w') as file:
            file.write(error_message)

if __name__ == "__main__":
    main()
