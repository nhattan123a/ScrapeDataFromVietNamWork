import pandas as pd
import re
import swifter
import numpy as np


def clean_salary_col(salary):
    if "Cạnh tranh" in salary or "Dưới" in salary or "Trên" in salary:
        return np.nan
    salary = salary.replace(',', '.')
    salary_range = map(float, re.findall(r"[-+]?(?:\d*\.\d+|\d+)", salary))
    avg_salary = sum(salary_range) / 2
    return avg_salary


def clean_experience_col(experience_):
    if experience_ == "Khong ro":
        return np.nan
    experience_range = map(int, re.findall(r'\d+', experience_))
    avg_exp_ = sum(experience_range) / 2
    return avg_exp_


# Define customized to cal average salary for each company
def custom_avg_salary(series):
    salary_sum = 0
    count = 0
    for val in series.values:
        if val != 0:
            salary_sum = salary_sum + val
            count = count + 1
    if count == 0:
        return salary_sum
    return salary_sum / count


def clean_list(list_):
    list_ = list_.replace('[', '"[')
    list_ = list_.replace(']', ']"')
    return list_


df = pd.read_csv('/Users/macos/PycharmProjects/ScrapingData/job_data.csv')

df['Published time'] = pd.to_datetime(df['Published time'])
df['New salary(mil vnd)'] = df['Salary'].apply(clean_salary_col)

# Create new dataframe to save company information: name, avg salary, number of published jobs
company_df = df.groupby(['Company'])['New salary(mil vnd)'].agg(lambda x: x.mean(skipna=True))\
                        .round(1).reset_index(name='Avg salary per job(mil vnd)')
count_jobs_per_company = df.groupby(['Company']).size()\
                            .reset_index(name='Number of published jobs')['Number of published jobs']
company_df['Number of published jobs'] = count_jobs_per_company


# df = df.drop(['New salary'], axis=1)

# Create new dataframe to save career type info: avg salary, avg experience, count unique career type

# Clean data, turn string to list
df['Career type'] = df['Career type'].fillna('[]')
df['Career type'] = df['Career type'].apply(eval)

# transform each element of a list-like to a row
career_type_df = df.explode('Career type').reset_index(drop=True)[['Career type', 'New salary(mil vnd)'

                                                                                        , 'Experience needed']]
# Clean data again
career_type_df['Experience needed'] = career_type_df['Experience needed'].str.replace('Năm', '')
career_type_df['Experience needed'] = career_type_df['Experience needed'].fillna('Khong ro')
career_type_df = career_type_df.rename(columns={'Experience needed': 'Experience needed(years)'})
career_type_df['Experience needed(years)'] = career_type_df['Experience needed(years)'].apply(clean_experience_col)


avg_exp = career_type_df.groupby(['Career type'])['Experience needed(years)'].agg(lambda x: x.mean(skipna=True))\
                                                                            .reset_index(name="Avg experience(year)")
avg_salary = career_type_df.groupby(['Career type'])['New salary(mil vnd)'].agg(lambda x: x.mean(skipna=True))\
                                                                            .reset_index(name="Avg salary(mil vnd)")
demo = pd.merge(avg_salary, avg_exp, on=['Career type'])


demo = career_type_df.groupby(['Career type'], as_index=False).agg(lambda x: x.mean(skipna=True)).reset_index()

demo.rename(columns={'New salary(mil vnd)': "X"}, inplace=True)
demo.rename(columns={'Experience needed(years)': "Y"}, inplace=True)

selected_cols = ['New salary(mil vnd)', 'Job level', 'Employment type', 'Experience needed']
mis_val_counts = df[selected_cols].isnull().sum(axis=1)
print(df.loc[mis_val_counts == 4])








