import pandas as pd
from IPython.display import display

def pretty_print_value_counts(df, column, title=None):
    """
    Pretty prints the value counts of a specified column in a Pandas DataFrame, 
    with counts formatted with thousand separators and percentages.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column for which to calculate value counts.
    title : str, optional
        A title to print above the formatted output. If None, no title is printed.
    
    Returns:
    --------
    None
        Displays a styled DataFrame with counts and percentages.
    """
    # Calculate the value counts and convert to DataFrame
    count_df = pd.DataFrame(df[column].value_counts(normalize=False).reset_index())
    count_df.columns = ['Category', 'Count']
    
    # Add a percentage column
    count_df['Percent'] = (count_df['Count'] / count_df['Count'].sum()) * 100
    
    # Optionally print the title
    if title:
        print("="*50)
        print(f"  {title}")
        print("="*50)
    
    # Display the styled DataFrame without index, formatting Count and Percent columns
    display(count_df.style.hide(axis='index')
            .format({
                "Count": "{:,.0f}",  # Thousand separator for Count
                "Percent": "{:.2f}%"  # Format Percent to 2 decimal places with a % symbol
            }))
    
    # Print footer or separator
    print("-"*45)
