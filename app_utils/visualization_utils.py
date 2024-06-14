import matplotlib.pyplot as plt
import seaborn as sns
import py3Dmol
def heatmap_df(df, index, columns, values):

    # Create the pivot table
    pivot_table = df.pivot_table(index=index, columns=columns, values=values, aggfunc='mean')

    # Plot the heatmap
    plt.figure(figsize=(20, 15))
    sns.heatmap(pivot_table, cmap='viridis', cbar_kws={'label': 'Fitness'}, xticklabels=1, yticklabels=1)
    plt.xlabel(columns)
    plt.ylabel(index)

    return plt


# Function to generate py3Dmol view
def generate_pdb_view(pdb_data, residue_numbers=None, chains=None, color='red', radius=1.0):
    
    view = py3Dmol.view(width=800, height=600)
    view.addModel(pdb_data, 'pdb')
    view.setBackgroundColor('white')
    view.setStyle({'cartoon': {'color': 'spectrum'}})
    if residue_numbers and chains:
        for residue_number, chain in zip(residue_numbers, chains):
            view.addStyle({'resi': residue_number.strip(), 'chain': chain.strip()}, {'sphere': {'color': color, 'radius': radius}})
    view.zoomTo()
    return view

