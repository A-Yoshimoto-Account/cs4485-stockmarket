import pandas as pd
import tiktoken

EMBEDDING_ENCODING = "cl100k_base"
MAX_TOKENS = 8000


#Main runner of datasetcleaner
def clean_csv(filepath):
    dataframe = pd.read_csv(filepath)
    dataframe = checkRelavance(dataframe)
    dataframe = cleaning_Title(dataframe)
    # dataframe = cleaning_Date(dataframe)
    dataframe = cleaning_Content(dataframe)
    dataframe = create_combined(dataframe)
    dataframe = create_token_count(dataframe)
    overwrite(dataframe,filepath)

def checkRelavance(df):
    df.drop(df[(df['Content'].str.contains('Nvidia') == False) 
            & (df['Content'].str.contains('NVDA') == False)
            &(df['Content'].str.contains('nvidia') == False)
            & (df['Content'].str.contains('nvda') == False)].index, inplace=True)
    return df


#Cleans title of any unwanted or unneeded data
def cleaning_Title(df):
    #removes double lines and single new lines
    df["Title"] = df["Title"].replace(to_replace = r'\n\n', value = '', regex=True)
    df["Title"] = df["Title"].replace(to_replace = r'\n', value = '', regex=True)
    #removes escape charaters
    df["Title"] = df["Title"].replace(to_replace = r'\'', value = '', regex=True)

    #removes any URL
    df["Title"] = df["Title"].replace(to_replace = r"https?://\S+|www.\.\S+", value = '', regex=True)

    #removes any html
    df["Title"] = df["Title"].replace(to_replace = r"<.*?>", value = '', regex=True)

    #removes any emojis
    df["Title"] = df["Title"].replace(to_replace = "["u"\U0001F600-\U0001F64F"
                                                      u"\U0001F300-\U0001F5FF"
                                                      u"\U0001F680-\U0001F6FF"
                                                      u"\U0001F1E0-\U0001F1FF"
                                                      u"\U00002702-\U000027B0"
                                                      u"\U000024C2-\U0001F251"
                                                      "]+", value = '', regex=True)
    return df

#Cleans date of any unwanted or unneeded data
def cleaning_Date(df):
    pass

#Cleans content of any unwanted or unneeded data
def cleaning_Content(df):
    #removes double lines and single new lines
    df["Content"] = df["Content"].replace(to_replace = r'\n\n', value = '', regex=True)
    df["Content"] = df["Content"].replace(to_replace = r'\n', value = '', regex=True)
    #removes escape charaters
    df["Content"] = df["Content"].replace(to_replace = r'\'', value = '', regex=True)

    #removes any URL
    df["Content"] = df["Content"].replace(to_replace = r"https?://\S+|www.\.\S+", value = '', regex=True)

    #removes any html
    df["Content"] = df["Content"].replace(to_replace = r"<.*?>", value = '', regex=True)

    #removes any emojis
    df["Content"] = df["Content"].replace(to_replace = "["u"\U0001F600-\U0001F64F"
                                                                                  u"\U0001F300-\U0001F5FF"
                                                                                  u"\U0001F680-\U0001F6FF"
                                                                                  u"\U0001F1E0-\U0001F1FF"
                                                                                  u"\U00002702-\U000027B0"
                                                                                  u"\U000024C2-\U0001F251"
                                                                                  "]+", value = '', regex=True)
    return df

#Creates a new col named "Combined" which is what will be fed into embeddings
def create_combined(df):
    df["Combined"] = (
    "Title: " + df.Title.str.strip() + "; Date: " + df.Date.str.strip()
    + "; Content: " + df.Content.str.strip())
    return df

#Creates a new col named "n_tokens" that stores the number of tokens each "combined" col has
def create_token_count(df):
    encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)

    df["n_tokens"] = df.Combined.apply(lambda x: len(encoding.encode(x)))
    df = df[df.n_tokens <= MAX_TOKENS]
    return df

#Overwrites original dataset
def overwrite(df,fp):
    df.to_csv(fp)