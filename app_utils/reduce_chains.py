from Bio.PDB import PDBParser, PDBIO, Select
import sys
class ChainSelect(Select):
    """
    A class that implements the Select interface from Biopython. This class
    is used to select which chains to keep when writing a PDB file.
    """
    def __init__(self, chains_to_keep):
        self.chains_to_keep = chains_to_keep

    def accept_chain(self, chain):
        return chain.id in self.chains_to_keep

def reduce_chains(pdb_filename, output_filename):
    """
    This function reads a PDB file, extracts all chains from the first model,
    and writes the first 8 chains to a new PDB file. If there are more than 8
    chains, the function will remove the extra chains from the middle of the list
    so that the first and last 4 chains are kept.

    Parameters
    ----------
    pdb_filename : str
        The name of the input PDB file.
    output_filename : str
        The name of the output PDB file.

    Returns
    -------
    None
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('protein', pdb_filename)
    
    # Extract all chains from the first model
    model = structure[0]
    chains = list(model.get_chains())
    
    if len(chains) > 8:
        # Calculate how many chains need to be removed
        num_to_remove = len(chains) - 8
        start = num_to_remove // 2
        end = len(chains) - (num_to_remove - start)
        
        # Get the chain IDs to keep
        chains_to_keep = [chain.id for chain in chains[start:end]]
    else:
        chains_to_keep = [chain.id for chain in chains]

    # Write the reduced structure to a new PDB file
    io = PDBIO()
    io.set_structure(structure)
    io.save(output_filename, ChainSelect(chains_to_keep))

if __name__ == '__main__':
    """
    This block of code runs when the script is called from the command line.
    It expects two arguments: the name of the input PDB file and the name of
    the output PDB file.

    Example usage:
    python reduce_chains.py path/to/input.pdb path/to/output.pdb
    """
    pdb_filename = sys.argv[1]
    output_filename = sys.argv[2]
    reduce_chains(pdb_filename, output_filename)

