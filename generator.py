import argparse
from distgen import Generator
from distgen.writers import writer

parser = argparse.ArgumentParser(description="Generate a beam using Distgen.")
parser.add_argument("filename", help="Path to the Distgen YAML configuration file")
args = parser.parse_args()

gen = Generator(args.filename, verbose=1)
beam = gen.beam()
writer("openPMD", beam, args.filename.replace("yaml", "h5"))

