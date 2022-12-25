from playwright.sync_api import sync_playwright
from secret import *
from twilio_send import send_message

new_jobs = []
removed_jobs = []
posted_jobs = []

with open('old_jobs.txt', 'r') as oj:
    old_jobs = oj.read().splitlines()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state('networkidle')
    iframe = page.frame_locator('#icims_content_iframe')
    num_pages_element = iframe.locator('h2.iCIMS_SubHeader_Jobs').text_content()

    more_pages = True
    while more_pages:
        jobs_table = iframe.locator('div.iCIMS_JobsTable')
        jobs_count = jobs_table.locator('h2').count()
        i = 0
        for job in range(jobs_count):
            posted_jobs.append(jobs_table.locator('h2').nth(i).text_content().strip('\n'))
            i = i +1
        if iframe.locator('span[title="Next page of results"]').is_visible():
            with page.expect_response(response_url):
                iframe.locator('span[title="Next page of results"]').click()
        else:
            more_pages = False

    browser.close()

for job in posted_jobs:
    if job not in old_jobs:
        new_jobs.append(job)

for job in old_jobs:
    if job not in posted_jobs:
        removed_jobs.append(job)

with open ('old_jobs.txt', 'w') as f:
    for job in posted_jobs:
        f.write(f'{job}\n')

if new_jobs == []:
    new_job_message = 'There are no new jobs.\n'
else:
    new_job_message = 'The newly posted jobs are:\n'
    for job in new_jobs:
        new_job_message += f'{job}\n'

if removed_jobs == []:
    removed_job_message = "No jobs have been taken down."
else:
    removed_job_message = "The following jobs have been taken down:\n"
    for job in removed_jobs:
        removed_job_message+= f'{job}\n'

final_message = f'{new_job_message}\n{removed_job_message}'

for number in numbers:
    send_message(number, final_message) 