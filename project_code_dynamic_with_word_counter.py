# -*- coding: utf-8 -*-
"""
Created on Fri Aug 04 14:56:35 2017

@author: Linn
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 01 13:51:02 2017

@author: Linn
"""

import os, glob, codecs, io, re
wd = 'C:\Users\Linn\Desktop\Tutorial_py'
os.chdir(wd)
import textminer as tm
dir_path = wd +'\sermons\\'

os.listdir(dir_path)

def read_multi_encode(path):
    """
    Read multiple files
    """
    filenames = glob.glob(dir_path +'*.txt')
    text_ls =[]
    meta_data = []
    for filename in filenames:
        try:
            text = codecs.open(filename, encoding= 'UTF-8').read()
            with io.open(filename, 'r', encoding = 'utf-8') as f:
                lignes =f.readlines()
                #if sermon is not in UTF-8, I will create a variable called text and try to read with latin-1 encoding
    #and divide into lines
        except:
            text = codecs.open(filename, encoding= 'LATIN-1').read()
            with io.open(filename, 'r', encoding = 'LATIN-1') as f:
                lignes =f.readlines()
                
        text_ls.append(text)
        #for each files, add the first three lines (name, date, sunday)
        meta_data.append(lignes[1][4:6])
    return text_ls, meta_data

#create lists with sermons and metadata
sermons, meta_data = read_multi_encode(dir_path)

#Create a new meta-list
date_reg = re.compile(r'% \d{6}')
dates = []
for sermon in sermons:
        date = date_reg.findall(sermon)
        dates.append(date)

month = []
for date in dates:
    try:
        month.append(date[0][4:6])
    except:
        month.append('FALSE')

#tokenize list with sermons using the function in tm called tokenize. We lowercase everything and are not interested in allcaps..

tokenized_sermons=[]
for i in sermons:
    tokenized_sermons.append(tm.tokenize(i.lower()))
    
#Use pruning to remove unwanted words:
prune = tm.prune_multi(tokenized_sermons, 50, 500)
    
#Alternatively you can use a stopword-list
#Create and apply stopword-list
sw = tm.gen_ls_stoplist(tokenized_sermons, 250) #How many words do we want to delete
sermons_nosw = []
for sermon in tokenized_sermons: #For each sermon:
    nosw_sermon = [] #Create empty list
    nosw_sermon =[token for token in sermon if token not in sw] #Fill the empty list with the words not in sw
    sermons_nosw.append(nosw_sermon) #Add the created list to sermons_nosw
    




#LDA modelling
from gensim import corpora, models
dictionary = corpora.Dictionary(prune) #Gives each word a numerical value




sermon_bow = [dictionary.doc2bow(sermon) for sermon in prune]

i = 1
sermon = sermon_bow[i]

from numpy.random import seed
seed(1234)

mdl = models.LdaModel(sermon_bow, id2word = dictionary,
                      num_topics = 10, random_state = 1234)

for i in range(10):
    print 'Topic', i
    print [t[0] for t in mdl.show_topic(i,10)] #asks for the first 10 words of topic i
    print '---------'
    
mdl[dictionary.doc2bow(prune[0])]
print mdl.show_topic(6,15)

"""Create dataframe"""

import pandas as pd

frame = pd.DataFrame()
frame['sermon'] = prune
frame['month'] = month
frame['date2'] = month
frame['sermon_BOW'] = sermon_bow

"Slice sermons together by date"
frame.set_index(('date2'), drop=False, append=False,
                inplace=True, verify_integrity=False)#Sets index after months
frame = frame.sort_index()#resorts the lists according to the index
frame = frame.groupby(frame['date2']).sum() #Groups together variables with the same value at 'date2'
frame = frame.drop('FALSE') # removes every variable with the index-value 'FALSE'
date_clean = [1,2,3,4,5,6,7,8,9,10,11,12]
frame['month'] = date_clean #Cleans column 'month'

"Get the topics for each month"

sermon_topics = []
for BOW in frame['sermon_BOW']: #For every month run the underlying
    month_topic = mdl[BOW] #The topics of the month is placed in month_topic
    sermon_topics.append(month_topic) #adds the month_topic to the sermon_topics-list
frame['Sermon_Topics'] = sermon_topics #adds the sermon_topics to our DataFrame



"""Get the most frequent topic of each month"""
def get_topic_fq(month):
    topic_fq = mdl[frame['sermon_BOW'][month]]
    return topic_fq #Creates function to get the topics of a month

highest_fq = []
for number in range (len(frame['month'])): #Tells python to run this for each month
    topic_fq = get_topic_fq(number) #Gets topics of the month
    topic_FQ = [0, 0.0] #creates a variable with the most frequent topic
    for topic in topic_fq: #For every topic in the month
        if topic[1] > topic_FQ[1]: #if its frequency is higher than the currently highest
            topic_FQ[0] = topic[0] #Replace the topic number
            topic_FQ[1] = topic[1] #Replace the topic frequency
    highest_fq.append(topic_FQ) #Add it to a list corresponding to our month

#Function to print month and its most frequent topic:
i = 0
for month in frame['month']:
    print ('most frequent topic of month '+str(month)+' is:')
    print  'topic '+str(highest_fq[i][0])+': whose 5 most frequent words are:'
    for x in range (5):
        term = mdl.show_topic((highest_fq[i][0]),5)
        print term[x][0]
    print '-------'
    i = i+1


from collections import Counter   
words =[]
for sermon in sermons_nosw:
   for word in sermon:
       words.append(word)
       
word_count = Counter(words)
print word_count.most_common(10)













