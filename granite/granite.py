#!/usr/bin/env python

#################################################################
#
#    granite
#        Entry point for granite from the command line
#
#        Michele Berselli
#        Harvard Medical School
#        berselli.michele@gmail.com
#
#################################################################


#################################################################
#
#    LIBRARIES
#
#################################################################
import sys, os
import argparse
# Tools
from . import novoCaller
from . import blackList
from . import mpileupCounts
from . import toBgi


#################################################################
#
#    FUNCTIONS
#
#################################################################
#################################################################
#    runner
#################################################################
def main():
    ''' command line wrapper around available tools '''
    # Adding parser and subparsers
    parser = argparse.ArgumentParser(prog='granite', description='GRANITE is a collection of software to call, filter and work with genomic variants')
    subparsers = parser.add_subparsers(dest='func')

    # Add novoCaller to subparsers
    novoCaller_parser = subparsers.add_parser('novoCaller', description='Bayesian de novo variant caller',
                                                help='Bayesian de novo variant caller')

    novoCaller_parser.add_argument('-i', '--inputfile', help='input VCF file', type=file, required=True)
    novoCaller_parser.add_argument('-o', '--outputfile', help='output file to write results as VCF, use .vcf as extension', type=str, required=True)
    novoCaller_parser.add_argument('-u', '--unrelatedfiles', help='TSV file containing ID<TAB>Path/to/file for unrelated files used to train the model (BAM or bgzip and tabix indexed RCK)', type=file, required=True)
    novoCaller_parser.add_argument('-t', '--triofiles', help='TSV file containing ID<TAB>Path/to/file for family files, the PROBAND must be listed as LAST (BAM or bgzip and tabix indexed RCK)', type=file, required=True)
    novoCaller_parser.add_argument('--ppthr', help='threshold to filter by posterior probabilty for de novo calls [0]', type=float, required=False)
    novoCaller_parser.add_argument('--afthr', help='threshold to filter by population allele frequency [1]', type=float, required=False)
    novoCaller_parser.add_argument('--aftag', help='TAG (TAG=<float>) to be used to filter by population allele frequency [novoAF]', type=str, required=False) # novoAF=<float>
    novoCaller_parser.add_argument('--bam', help='by default the program expect bgzip and tabix indexed RCK files for "--triofiles" and "--unrelatedfiles", add this flag if files are in BAM format instead (SLOWER)', action=store_true, required=False)
    novoCaller_parser.add_argument('--MQthr', help='(only with "--bam") minimum mapping quality for an alignment to be used [0]', type=int, required=False)
    novoCaller_parser.add_argument('--BQthr', help='(only with "--bam") minimum base quality for a base to be considered [0]', type=int, required=False)

    # Add mpileupCounts to subparsers
    mpileupCounts_parser = subparsers.add_parser('mpileupCounts', description='samtools wrapper to calculate reads statistics for pileup at each position',
                                                    help='samtools wrapper to calculate reads statistics for pileup at each position')

    mpileupCounts_parser.add_argument('-i', '--inputfile', help='input file in BAM format', type=file, required=True)
    mpileupCounts_parser.add_argument('-o', '--outputfile', help='output file to write results as RCK format (TSV), use .rck as extension', type=str, required=True)
    mpileupCounts_parser.add_argument('-r', '--reference', help='reference file in FASTA format', type=file, required=True)
    mpileupCounts_parser.add_argument('--region', help='region to be analyzed [e.g chr1:1-10000000, 1:1-10000000, chr1, 1], chromosome name must match the reference', type=str, required=False)
    mpileupCounts_parser.add_argument('--MQthr', help='minimum mapping quality for an alignment to be used [0]', type=int, required=False)
    mpileupCounts_parser.add_argument('--BQthr', help='minimum base quality for a base to be considered [13]', type=int, required=False)

    # Add blackList to subparsers
    blackList_parser = subparsers.add_parser('blackList', description='utility to blacklist and filter out variants from input VCF file based on positions set in BGI format file and/or population allele frequency',
                                                help='utility to blacklist and filter out variants from input VCF file based on positions set in BGI format file and/or population allele frequency')

    blackList_parser.add_argument('-i', '--inputfile', help='input VCF file', type=file, required=True)
    blackList_parser.add_argument('-o', '--outputfile', help='output file to write results as VCF, use .vcf as extension', type=str, required=True)
    blackList_parser.add_argument('-b', '--bgifile', help='BGI format file with positions set for blacklist', type=file, required=False)
    blackList_parser.add_argument('--aftag', help='TAG (TAG=<float>) to be used to filter by population allele frequency', type=str, required=False)
    blackList_parser.add_argument('--afthr', help='threshold to filter by population allele frequency [1]', type=float, required=False)

    # Add whiteList to subparsers

    # Add toBgi to subparsers
    toBgi_parser = subparsers.add_parser('toBgi', description='utility that converts counts from bgzip and tabix indexed RCK format into BGI format. Positions are "called" by reads counts or allelic balance for single or multiple files (joint calls) in specified regions',
                                                help='utility that converts counts from bgzip and tabix indexed RCK format into BGI format. Positions are "called" by reads counts or allelic balance for single or multiple files (joint calls) in specified regions')

    toBgi_parser.add_argument('-i', '--inputfiles', help='list of files to be used for the single/joint calling [e.g -i file_1 file_2 ...], expected bgzip and tabix indexed RCK files', type=file, nargs='+')
    toBgi_parser.add_argument('-o', '--outputfile', help='output file to write results as BGI format (binary hdf5), use .bgi as extension', type=str, required=True)
    toBgi_parser.add_argument('-r', '--regionfile', help='file containing regions to be used [e.g chr1:1-10000000, 1:1-10000000, chr1, 1] listed as a column, chromosomes names must match the reference', type=file, required=True)
    toBgi_parser.add_argument('-f', '--chromfile', help='chrom.sizes file containing chromosomes size information', type=file, required=True)
    toBgi_parser.add_argument('--ncores', help='number of cores to be used if multiple regions are specified [1]', type=int, required=False)
    toBgi_parser.add_argument('--bmthr', help='minimum number of bam files with at least "--rdthr" for the alternate allele or having the variant, "calls" by allelic balance, to jointly "call" position', type=int, required=True)
    toBgi_parser.add_argument('--rdthr', help='minimum number of alternate reads to count the bam file in "--bmthr", if not specified "calls" are made by allelic balance', type=int, required=False)
    toBgi_parser.add_argument('--abthr', help='minimum percentage of alternate reads compared to reference reads to count the bam file in "--bmthr" when "calling" by allelic balance [15]', type=int, required=False)

    # Subparsers map
    subparser_map = {
                    'novoCaller': novoCaller_parser,
                    'blackList': blackList_parser,
                    'mpileupCounts': mpileupCounts_parser,
                    'toBgi': toBgi_parser
                    }

    # Checking arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif len(sys.argv) == 2:
        if sys.argv[1] in subparser_map:
            subparser_map[sys.argv[1]].print_help(sys.stderr)
            sys.exit(1)
        else:
            parser.print_help(sys.stderr)
            sys.exit(1)
        #end if
    #end if
    args = vars(parser.parse_args())

    # Call the right tools
    if args['func'] == 'novoCaller':
        pass
    elif args['func'] == 'blackList':
        blackList.main(args)
    elif args['func'] == 'mpileupCounts':
        mpileupCounts.main(args)
    elif args['func'] == 'toBgi':
        toBgi.main(args)
    #end if

#end def


#################################################################
#
#    MAIN
#
#################################################################
if __name__ == "__main__":

    main()

#end if
