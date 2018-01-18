"""
Created on January. 05, 2018

@authors: Kenzo-Hugo Hillion and Fabien Mareuil, Institut Pasteur, Paris
@contacts: kehillio@pasteur.fr and fabien.mareuil@pasteur.fr
@project: galaxy
@githuborganization: C3BI
Phylip datatype sniffer
"""

from metadata import MetadataElement

from galaxy import util
from galaxy.datatypes.data import get_file_peek, Text
from galaxy.datatypes.sniff import get_headers
from galaxy.util import nice_size


class Phylip(Text):
    """Phylip format stores a multiple sequence alignment"""
    edam_data = "data_0863"
    edam_format = "format_1997"
    file_ext = "phylip"

    """Add metadata elements"""
    MetadataElement(name="sequences", default=0, desc="Number of sequences", readonly=True,
                    visible=False, optional=True, no_value=0)

    def set_meta(self, dataset, **kwd):
        """
        Set the number of sequences and the number of data lines in dataset.
        """
        dataset.metadata.data_lines = self.count_data_lines(dataset)
        try:
            dataset.metadata.sequences = int(get_headers(dataset.file_name, '\t', count=1)[0][0].split()[0])
        except:
            raise Exception("Header does not correspond to PHYLIP header.")

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.peek = get_file_peek(dataset.file_name, is_multi_byte=is_multi_byte)
            if dataset.metadata.sequences:
                dataset.blurb = "%s sequences" % util.commaify(str(dataset.metadata.sequences))
            else:
                dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def sniff(self, filename):
        """
        All Phylip files starts with the number of sequences so we can use this
        to count the following number of sequences in the first 'stack'
        """
        with open(filename, "r") as f:
            # Get number of sequence from first line
            try:
                nb_seq = int(f.readline().split()[0])
            except:
                return False
            # counts number of sequence from first stack
            count = 0
            for line in f:
                if not line.split():
                    break
                count += 1
                if count > nb_seq:
                    return False
        return count == nb_seq
