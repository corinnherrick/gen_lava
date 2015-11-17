import argparse

def main(sentence_file, output_file):
    for line in sentence_file:
        filename = "-".join(line.split()[:3])
        entryID = " ".join(line.split()[3:])
        output_file.write(" ".join([filename, entryID, "\n"]))
        
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create mapping file with actual filenames and then we will add whether the middle frames disambiguate the sentence.")
    parser.add_argument("mapping_file", help="A file in the format \"filenamepiece1 filenamepiece2 filenamepiece3 sentenceID variantID\"")
    parser.add_argument("output_file", help="The output json file.")

    args = parser.parse_args()

    with open(args.mapping_file) as sf:
        with open(args.output_file, "w") as of:
            main(sf, of)


