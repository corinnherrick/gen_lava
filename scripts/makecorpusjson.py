import argparse
from collections import OrderedDict
import json
import itertools
from transform_logical_form import ParenForm

class Sentence:
    def __init__(self, sentenceID, variantID, initialProperties):
        self.properties = initialProperties
        self.properties["sentenceID"] = sentenceID
        self.properties["variantID"] = variantID
        self.sentenceID = sentenceID
        self.variantID = variantID

class Corpus:
    def __init__(self):
        self.sentences = OrderedDict()

    def add_sentence(self, sentence):
        self.sentences[(sentence.sentenceID, sentence.variantID)] = sentence

    def get_sentence(self, sentenceID, variantID):
        return self.sentences[(sentenceID, variantID)]

    def get_sentences_all_variants(self, sentenceID):
        sentences = []
        for (sentenceID, variantID), sentence in self.sentences.items():
            if sentenceID == sentenceID:
                sentences.append(sentence)
        return sentences

    def to_json(self, output_filename):
        with open(output_filename, "w") as out:
            json.dump(map(lambda s: s.properties, self.sentences.values()), out, sort_keys=True, indent=2, separators=(',', ': '))


def parse_sentences_file(filename, corpus):
    with open(filename, "r") as f:
        for line in f:
            start, sentenceID, variantID, text, visual_setup, logical_form, end = line.split("|")
            sentenceID = int(sentenceID)
            variantID = int(variantID)
            text = text.strip()
            visual_setup = visual_setup.strip()
            pf = ParenForm(logical_form.strip(), text)
            logical_form = pf.parse()
            sentence = Sentence(sentenceID, variantID, {"text": text, 
                                                        "visualSetup": visual_setup, 
                                                        "logicalForm": logical_form})
            corpus.add_sentence(sentence)

        
def parse_mapping_file(filename, corpus):
    with open(filename, "r") as f:
        for line in f:
            split_line = line.split()
            no_image = split_line[-1] == 'n'
            if no_image:
                split_line = split_line[:-1]
            if len(split_line) > 5:
                print "When going through mapping file, found line \"%s\"" % line
                continue
            fileID, sentenceID, variantID = split_line
            sentenceID = int(sentenceID)
            variantID = int(variantID)
            try:
                sentence = corpus.get_sentence(sentenceID, variantID)
                sentence.properties["visualFilename"] = fileID
                sentence.properties["image_disambiguates"] = not no_image
            except KeyError:
                print "When going through mapping file, can't find sentence %d %d" % (sentenceID, variantID)
                pass # JSON won't have a visual filename for this sentence.

def parse_matching_file(filename, property_name, corpus):
    with open(filename, "r") as f:
        for line in f:
            sentences = zip(map(int, line.split())[::2], map(int, line.split())[1::2])
            for sentence1, sentence2 in itertools.permutations(sentences, r=2):
                try:
                    sentence1props = corpus.get_sentence(*sentence1).properties
                except KeyError:
                    print "When processing %s, can't find sentence %s" % (property_name, str(sentence1))
                    continue
                if property_name not in sentence1props:
                    sentence1props[property_name] = []
                sentence1props[property_name].append("%d,%d" % sentence2)

def parse_syntactic_tree_file(filename, corpus):
    with open(filename, 'r') as f:
        for line in f:
            if "|" in line:
                ids, tree = line.split("|")
                sentenceID = int(ids.split()[0])
                variantIDs = map(int, ids.split()[1:])
                for variantID in variantIDs:
                    corpus.get_sentence(sentenceID, variantID).properties["syntactic_tree"] = tree.strip()
            else:
                # Only one parse for all variants
                sentenceID, tree = line.split("\t")
                sentenceID = int(sentenceID) + 1 # parser is 0-indexed instead of 1-indexed
                for sentence in corpus.get_sentences_all_variants(sentenceID):
                    sentence.properties["syntactic_tree"] = tree.strip()
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create JSON for corpus.")
    parser.add_argument("sentences_file", help="A file in the format \"|sentenceID|variantID|text|visualSetup|logicalForm|\"")
    parser.add_argument("mapping_file", help="A file in the format \"filenamepiece1 filenamepiece2 filenamepiece3 sentenceID variantID\"")
    parser.add_argument("equivalence_file", help="A file in the format \"sentenceID1 variantID1 sentenceID2 variantID2\"")
    parser.add_argument("contrasts_file", help="A file in the format \"sentenceID1 variantID1 sentenceID2 variantID2\"")
    
    parser.add_argument("syntactic_tree_file", help="A file in the format \"sentenceID variantID1 ... variantIDN | parse_tree\"")

    parser.add_argument("output_file", help="The output json file.")

    args = parser.parse_args()

    corpus = Corpus()
    parse_sentences_file(args.sentences_file, corpus)
    parse_mapping_file(args.mapping_file, corpus)
    parse_matching_file(args.equivalence_file, "equivalentVariants", corpus)
    parse_matching_file(args.contrasts_file, "contrastVariants", corpus)
    parse_syntactic_tree_file(args.syntactic_tree_file, corpus)
    
    corpus.to_json(args.output_file)    
