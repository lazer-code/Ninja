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
    key_type_count = 0
    found_attack_keys = set()
    words = sentence.lower().split()

    i = 0
    while i < len(words):
        word = words[i]
        if word in all_keys:
            if word in attack_keys:
                found_attack_keys.add(word)
            elif key_type_count > 0:
                return "Only one request at a time"
            else:
                key_type_count += 1

            j = i + 1
            while j < len(words) and words[j] in {"value", "is", "for", "the", "with", "of"}:
                j += 1
            if j < len(words):
                results[word] = words[j].strip("'\"")
                i = j
        i += 1

    if key_type_count > 0 and found_attack_keys:
        return "Only one request at a time"

    missing_data_keys = found_attack_keys - results.keys()
    if missing_data_keys:
        return f"Not enough data for: {', '.join(missing_data_keys)}"

    return results if results else "Only one request at a time"

def main():
    args = sys.argv[1:]
    sentence = args[0]
    key_value_pairs = extract_key_value(sentence)

    with open ('output.txt', 'w') as file:
        json.dump(key_value_pairs, file, indent=3)
        
if __name__ == "__main__":
    main()
