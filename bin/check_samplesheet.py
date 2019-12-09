#!/usr/bin/env python

#######################################################################
#######################################################################
## Created on August 28th 2019 to check nf-core/nanoseq design file
#######################################################################
#######################################################################

import os
import sys
import argparse

############################################
############################################
## PARSE ARGUMENTS
############################################
############################################

Description = 'Reformat nf-core/nanoseq design file and check its contents.'
Epilog = """Example usage: python check_samplesheet.py <DESIGN_FILE_IN> <DESIGN_FILE_OUT>"""

argParser = argparse.ArgumentParser(description=Description, epilog=Epilog)

## REQUIRED PARAMETERS
argParser.add_argument('DESIGN_FILE_IN', help="Input design file.")
argParser.add_argument('DESIGN_FILE_OUT', help="Output design file.")

## OPTIONAL PARAMETERS
argParser.add_argument('-sd', '--skip_demultiplexing', dest="SKIP_DEMULTIPLEXING", help="Whether demultipexing is to be performed (default: False).",action='store_true')
args = argParser.parse_args()

############################################
############################################
## MAIN SCRIPT
############################################
############################################

ERROR_STR = 'ERROR: Please check samplesheet'
HEADER = ['sample', 'fastq', 'barcode', 'genome']
HEADER_TX = ['sample', 'fastq', 'barcode', 'genome', 'transcriptome']

## CHECK HEADER
fin = open(args.DESIGN_FILE_IN,'r')
header = fin.readline().strip().split(',')
if header != HEADER and header != HEADER_TX:
    print("{} header: {} != {} or {}".format(ERROR_STR,','.join(header),','.join(HEADER),','.join(HEADER_TX)))
    sys.exit(1)

outLines = []
while True:
    line = fin.readline()
    if line:
        lspl = [x.strip() for x in line.strip().split(',')]
        sample,fastq,barcode,genome,txome = lspl

        ## CHECK VALID NUMBER OF COLUMNS PER SAMPLE
        numCols = len([x for x in lspl if x])
        if numCols < 2:
            print("{}: Invalid number of columns (minimum of 2)!\nLine: '{}'".format(ERROR_STR,line.strip()))
            sys.exit(1)

        if sample:
            ## CHECK SAMPLE ID HAS NO SPACES
            if sample.find(' ') != -1:
                print("{}: Sample ID contains spaces!\nLine: '{}'".format(ERROR_STR,line.strip()))
                sys.exit(1)
        else:
            print("{}: Sample ID not specified!\nLine: '{}'".format(ERROR_STR,line.strip()))
            sys.exit(1)

        if barcode:
            ## CHECK BARCODE COLUMN IS INTEGER
            if not barcode.isdigit():
                print("{}: Barcode not an integer!\nLine: '{}'".format(ERROR_STR,line.strip()))
                sys.exit(1)
            else:
                barcode = 'barcode%s' % (barcode.zfill(2))

        if fastq:
            ## CHECK FASTQ FILE EXTENSION
            if fastq[-9:] != '.fastq.gz' and fastq[-6:] != '.fq.gz':
                print("{}: FastQ file has incorrect extension (has to be '.fastq.gz' or '.fq.gz')!\nLine: '{}'".format(ERROR_STR,line.strip()))

        if genome:
            ## CHECK GENOME HAS NO SPACES
            if genome.find(' ') != -1:
                print("{}: Genome field contains spaces!\nLine: '{}'".format(ERROR_STR,line.strip()))
                sys.exit(1)

            ## CHECK GENOME EXTENSION
            if len(genome.split('.')) > 1:
                if genome[-6:] != '.fasta' and genome[-3:] != '.fa' and genome[-9:] != '.fasta.gz' and genome[-6:] != '.fa.gz':
                    print("{}: Genome field incorrect extension (has to be '.fasta' or '.fa' or '.fasta.gz' or '.fa.gz')!\nLine: '{}'".format(ERROR_STR,line.strip()))
                    sys.exit(1)

        if txome:
            ## CHECK TRANSCRIPTOME HAS NO SPACES
            if txome.find(' ') != -1:
                print("{}: Transcriptome field contains spaces!\nLine: '{}'".format(ERROR_STR,line.strip()))
                sys.exit(1)

            # CHECK TRANSCRIPTOME EXTENSION
            if len(txome.split('.')) > 1:
                if txome[-6:] != '.fasta' and txome[-3:] != '.fa' and txome[-9:] != '.fasta.gz' and txome[-6:] != '.fa.gz' and txome[-4:] != '.gtf' and txome[-7:] != '.gtf.gz':
                    print("{}: Genome field incorrect extension (has to be '.fasta' or '.fa' or '.fasta.gz' or '.fa.gz' or '.gtf' or '.gtf.gz')!\nLine: '{}'".format(ERROR_STR,line.strip()))
                    sys.exit(1)

                # CHECK TRANSCRIPTOME DOES NOT INTERFERE WITH GENOME
                if genome and (txome[-4:] != '.gtf' and txome[-7:] != '.gtf.gz'):
                    print("{}: Genome and transcriptome cannot both be of type 'fasta'!\nLine: '{}'".format(ERROR_STR,line.strip()))
                    sys.exit(1)
                if not genome and (txome[-4:] == '.gtf' or txome[-7:] == '.gtf.gz'):
                    print("{}: Genome or transcriptome must be of type 'fasta'!\nLine: '{}'".format(ERROR_STR,line.strip()))
                    sys.exit(1)

        outLines.append([sample,fastq,barcode,genome,txome])
    else:
        fin.close()
        break

if args.SKIP_DEMULTIPLEXING:
    if len(outLines) != 1:
        print("{}: Only a single-line can be specified in samplesheet without barcode information!".format(ERROR_STR))
        sys.exit(1)
    ## USE SAMPLE NAME AS BARCODE WHEN NOT DEMULTIPLEXING
    outLines[0][2] = outLines[0][0]

## WRITE TO FILE
fout = open(args.DESIGN_FILE_OUT,'w')
fout.write(','.join(HEADER) + '\n')
for line in outLines:
    fout.write(','.join(line) + '\n')
fout.close()
