import json
import openpyxl 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import time
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import os
import requests
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
from datetime import date
import html2text
import os, glob
import sys
import send_email
#DRIVER INSTALLATIONS
driver = webdriver.Chrome(ChromeDriverManager().install())
#MAXIMIZE THE CHROME
driver.maximize_window()
today = date.today()
try:
    time.sleep(2)
    ds_usa_url = 'https://www.linkedin.com/login'
    driver.get(ds_usa_url)
    time.sleep(2)
    #LOGIN CREDENTIAL
    user = driver.find_element_by_id('username').send_keys('shoebahmed370@gmail.com')
    pwd = driver.find_element_by_id('password').send_keys('yasmeen1878')

    driver.find_element_by_xpath("//button[@aria-label= 'Sign in']").click()
except: 
    pass
       
def post_extraction(dom):
    print("*"*100)
    
    # dom = 'Artificial Intelligence Developer'
    # driver.implicitly_wait(10)
    time.sleep(5)
    print("domain name is", dom)
    driver.get('https://www.linkedin.com/feed/')
    time.sleep(5)
    driver.find_element_by_xpath("//input[@aria-label='Search']").clear()
    time.sleep(5)
    driver.find_element_by_xpath("//input[@aria-label='Search']").send_keys(dom)
    time.sleep(5)
    driver.find_element_by_xpath("//input[@aria-label='Search']").send_keys(Keys.ENTER )
    
    ##############################FILTER SELECTIONS#########################
    #POST
    time.sleep(5)
    post = driver.find_element_by_xpath('//div[@class = "authentication-outlet"]')
    
    time.sleep(5)
    post.find_element_by_xpath("//*[text() = 'Posts']").click()
    # post.find_element_by_xpath("//button[@aria-label= 'Posts']").click()
    time.sleep(5)
    #All Filters BOX
    time.sleep(5)
    filters = driver.find_element_by_xpath('//div[@class = "display-flex align-items-center"]')
    filters.find_element_by_xpath("//*[text() = 'All filters']").click()
    time.sleep(5)
    #PAST WEEK
    filter_box = driver.find_element_by_xpath('//div[@class = "artdeco-modal artdeco-modal--layer-default justify-space-between search-reusables__side-panel search-reusables__side-panel--open"]')

    filter_box.find_element_by_xpath("//*[text() = 'Past week']").click()
    time.sleep(5)
    #LATEST SELECTION POST
    filter_box.find_element_by_xpath("//*[text() = 'Latest']").click()
    time.sleep(5)
    driver.find_element_by_xpath("//button[@aria-label= 'Apply current filters to show results']").click()
    #####################################SCROLLER
    for i in range(0,30):
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, 0);")
    ######################################BS4 Capturing
    #BS4 panel
    source  = BeautifulSoup(driver.page_source)
    #Capture the content box
    post_link_list= []
    post_list = driver.find_elements_by_xpath('//div[@class= "occludable-update ember-view"]')
    search_res = source.findAll('div',{'class':'occludable-update ember-view'})
    description_temp_name_list = [];title_name_list =[];time_list =[];link_list=[];temp_link=[]
    mail_to_list = [];hastag_list =[];normal_link_list =[]
    attempt=1
    print("the length of post is", len(search_res))
    for i in range(len(search_res)):
        # print(i)
        mail_to = re.findall(r'(?<=href=\"mailto\:)[^\"\s]*', str(search_res[i]))
        if mail_to !=[]:
            mail_to_list.append(mail_to[0])
        else:
            mail_to_list.append(np.nan)
        hastag_link = re.findall(r"(?<=href=\")[^\"^\>^\#]*(?=\"\>\#)", str(search_res[i]))
        if hastag_link !=[]:
            hastag_list.append(hastag_link)
        else:
            hastag_list.append(np.nan)
        normal_link = re.findall(r"(?<=href=\")[^\"^\>^\#]*(?=\"\starget)", str(search_res[i]))
        if normal_link !=[]:
            normal_link_list.append(normal_link)
        else:
            normal_link_list.append(np.nan)

    
        title_name_var = re.findall(r'(?<=\<span dir=\"ltr\"\>)(.*)', str(search_res[i]))
        if title_name_var!=[]:
            title_name_var_name = title_name_var[0].split('</span>')[0]
            title_name_list.append(title_name_var_name.strip())
        else:
            title_name_list.append(np.nan)
        description_temp = re.findall(r'(?<=\<span dir=\"ltr\"\>)(.*)', str(search_res[i]))
        try:
            description_temp_name = description_temp[1].split('</span>')[0]
            description_temp_name = html2text.html2text(description_temp_name)
            description_temp_name_list.append(description_temp_name.strip())
        except:
            description_temp_name_list.append(np.nan)
        time_stamp = re.findall(r'(?<=\<span aria\-hidden\=\"true\"\>)([\s\S]*)', str(search_res[i]))
        if time_stamp !=[]:
            time_temp = time_stamp[0].split('•')[0].strip()
            if 'h' in time_temp or 'm' in time_temp or 's' in time_temp:
                time_stamp_var = today.strftime("%d/%m/%Y")
                time_list.append(time_stamp_var)
            elif 'd' in time_temp:
                time_diff = eval(time_temp.replace('d',''))
                time_stamp_var = today - timedelta(days = time_diff)
                time_list.append(time_stamp_var.strftime("%d/%m/%Y"))
            else:
                time_list.append(np.nan)
        else:
            time_list.append(np.nan)

        # print(description_temp_name)

        #Links_list_Post
        try:
            ccc= post_list[i].get_attribute('innerHTML')
            ddd= re.findall(r'(?<=id\=\"ember)(.*)(?=\" class\=\"artdeco-dropdown)',str(ccc))
            time.sleep(5)
            #we have to apply regular expression
            driver.find_element_by_xpath(f"//div[@id='ember{ddd[0]}' and @class='artdeco-dropdown artdeco-dropdown--placement-bottom artdeco-dropdown--justification-right ember-view']").click()
            time.sleep(5)
            post_list[i].find_element_by_xpath("//*[text() = 'Copy link to post']").click()
            time.sleep(5)
            sour1  = BeautifulSoup(driver.page_source)
            view_post= sour1.find_all('p',{'class':'artdeco-toast-item__message'})
            time.sleep(2)
            v_post = re.findall(r'(?<=href=")(.*)(?=")', str(view_post))
            # print(v_post[0])
            post_link_list.append(v_post[0])
            cancel= driver.find_element_by_xpath('//li-icon[@type="cancel-icon"]').click()
            time.sleep(5)
            
        except Exception as p:
            attempt=+1
            # print("post link exception as ----->",p)

            post_link_list.append(np.nan)
    print("length of post link is",len(post_link_list))
    df = pd.DataFrame ({"Post Name": dom.title(),
                        "Title_Name":title_name_list,
                       "Description":description_temp_name_list,
                       'Email_List': mail_to_list,
                       "Links":post_link_list,
                       "Date":time_list,
                       "Hastag_List":hastag_list,
                       "Link_List": normal_link_list
                       })
    df = df.dropna(subset=["Links"])
    locations_list = []
    for i in range(len(df)):
            
        try:
            print(i)
            driver.get(df.Links.iloc[i])
            time.sleep(5)
            driver.find_element_by_xpath('//span[@class="feed-shared-actor__title"]').click()
            time.sleep(5)
            pros=BeautifulSoup(driver.page_source)
        
            temp_loc= pros.findAll('span',{'class':'text-body-small inline t-black--light break-words'})[0].text
            # org-top-card-summary-info-list t-14 t-black--light
            temp_loc = temp_loc.strip()
            locations_data = temp_loc.split(',')[-1].strip()
            print(locations_data)
            locations_list.append(locations_data.strip())
        except:
            try:
                temp_loc = driver.find_element_by_xpath('//div[@class="org-top-card-summary-info-list t-14 t-black--light"]')
                temp_loc_2 = temp_loc.get_attribute('innerHTML') 
                temp3 = temp_loc_2.split('"inline-block">')[-1]
                locations_data = html2text.html2text(temp3).split('\n')[0].split(',')[-1]
                if 'followers'in locations_data:
                    locations_list.append(np.nan)
                else:
                    print(locations_data)

                    locations_list.append(locations_data.strip())
                    # print("-"*30)
            except Exception as e:
                print("Error in locations is ",e)
                locations_list.append(np.nan)
                # passs
    df["Locations"] = locations_list
    df = df[['Post Name', 'Title_Name', 'Description', 'Email_List', 'Links','Locations' ,'Date','Hastag_List', 'Link_List' ]]
           
    df = df.dropna(subset=["Locations"])

    
    print('length of dataFrame is',len(df))
    print("Number of missing email should be",attempt)
    return df
def dom_read():
    domain_name_list = []
    with open('domain.txt') as f:
        for dom in f:
            if dom:
                dom = dom[:-1].replace(',','')
                domain_name_list.append(dom.strip())
    all_dd = pd.DataFrame()
    # domain_name_list =['Tableau Developer']
    for i in domain_name_list:
        data_frame = post_extraction(i.lower())
        all_dd = all_dd.append(data_frame,ignore_index = True)
    curr = os.getcwd()
    
     
    dir_data = curr+'\\Linked_in_post_output'
    filelist = glob.glob(os.path.join(dir_data, "*"))
    for f in filelist:
        os.remove(f)
    if not os.path.exists(curr+'\\Linked_in_post_output'):
        # os.chdir(curr)
        os.makedirs(curr+'\\Linked_in_post_output')
    save_dir = curr+'\\Linked_in_post_output'
    os.chdir(save_dir)
    save_file_name =  'Linkedin_Post_'+today.strftime("%d_%m_%Y")+'.csv'
    all_dd.to_csv(save_file_name,index=False)
    # filename = save_dir+'\\'+save_file_name
    os.chdir(curr)
    sender_list = []
    with open('sender_list.txt') as f:
        for s_l in f:
            if s_l:
                s_l = s_l.replace(',','')
                # sender_list = 
                sender_list.append(s_l.strip())
    receiver_email=''
    receiver_email = ','.join(sender_list)
    #=======================MAIL_CONTENT======
    dom_str = ""
    for ind,i in enumerate(domain_name_list):
        dom_str +=str(ind+1)+". "+i+"\n"
    

    mail_content = f"""Hi, \nPlease find the attachment.\n\nAttached excel data contains following Technologies:\n{dom_str.title()}
    \n\n
    Thanks and Regards
    Data Analytics Team
    """
    mail_send = send_email.send_the_data(receiver_email,save_dir,save_file_name,curr,mail_content)
    # send_email.system_exit(driver)
    

while True:
    try:
        dom_read()
        driver.close()
        break
    except Exception as e:
        print("Hey we have an error as-->\n", e)
        pass

sys.exit()

# driver.close()    
# df.to_csv("linkdin_post.csv",index=False) 
# import send_email   

"""   
description_html = source.findAll("div",{'class':"feed-shared-update-v2__description-wrapper"})
all_span= source.find_all('div',class_='feed-shared-actor__meta relative')
# title_name_source = source.findAll("span",{'class':"feed-shared-actor__title"})
# time_source = source.findAll("span",{'class':"feed-shared-actor__sub-description t-12 t-normalt-black--light"})

feed-shared-update-v2__description-wrapper

# designation_list_source = source.findAll("span",{'class':"feed-shared-actor__description t-12 t-normalt-black--light"}) 

#list creation
title_name_list = []
description_list = []
link_list = []
time_list = []
temp_link=[]
# designation_list = []
today = date.today()
    
#Extracting data 
#For title name
 # \<li\-icon aria\-hidden

#TITLE 
# description_html= source.findAll("span",{'dir':"ltr"})
########################################################################
#Need to work on it
title_name_list = []
search_all= source.findAll("div",{'class':"search-results-container"})
# for i in search_all:
# var = 
title_name_var = re.findall(r'(?<=<span dir=\"ltr\"\>)(.*)',str(search_all))
print(title_name_var)


# if title_name_var ==[]:
#     title_name_list.append(np.nan)
# else:
#     title_name_list.append(title_name_var[0].split('</span>')[0])
###########################################################################
        
for i in all_span:
    var = str(i)
    title_name_var = re.findall(r'(?<=<span dir=\"ltr\"\>)(.*)',var)
    if title_name_var ==[]:
        title_name_list.append(np.nan)
    else:
        title_name_list.append(title_name_var[0].split('</span>')[0])
        
        
        
# Description


#for link 
for i in description_html:
    print(i.text)
    
    aa = i.find_all('a')
    if aa==[]:
        link_list.append(np.nan)
        temp_link.append(np.nan)
        pass
        
    else:
        # print(aa.text)
        temp =[]
        temp_link.append(aa)
        for x in aa:
            # print(x)
            if "hashtag" not in str(x):
                # print(x)
                link_list.append(x.get('href'))
            # link_list.append(temp)
    description_list.append(i.text.strip()) 
    
# Date
for i in all_span:
    # print(i.text.strip())
    temp_time = re.findall(r'(?<=<span aria\-hidden\=\"true\"\>)([\s\S]*)(?= \• )',str(i))[0]
    temp_time = temp_time.replace(' • Edited','')
    if 'h' in temp_time:
        print('we consider as a same day',temp_time, today)


df = pd.DataFrame ({"Title_Name":title_name_list,
                   "Description":description_list,
                   "Link":link_list,
                   "time":temp_time})    


for i in range(0,10):
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.execute_script("window.scrollTo(0, 0);")


post=driver.find_element_by_class_name("search-results-container")
driver.find_element_by_xpath("//button[@class='feed-shared-inline-show-more-text__see-more-less-toggle see-more t-14 t-black--light t-normal hoverable-link-text']").text


# c=[]
# for i in post:
#     c.append(i.text)
# print(c)
# print()
# print(len(c))

# col=["post"]
# df=pd.DataFrame({"Post":post})
# df.head()
# df.to_csv("linkdin_jobs.csv")

see_more_toggle = source.findAll("button",{'class':"feed-shared-inline-show-more-text__see-more-less-toggle see-more t-14 t-black--light t-normal hoverable-link-text"})
# #Sort by panel#################################################
# sort_data = post.text.split("\n")[3]
# if sort_data == 'Sort by':
#     post.find_element_by_xpath("//button[@aria-label = 'Sort by filter. Clicking this button displays all Sort by filter options.']").click()
# sort_dropdown = driver.find_element_by_id('hoverable-outlet-sort-by-filter-value')
# time.sleep(5)

# select_one_top_match = sort_dropdown.text.split("\n")[1]
#sort_dropdown.find_element_by_xpath("//*[text()='Top match']").click()
# sort_dropdown.find_element_by_xpath("//*[text()='Latest']").click()
#sort_dropdown.find_element_by_xpath("//*[@id='ember758']").click()
# post.find_element_by_xpath("//*[text() = '…see more']").text
# driver.find_element_by_xpath("/html/body/div[6]/div[3]/div/div[2]/section/div/nav/div/ul/li[3]/div/div/div/div[1]/div/form/fieldset/div[2]/button[2]/span").text
# driver.find_element_by_class_name("artdeco-button__text").text
#######################################
# material_data = source.findAll("div",{'class':"search-results-container"})
#################################################
############

"""