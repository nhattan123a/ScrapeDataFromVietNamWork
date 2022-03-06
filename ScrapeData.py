from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime


# We only need to get data on the current date, define function to check the published date
def check_current_date(published_time):
    current_time = datetime.datetime.now()
    day, month, year = current_time.day, current_time.month, current_time.year
    if int(published_time[0:2]) == day and int(published_time[3:5]) == month and year == int(published_time[6:10]):
        return True
    return False


# Define variable for job data
job_titles = []
company_names = []
published_time = []
locations = []
salary = []
# flex variable, can have value 'NULL'
employment_types = []
experience = []
job_levels = []
career_types = []


def get_data():
    for page_num in range(1, 50):
        # Get html text and use BeautifulSoup to get info
        url = f"https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-trang-{page_num}-vi.html"
        headers = {'User-Agent': 'Mozilla/5'}
        html_text = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html_text, features="html.parser")

        # Find value
        jobs_lists = soup.find('div', class_='jobs-side-list')
        job_infos = jobs_lists.find_all('div', class_="job-item")

        for job_info in job_infos:

            if not check_current_date(job_info.time.get_text()):
                break

            # basic info about job
            company_names.append(job_info.a.img['alt'])
            published_time.append(job_info.time.get_text())
            job_titles.append(job_info.find('a', class_="job_link")['title'])
            salary.append(job_info.find('div', class_="salary").text)
            locations.append(job_info.find('div', class_="location").text.strip())

            # more detailed info
            detailed_url = job_info.find('a', class_="job_link")['href']
            detailed_job = BeautifulSoup(requests.get(detailed_url, headers=headers).content, features="html.parser")

            details = detailed_job.find_all('div', class_='detail-box has-background')

            check1, check2, check3, check4 = 0, 0, 0, 0
            for index1, detail in enumerate(details):

                if index1 == 1:
                    for info in detail.find_all('li'):
                        if info.strong.text == "Kinh nghiệm":
                            experience.append(info.p.text.strip())
                            check1 = 1
                        if info.strong.text == "Cấp bậc":
                            job_levels.append(info.p.text)
                            check2 = 1

                if index1 == 0:
                    for info in detail.find_all('li'):
                        if info.strong.text == " Ngành nghề":
                            check3 = 1
                            career_type = []
                            for career in info.find_all('a'):
                                career_type.append(career.text.replace('\r\n','').strip())
                            career_types.append(career_type)
                        if info.strong.text == " Hình thức":
                            employment_types.append(info.p.text)
                            check4 = 1

            # If check is 0 then there is no value appended in list, so we have to insert 'NULL' value
            if check1 == 0:
                experience.append("NULL")
            if check2 == 0:
                job_levels.append("NULL")
            if check3 == 0:
                career_types.append("NULL")
            if check4 == 0:
                employment_types.append("NULL")


# Extract information from web
get_data()

# Create dataframe to save value
job_data = {'Job title': job_titles, 'Company': company_names, 'Salary': salary,
            'Published time': published_time, 'Location': locations, 'Experience needed': experience,
            'Career type': career_types, 'Job level': job_levels, 'Employment type': employment_types}


job = pd.DataFrame(data=job_data)

job.to_csv(r'/Users/macos/PycharmProjects/ScrapingData/job_data.csv', index=False, header=True)

# job['Salary'] = job['Salary'].strip








