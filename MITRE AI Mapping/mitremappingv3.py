import subprocess
import sys
from datetime import datetime

# Function to install required packages
def install_and_import_packages():
    try:
        global SentenceTransformer, util, attack_client, np
        from sentence_transformers import SentenceTransformer, util
        from attackcti import attack_client
        import numpy as np
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "attackcti"])
        from sentence_transformers import SentenceTransformer, util
        from attackcti import attack_client
        import numpy as np

install_and_import_packages()

# Initialize the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Initialize the MITRE ATT&CK client
lift = attack_client()

def find_similar_techniques(sentence):
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    techniques = lift.get_techniques(stix_format=False)
    
    technique_details = []
    for technique in techniques:
        technique_id = technique.get('technique_id', 'No ID')
        technique_name = technique.get('technique', 'No Name')
        technique_description = technique.get('technique_description', 'No Description')
        technique_tactic = ', '.join(technique.get('tactic', []))
        technique_details.append({
            'id': technique_id,
            'name': technique_name,
            'description': technique_description,
            'tactic': technique_tactic
        })

    descriptions_embeddings = model.encode([detail['description'] for detail in technique_details], convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(sentence_embedding, descriptions_embeddings)

    top_matches_indices = np.argsort(-similarities[0])[:3]
    top_matches = [{**technique_details[index], 'similarity': similarities[0][index].item()} for index in top_matches_indices]

    return top_matches

def write_matches_to_file(sentence, matches):
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H%M')
    filename = f"{current_datetime}_techniquematch.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Input Sentence: {sentence}\n\nTop 3 Technique Matches:\n")
        for match in matches:
            file.write(f"ID: {match['id']}, Name: {match['name']}, Tactic: {match['tactic']}, Similarity: {match['similarity']:.4f}\n")
    print(f"Results written to {filename}")

def main():
    # Prompt the user for a sentence describing a cybersecurity attack
    sentence = input("Please enter a sentence describing a cybersecurity attack: ")
    matches = find_similar_techniques(sentence)
    if matches:
        write_matches_to_file(sentence, matches)
    else:
        print("No matches found. Review technique processing and matching logic.")

if __name__ == "__main__":
    main()
