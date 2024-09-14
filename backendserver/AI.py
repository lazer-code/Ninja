import sys
import json

def extract_key_value(sentence):
    attack_keys = {"id", "description", "phase name", "name", "platform", "detection"}
    encryption_types = {"md5", "sha1", "sha256", "sha512", "bcrypt", "aes", "rsa"}
    url_like_words = {"url", "website", "link"}
    ip_address_like_words = {"ip", "ipaddress"}
    file_hash_words = {"hash", "checksum", "filehash"}


    all_keys = attack_keys | encryption_types | url_like_words | ip_address_like_words | file_hash_words

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

def main():
    args = sys.argv[1:]
    try:
        if not args:
            raise ValueError("No input sentence provided")
        sentence = args[0]

        key_value_pairs = extract_key_value(sentence)

        with open('output.txt', 'w') as file:
            json.dump(key_value_pairs, file, indent=3)
    
    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        with open('output.txt', 'w') as file:
            file.write(error_message)

if __name__ == "__main__":
    main()
