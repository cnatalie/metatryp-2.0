import sys
import os.path
import argparse
import logging
from gzip import GzipFile
import sqlite3
import re

db_filename = "C:\Users\David\Documents\WHOI Files\Metatryp\Venter\CN_2012_92pct_seqid_annotation_map_for_mak_saito.sqlite"

def open_venter_db(self, db_filename):
   # used_filename = db_filename
   # if not os.path.exists(used_filename):
   #     used_filename = os.path.join(self.exe_path, used_filename)
   #     if not os.path.exists(used_filename):
    #        sys.exit('Could not file database {}'.format(db_filename))
    self.annotationdb = sqlite3.connect(db_filename)
    self.annotationdb.row_factory = sqlite3.Row  # get rows as dicts


def extract_venter_annotations(self, seq_ids, logger=None):
    if not seq_ids:
        return

    logger.info("sequence ids: %s" % (seq_ids))

    query = """SELECT
        a.seq_id, a.orf_id, a.scaffold_id, a.orf_num, a.annotation,
        a.gene_name, a.orf_tax_level, a.orf_taxonomy, a.orf_tax_id,
        a.contig_tax_level, a.contig_taxonomy, a.contig_tax_id,
        b.annotation AS target_annotation
        FROM annotations AS a
        JOIN annotations as b
            ON a.scaffold_id = b.scaffold_id
        WHERE a.seq_id in (%s)
            AND a.orf_num -3 <= b.orf_num AND a.orf_num +3 >= b.orf_num
        ORDER BY a.seq_id, b.orf_num""" % ','.join('?'*len(seq_ids))

    open_venter_db(self, db_filename)
    cursor = self.annotationdb.cursor()

    cursor.execute(query, seq_ids)


    annot = []
    curr_seq_id = None
    new_seq = None
    tar_annotation = None
    for row in cursor:

        new_seq_id = row[0]

        if new_seq_id != curr_seq_id:
            if new_seq:
                new_seq.append(tar_annotation)
                annot.append(new_seq)
            new_seq = list(row)[:-1]
            curr_seq_id = row[0]
            tar_annotation = row[-1]

        else:
            tar_annotation = tar_annotation + '|' +(row[-1])
       # annot.append(new_seq)
       # logger.info("annotation rows: %s" % (annot))

    returnVal = [[None if x == '' else x for x in c] for c in annot]
    return returnVal