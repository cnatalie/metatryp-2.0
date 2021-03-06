from proteomics import db
import os

import logging
import csv
import argparse
import time

def main():
    """
    Process arguments.
    """
    argparser = argparse.ArgumentParser(description=(
        'Update specialized assembly lineage from CSV file.'))
    argparser.add_argument('--filepath', help=(
        'CSV file containing genome lineage'))

    start_time = time.time()
    logger = logging.getLogger('update_specialized_Assembly_taxons')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    args = argparser.parse_args()

    if args.filepath:
        filename = args.filepath
        print(filename)

        with open(filename, 'rt') as f:
            reader = csv.reader(f)
            try:
                count=1;
                for row in reader:
                    #get the ncbi_id and genome (MAG or SAG) name and update the specialized_assembly table with this info
                    if count > 1:
                        fasta_file_name = row[0]
                        genome_id = os.path.splitext(os.path.basename(fasta_file_name))[0]
                        taxon_name = row[1]
                        print("Genome ID", genome_id)
                        ncbi_id = row[2]
                        tax_group = row[3]
                        tax_kingdom = row[4]
                        tax_phylum = row[5]
                        tax_class = row[6]
                        tax_order = row[7]
                        tax_family = row[8]
                        tax_genus = row[9]
                        tax_species = row[10].replace(".","")
                        ncbi_taxon_name= row[11]

                        cur = db.get_psycopg2_cursor()
                        cur.execute("update specialized_assembly set ncbi_id = %s where genome_name = %s", (ncbi_id, taxon_name))
                        db.psycopg2_connection.commit()

                        s = "."
                        seq = (tax_group, tax_kingdom, tax_phylum,tax_class, tax_order, tax_family, tax_genus,tax_species)
                        hierachy = s.join(seq)
                        hierachy = hierachy.replace(" ", "_")
                        hierachy = hierachy.replace("-", "_")
                        hierachy = hierachy.replace("(", "_")
                        hierachy = hierachy.replace(")", "_")
                        hierachy = hierachy.replace("[", "")
                        hierachy = hierachy.replace("]", "")
                        hierachy = hierachy.replace("'", "")
                        hierachy = hierachy.replace("'", "")
                        hierachy = hierachy.replace("..", ".")
                        hierachy = hierachy.replace(":", ".")
                        if hierachy.endswith("."):
                            hierachy = hierachy[:-1]


                        ncbi_url = "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+ncbi_id
                        print("URL: ",ncbi_url)

                        cur.execute("select nt.ncbi_id from ncbi_taxonomy nt where nt.ncbi_id = %s;", (ncbi_id,))
                        taxon_result = cur.fetchone()
                        if taxon_result is None:
                            cur.execute(
                                "insert into ncbi_taxonomy(ncbi_id, tax_group, tax_kingdom, tax_phylum, tax_class, "
                                          "tax_order, tax_family, tax_genus, tax_species, hierachy, ncbi_url)"
                                          " values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",  (ncbi_id, tax_group, tax_kingdom, tax_phylum, tax_class, tax_order, tax_family, tax_genus, tax_species, hierachy, ncbi_url))
                            db.psycopg2_connection.commit()
                        else:
                            cur.execute("update ncbi_taxonomy set ncbi_id = %s, tax_group = %s, tax_kingdom = %s, tax_phylum = %s, tax_class = %s, "
                                        "tax_order = %s, tax_family = %s, tax_genus = %s, tax_species = %s, hierachy = %s, ncbi_url = %s where ncbi_id=%s", (
                                        ncbi_id, tax_group, tax_kingdom, tax_phylum, tax_class, tax_order, tax_family, tax_genus, tax_species, hierachy, ncbi_url, ncbi_id))
                            db.psycopg2_connection.commit()


                    count = count + 1
            except csv.Error as e:
               logger.error('file %s, line %d: %s' % (filename, reader.line_num, e))


if __name__ == '__main__':
    main()

