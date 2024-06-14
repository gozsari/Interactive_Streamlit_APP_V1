import pandas as pd
path_to_gass_preds = '../../results-outputs/cryoEM_structure/cryoEM_GASS-WEB_predictions_2_resids.csv'
path_to_prank_preds = '../../results-outputs/cryoEM_structure/prankweb-aSyn_pH75_ATP_p9mer/structure.pdb_residues.csv'



def form_dict_res_chain(df_prank):
    """
    form a dictionary with key as chain_residue and value as list of tuples of (probability, pocket)

    Parameters
    ----------
    df_prank : pd.DataFrame
        dataframe of prank predictions

    Returns
    -------
    dict_res_chain : dict
        dictionary with key as chain_residue and value as list of tuples of (probability, pocket)
    """
    dict_res_chain = {}
    for row in df_prank.iterrows():
        chain = row[1]["chain"]
        res_id = row[1]["residue_label"]
        chain_res = f"{chain}_{res_id}"
        if chain_res not in dict_res_chain:
            dict_res_chain[chain_res] = []
        dict_res_chain[chain_res].append((row[1]["probability"], row[1]["pocket"]))

    return dict_res_chain

def process_prank_df(df_prank):
    """
    remove leading and trailing whitespaces from column names

    Parameters
    ----------
    df_prank : pd.DataFrame
        dataframe of prank predictions
    
    Returns
    -------
    df_prank : pd.DataFrame
        dataframe of prank predictions with column names stripped of leading and trailing whitespaces
    """
    df_prank.columns = df_prank.columns.str.strip()
    return df_prank

def process_gass_df(df_gass):
    """
    re-organize the columns and drop the '#' column

    Parameters
    ----------
    df_gass : pd.DataFrame
        dataframe of gass predictions

    Returns
    -------
    df_gass : pd.DataFrame
        dataframe of gass predictions
    """
    columns = ['FITNESS', 'ACTIVE_SITE', 'TEMPLATE_PDB', 'TEMPLATE', 'TEMPLATE_EC',	'TEMPLATE_UNIPROT', 'TEMPLATE_RESOLUTION', '#']
    df_gass.columns = columns
    df_gass = df_gass.drop('#', axis=1)
    # reindex the dataframe
    df_gass = df_gass.reset_index(drop=True)
    return df_gass

def add_ec_level_colums(df_common):
    """
    add EC1 and EC2 columns to the dataframe

    Parameters
    ----------
    df_common : pd.DataFrame
        dataframe of common predictions

    Returns
    -------
    df_common : pd.DataFrame
        dataframe of common predictions with EC1 and EC2 columns
    """
    # add a new column that takes first two of EC
    df_common['EC2'] = df_common['EC'].str[:3]
    df_common['EC1'] = df_common['EC'].str[:1]
    return df_common

def produce_common_df(df_prank, df_gass):
    """
    produce a common dataframe from prank and gass dataframes

    Parameters
    ----------
    df_prank : pd.DataFrame
        dataframe of prank predictions

    df_gass : pd.DataFrame
        dataframe of gass predictions

    Returns
    -------
    df_common : pd.DataFrame
        dataframe of common predictions
    """

    df_prank = process_prank_df(df_prank)
    dict_res_chain = form_dict_res_chain(df_prank)
    df_gass = process_gass_df(df_gass)
    list_rows = []
    for row in df_gass.iterrows():
        act_site_ls = row[1]["ACTIVE_SITE"].split(";")
        for act_site in act_site_ls:
            res_name, res_id, chain = act_site.split()
            chain_res = f"{chain}_{res_id}"
            if chain_res in dict_res_chain:
                for prob, pocket in dict_res_chain[chain_res]:
                    list_rows.append((pocket, chain_res, row[1]["TEMPLATE_EC"], 
                                    row[1]["FITNESS"],prob,res_name, res_id, chain ))
    df_common = pd.DataFrame(list_rows, columns=[ "POCKET", "RESIDUE","EC","FITNESS",  "PROB.POCKET", "res_name", "res_id", "chain"])
    df_common = add_ec_level_colums(df_common)
    return df_common

if __name__ == '__main__':
    df_prank = pd.read_csv(path_to_prank_preds)
    df_gass = pd.read_csv(path_to_gass_preds, sep='\t')
    print(df_prank.head())
    print(df_gass.head())
    df_common = produce_common_df(df_prank, df_gass)
    print(df_common.head())
