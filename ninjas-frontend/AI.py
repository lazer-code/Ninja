def extract_key_value(sentence):
    results = {}
    
    attack_keys = ["id", "description", "phase name", "name", "platform", "detection"]
    encryption_types = ["md5", "sha1", "sha256", "sha512", "bcrypt", "aes", "rsa"]
    url_like_words = ["url", "website", "link"]
    ip_address_like_words = ["ip", "ipaddress"]
    file_hash_words = ["hash", "checksum", "filehash"]

    attack_key_set = set(attack_keys)
    encryption_set = set(encryption_types)
    url_set = set(url_like_words)
    ip_set = set(ip_address_like_words)
    file_hash_set = set(file_hash_words)

    all_keys = attack_key_set | encryption_set | url_set | ip_set | file_hash_set

    words = sentence.split()
    
    key_sets = {
        'attack_keys': set(),
        'encryption_types': set(),
        'url_like_words': set(),
        'ip_address_like_words': set(),
        'file_hash_words': set()
    }
    
    i = 0
    while i < len(words):
        word = words[i].lower()
        if word in all_keys:
            if word in attack_key_set:
                key_sets['attack_keys'].add(word)
            elif word in encryption_set:
                key_sets['encryption_types'].add(word)
            elif word in url_set:
                key_sets['url_like_words'].add(word)
            elif word in ip_set:
                key_sets['ip_address_like_words'].add(word)
            elif word in file_hash_set:
                key_sets['file_hash_words'].add(word)
            
            if i + 1 < len(words):
                value = words[i + 1].strip("'\"")
                if word in attack_key_set:
                    results[word] = value
                i += 1  # Skip the next word as it's already used as a value
        i += 1

    # Validate the extracted keys
    if (len(key_sets['encryption_types']) > 0 or 
        len(key_sets['url_like_words']) > 0 or 
        len(key_sets['ip_address_like_words']) > 0 or 
        len(key_sets['file_hash_words']) > 0):
        if (len(key_sets['encryption_types']) > 1 or 
            len(key_sets['url_like_words']) > 1 or 
            len(key_sets['ip_address_like_words']) > 1 or 
            len(key_sets['file_hash_words']) > 1):
            return "Only one request at a time"
        if (len(key_sets['encryption_types']) > 0 and 
            (len(key_sets['url_like_words']) > 0 or 
             len(key_sets['ip_address_like_words']) > 0 or 
             len(key_sets['file_hash_words']) > 0)):
            return "Only one request at a time"
        if (len(key_sets['url_like_words']) > 0 and 
            (len(key_sets['ip_address_like_words']) > 0 or 
             len(key_sets['file_hash_words']) > 0)):
            return "Only one request at a time"
        if (len(key_sets['ip_address_like_words']) > 0 and 
            len(key_sets['file_hash_words']) > 0):
            return "Only one request at a time"
    
    # Check for keys with no values and list them
    missing_data_keys = [key for key in attack_keys if key in key_sets['attack_keys'] and key not in results]
    
    if missing_data_keys:
        return f"Not enough data for: {', '.join(missing_data_keys)}"
    
    return results if len(results) > 0 else "Only one request at a time"

sentence = "name hello platform"

key_value_pairs = extract_key_value(sentence)

if isinstance(key_value_pairs, dict):
    for key, value in key_value_pairs.items():
        print(f"{key}: {value}")
else:
    print(key_value_pairs)
