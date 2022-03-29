import argparse 

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', required=True, help='The destination file for the output of this program')
parser.add_argument('-t', '--text', required=True, help='Text to write to the file')

args = parser.parse_args()

with open(args.output, 'w') as f:
    f.write(args.text+'\n')

print(f'Wrote "{args.text}" to file {args.output}')