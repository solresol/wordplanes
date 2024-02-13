import argparse

from wordnet_vocab import GloveLookup


def main():
    parser = argparse.ArgumentParser(description='Sanity test for GloveLookup class.')
    parser.add_argument('database_file', type=str, help='Path to the SQLite database file.')
    parser.add_argument('table_name', type=str, help='Name of the table in the SQLite database.')
    parser.add_argument('dimension_size', type=int, help='Dimension size of the word vectors.')
    parser.add_argument('synset_name', type=str, help='Synset name to look up and dump.')
    
    args = parser.parse_args()
    
    glove_lookup = GloveLookup(args.database_file, args.table_name, args.dimension_size)
    glove_output = glove_lookup.dump_as_glove(args.synset_name)
    
    if glove_output:
        print(glove_output)
    else:
        print(f"No vector found for synset: {args.synset_name}")

if __name__ == "__main__":
    main()
