#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector as con
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image
from datetime import datetime
from time import process_time
import threading 
import time
from time import process_time
import os
import config_pan
import time
from time import process_time


P1_time, P2_time,P3_time,P4_time,P5_time,P6_time,P7_time,P8_time,P9_time = 0,0,0,0,0,0,0,0,0

pytesseract.pytesseract.tesseract_cmd = r'F:\NOT_DONE_work\ocr\tesseract.exe'
poppler_path = r"C:/Program Files/poppler-22.04.0/Library/bin"

#pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT', 'tesseract')
#poppler_path = os.environ.get('POPPLER', 'poppler')


REMARK=""
host='localhost'
user='root'
passwd='nsdl@1234'
database='OCR_DB'
state_dict = {1 : "ANDAMAN AND NICOBAR ISLANDS", 2:"ANDHRA PRADESH", 3:"ARUNACHAL PRADESH", 4:"ASSAM", 5:"BIHAR",                                  
                    6:"CHANDIGARH", 7:"DADRA AND NAGAR HAVELI", 8:"DAMAN AND DIU" ,9:"DELHI", 10:"GOA", 11:"GUJARAT",
                  12:"HARYANA", 13:"HIMACHAL PRADESH", 14:"JAMMU AND KASHMIR", 15:"KARNATAKA" , 16:"KERALA", 17:"LAKHSWADEEP", 
                  18:"MADHYA PRADESH", 19:"MAHARASHTRA", 20:"MANIPUR", 21:"MEGHALAYA",22:"MIZORAM", 23:"NAGALAND" , 24:"ORISSA",
                  25:"PONDICHERRY",26:"PUNJAB", 27:"RAJASTHAN",28:"SIKKIM",29:"TAMILNADU",30:"TRIPURA" , 31:"UTTAR PRADESH" , 
                  32 : "WEST BENGAL", 33:"CHHATISHGARH",34:"UTTRAKHAND" , 35:"JHARKHAND" , 36:"TELANGANA", 
                  99:"ADDRESS OF DEFENCE EMPLOYEES", 88:"FOREIGN ADDRESS", 37:"LEH"}



# In[2]:


def remove_spl(str_input):
    str_input = str(str_input)
    sp = str_input.split()
    sp_list=[]
    for i in range(0,len(sp)):
        sample_list=[]
        for i in sp[i]:
            if i.isalnum():
                sample_list.append(i)
        normal_string="".join(sample_list)
        sp_list.append(normal_string)
    sp =" ".join(sp_list)
    #print(sp)
    return sp
        


# In[3]:


###function for nmatching words in columns[address,namess,DOB,ETC] ###

def Match_words(word, text_dict):
    name_lis = []
    brk=0
    NA = "NA"
    
    for m in range (0, len(word)):
        for n in range(0, len(word)):
        #print((str(word).lower())[j:len(word)-i])
            try:
                    
                if len((str(word).lower())[n:len(word)-m]) >= 4:
                    a = re.findall((str(word).lower())[n:len(word)-m],text_dict)
                    if len(a) != 0:
                        name_lis.append(a)
                        #print("a: ",a)
                        brk=1
                        break
                #print((str(word).lower())[len(word)-i:-1])
                    b = re.findall((str(word).lower())[m:len(word)-n],text_dict) 
                    if len(b) != 0:
                        name_lis.append(b)
                        #print("b: ",b)
                        brk=1
                        break
            except Exception as e:
                print(e)
                brk=1
                break
                        
        if brk:
            break
    #print(name_lis, "NAME_LIS")
    #print("ok")
        
    return name_lis

            


# In[4]:


def match_words_full(word_string_1, text_dict):

    word_string = word_string_1.split()
    word_string_match = []
    for words in word_string:
        word_len = re.search(str(words), text_dict)
        if word_len :
            word_string_match.append(words)### full word##
            percentage = 100
        else:
            half_word = Match_words(words, text_dict)   ### half word match #
                #print(type(address_word))
            if len(half_word) !=0:
                if len(half_word[0]) !=0:
                     word_string_match.append(half_word[0][0])
                     
                                
                    
                    #print(address_match)      
    add_join = " ".join(word_string_match)
    
    #print("IN:",word_string_1)
    #Print(type(word_string_1))
    #print("OUT_add:",add_join)
    #print(add_join)
    percentage = (len(str(add_join))/ len(str(word_string_1)))*100
    #print(percentage)
    return [add_join, percentage]
    
    


# In[5]:


def name_dob_match(row, first_index, mid_index, last_index, dob_index, text_dict):
    full_name = ''
    full_name_percentage = 0
    count = 0
    if row[last_index] != "nan":
        Ap_Last_Name = row[last_index]
        Ap_Last_Name = Ap_Last_Name.lower()
      
        Last_Name = match_words_full(Ap_Last_Name, text_dict)
        full_name = full_name + " "+ Last_Name[0]
        full_name_percentage = full_name_percentage +  Last_Name[1]
        count +=1
        
        
    else:
        Last_Name = ["No Input",0]
            
    
    
    if row[mid_index] != "nan":
        Ap_Mid_Name = row[mid_index]
        Ap_Mid_Name = Ap_Mid_Name.lower()
      
        Mid_Name = match_words_full(Ap_Mid_Name, text_dict)
        full_name = full_name + " "+ Mid_Name[0]
        full_name_percentage = full_name_percentage +  Mid_Name[1]
        count +=1
    else:
        Mid_Name = ["No Input",0]
                              
                              
                              
    
    if row[first_index] != "nan":
        Ap_First_Name = row[first_index]
        Ap_First_Name = Ap_First_Name.lower()
        First_Name = match_words_full(Ap_First_Name, text_dict)
        full_name = full_name + " "+ First_Name[0]
        full_name_percentage = full_name_percentage +  First_Name[1]
        count +=1            

    else:
        First_Name = ["No Input",0]
        
        
    if row[dob_index] != "nan":
        Ap_DOB = row[dob_index]
        #print(type(Ap_DOB))
        cleanString = ''.join(letter for letter in str(Ap_DOB) if letter.isalnum())  ###dob 1995-05-06 ==> 1995/05/06##
        dob_new = datetime.strptime(cleanString, "%Y%m%d").strftime('%d/%m/%Y')
        #print(dob_new)
        if re.search(str(dob_new), text_dict):  
            percentage = 100
            DOB = [dob_new, percentage]
        else:
            DOB= ["nan",0]
            

    else:
         DOB= ["No Input",0]
            
    if full_name_percentage !=0 and count != 0:
        full_name_percentage = full_name_percentage/count
    else:
        full_name_percentage = full_name_percentage
        
    Name_matched = [full_name,  full_name_percentage]
 

    return [ Name_matched , DOB]   

    
    
   
    


# In[6]:


def address_search_res(Pincode, Statecode,Res_add_1, Res_add_2,Res_add_3,Res_add_4,Res_add_5,text_dict):
    if Pincode !="nan":
        if re.search(str(Pincode), text_dict):
            res_pin = [str(Pincode), 100]
        else:
            res_pin = ['nan',0]
            
    else:
        res_pin = ["No Input",0]
        ##if pincode matched then go for remaining address ##
            
    res_statecode= Statecode
    #print(res_statecode)
    state = str(state_dict[int(res_statecode)]).lower()
    #print(state)
    state = state.split(' ')
    if Statecode !="nan":
        if re.search(state[0],text_dict):
            res_state =[str(state_dict[int(res_statecode)]),100]
        else:
            res_state =['nan',0]
            
    else:
        res_state =["No Input",0]
    
    address = str(Res_add_1)+ ' '+str(Res_add_2)+' '+str(Res_add_3)+ ' '+str(Res_add_4)+' '+ str(Res_add_5)
        #cleanString = ' '.join(letter for letter in address if letter.isalnum()) 
    address = address.lower()
    address_match_res = match_words_full(address, text_dict)
    return [address_match_res, res_pin, res_state]

    
    


# In[7]:


##SEARCH ADHAAR DOC ##

def extract_and_collect(img):
    height = img.shape[0]
    width = img.shape[1]
    #print(height,width)
    
    height_cutoff = height // 3
    
    p1 = img[ :height_cutoff, :]
    p2 = img[height_cutoff-50 : 2*(height_cutoff), :]
    p3 = img[2*(height_cutoff)-50 :height, :]

    lis = [p1,p2,p3]
    text = ""
    
    for j in lis:
        text += pytesseract.image_to_string(j,config='--psm 6')
        
    return text
    

    


# In[8]:


def document_type_find(text, DOC_1, DOC_2, DOC_3, DOC_4, DOC_5,DOC_6):
    doc_words = ["UNIQUE", "Identification","AADHAAR", "ELECTION", "COMMISSION","REPUBLIC","PASSPORT", "DRIVE", "DRIVING","VEHICLE",  "INCOME", "TAX"]
    DOC_TYPE = ""
    text = remove_spl(text)
    for i in range(0, len(doc_words)):
        if i<3 and re.search(doc_words[i].lower(), text) :
            DOC_TYPE = "AADHAAR"
            DOC_1.update({ "DOC_TYPE": "AADHAAR",   "raw_text": text})
            break
        
        elif (3 <= i < 5) and re.search(doc_words[i].lower(), text):
            DOC_TYPE = "VOTER ID"
            DOC_2.update({ "DOC_TYPE":"VOTER ID" ,  "raw_text": text})
            break
        
        elif (5 <= i < 7) and re.search(doc_words[i].lower(), text):
            DOC_TYPE = "PASSPORT"
            DOC_3.update({"DOC_TYPE": "PASSPORT",   "raw_text": text})
            break
        
        elif (7 <= i < 10) and re.search(doc_words[i].lower(), text):
            DOC_TYPE = "DRIVING LICENSE"
            DOC_4.update({"DOC_TYPE": "DRIVING LICENSE",   "raw_text": text})
            break   
        
        elif (10 <= i < 12) and re.search(doc_words[i].lower(), text):
            DOC_TYPE = "PAN"
            DOC_5.update({"DOC_TYPE": "PAN",  "raw_text": text})
            break
            
        else:
            DOC_TYPE = "OTHER"
            DOC_6.update({"DOC_TYPE": "OTHER",  "raw_text": text})
            break
            
            
    return DOC_TYPE
        
        



# In[9]:


def match_calculate(row, table,file_type,images, img_proc):
    ack_no = row[4]
    pdf_path = fr"{row[2]}/{ack_no}.pdf"
    doc1_percentage = 0
    doc2_percentage = 0
    doc3_percentage = 0
    doc4_percentage = 0
    full_pdf_percentage = 0
    REMARK = ""
    
    DOC_1= {"DOC_TYPE": "","Masked_Adhaar_No": '', "Ap_Full_Name":'',"Ap_DOB":'', "Res_Address":'', "Res_pin":'', "Res_State": '', "raw_text" : ""}
    DOC_2 = {"DOC_TYPE":"","Ap_Full_Name":'',"Ap_DOB":'', "Res_Address":'', "Res_pin":'', "Res_State":'', "raw_text" : ""}
    DOC_3 = {"DOC_TYPE":"","Ap_Full_Name":'',"Ap_DOB":'', "Res_Address":'', "Res_pin":'', "Res_State":'', "raw_text" : ""}
    DOC_4 = {"DOC_TYPE":"","Ap_Full_Name":'',"Ap_DOB":'', "Res_Address":'', "Res_pin":'', "Res_State":'', "raw_text" : ""}
    DOC_5 = {"DOC_TYPE":"", "raw_text" : ""}
    DOC_6 =  {"DOC_TYPE":"","Ap_Full_Name":'',"Ap_DOB":'', "Res_Address":'', "Res_pin":'', "Res_State":'', "raw_text" : "", "Masked_Adhaar_No": '',"PAN_no":''}
    
    DOC_1_PARAMETRS_percentage = {"DOC_TYPE": "", "Masked_Adhaar_No_Percent":0,"Ap_Full_Name_percentage":0,"Ap_DOB_percentage":0,"Res_Address_Percentage":0, "Res_pin_Percentage":0, "Res_State_Percentage": 0, "DOC_1_PERCENTAGE": 0}
    DOC_2_PARAMETRS_percentage = {"DOC_TYPE": "", "Ap_Full_Name_percentage":0,"Ap_DOB_percentage":'',"Res_Address_Percentage":0, "Res_pin_Percentage":0, "Res_State_Percentage": 0, "DOC_2_PERCENTAGE":0}
    DOC_3_PARAMETRS_percentage = {"DOC_TYPE": "", "Ap_Full_Name_percentage":0,"Ap_DOB_percentage":'',"Res_Address_Percentage":0, "Res_pin_Percentage":0, "Res_State_Percentage": 0, "DOC_3_PERCENTAGE":0}
    DOC_4_PARAMETRS_percentage = {"DOC_TYPE": "", "Ap_Full_Name_percentage":0,"Ap_DOB_percentage":'',"Res_Address_Percentage":0, "Res_pin_Percentage":0, "Res_State_Percentage": 0, "DOC_4_PERCENTAGE":0}
    DOC_5_PARAMETRS_percentage = {"DOC_TYPE": "" ,  "PAN_match_percentage":""}
    DOC_6_PARAMETRS_percentage = {"DOC_TYPE":"","Ap_Full_Name_percentage":'',"Ap_DOB_percentage":'', "Res_Address_Percentage":'', "Res_pin_Percentage":'', "Res_State_Percentage":'',  "Masked_Adhaar_No_Percent": '',"PAN_match_percentage":'', "DOC_6_PERCENTAGE":0}
  

    
    for i in range(2,len(images)):
        start_4 = time.time()
        opencvImage = cv2.cvtColor(np.array(images[i]), cv2.COLOR_RGB2BGR)
            
        image_text = extract_and_collect(opencvImage)
        end_4 = time.time()
        global P4_time
        P4_time = end_4 - start_4
            
            
        text_dict=image_text.replace("\n","")
        text_dict=text_dict.replace(" ","")
        text_dict = text_dict.lower()
        ##print("RAW text---->",text_dict)
        
        start_6 = time.time()
        document_type = document_type_find(text_dict, DOC_1, DOC_2, DOC_3, DOC_4, DOC_5,DOC_6)
        end_6 = time.time()
        global P6_time
        P6_time = end_6 - start_6
        
        start_7 = time.time()
        t1_initial_match = name_dob_match(row,7,8,6,17,text_dict)
        end_7 = time.time()
        global P7_time
        P7_time = end_7 - start_7
        
        if document_type == "AADHAAR":
            if row[33] !="nan":
                if re.search(((str(row[19])).replace("X","")), DOC_1["raw_text"]): ### masked adhar : 33###
                    masked_adhaar_matched = [str(row[19]) , 1]
                else:
                     masked_adhaar_matched = ['nan' , 0]

                start_9 = time.time()
                res_add = address_search_res(row[15], row[14], row[9],row[10],row[11],row[12],row[13],text_dict)
                doc1_percentage = (res_add[0][1]+ res_add[2][1]+res_add[1][1])/3
                end_9 = time.time()
                global P9_time
                P9_time = end_9 - start_9

                DOC_1.update({"Masked_Adhaar_No": masked_adhaar_matched[0], "Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0]})
                DOC_1_PARAMETRS_percentage.update({"Masked_Adhaar_No_Percent": masked_adhaar_matched[1],"Ap_Full_Name_percentage":t1_initial_match[0][1],"Ap_DOB_percentage":t1_initial_match[1][1],"Res_Address_Percentage":res_add[0][1], "Res_pin_Percentage":res_add[1][1], "Res_State_Percentage": res_add[2][1], "DOC_1_PERCENTAGE":doc1_percentage})
                
                if doc1_percentage > config_pan.first_document_threshold:
                    REMARK = "AADHAAR DOC PERCENTAGE IS MORE THAN 70%" 
                    full_pdf_percentage = doc1_percentage
                    return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]
             
      
        elif document_type == "VOTER ID":
                res_add = address_search_res(row[15], row[14], row[9],row[10],row[11],row[12],row[13],text_dict)
                doc2_percentage = (res_add[0][1]+ res_add[2][1]+res_add[1][1])/3

                DOC_2.update({"Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0]})
                DOC_2_PARAMETRS_percentage.update({"Ap_Full_Name_percentage":t1_initial_match[0][1],"Ap_DOB_percentage":t1_initial_match[1][1],"Res_Address_Percentage":res_add[0][1], "Res_pin_Percentage":res_add[1][1], "Res_State_Percentage": res_add[2][1], "DOC_2_PERCENTAGE":doc2_percentage})

                if doc2_percentage > config_pan.first_document_threshold:
                    REMARK = "VOTER ID DOC PERCENTAGE IS MORE THAN 70%" 
                    full_pdf_percentage = doc2_percentage
                    return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]
             
                
        
        elif document_type == "PASSPORT":
                res_add = address_search_res(row[15], row[14], row[9],row[10],row[11],row[12],row[13],text_dict)
                doc3_percentage = (res_add[0][1]+ res_add[2][1]+res_add[1][1])/3

                DOC_3.update({"Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0]})
                DOC_3_PARAMETRS_percentage.update({"Ap_Full_Name_percentage":t1_initial_match[0][1],"Ap_DOB_percentage":t1_initial_match[1][1],"Res_Address_Percentage":res_add[0][1], "Res_pin_Percentage":res_add[1][1], "Res_State_Percentage": res_add[2][1], "DOC_3_PERCENTAGE":doc3_percentage})

                if doc3_percentage > config_pan.first_document_threshold:
                    REMARK = "PASSPORT DOC PERCENTAGE IS MORE THAN 70%"
                    full_pdf_percentage = doc3_percentage
                    return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]
             
                
        elif document_type == "DRIVING LICENSE":
                res_add = address_search_res(row[15], row[14], row[9],row[10],row[11],row[12],row[13],text_dict)
                doc4_percentage = (res_add[0][1]+ res_add[2][1]+res_add[1][1])/3

                DOC_4.update({"Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0]})
                DOC_4_PARAMETRS_percentage.update({"Ap_Full_Name_percentage":t1_initial_match[0][1],"Ap_DOB_percentage":t1_initial_match[1][1],"Res_Address_Percentage":res_add[0][1], "Res_pin_Percentage":res_add[1][1], "Res_State_Percentage": res_add[2][1], "DOC_4_PERCENTAGE":doc4_percentage})

                if doc4_percentage > config_pan.first_document_threshold:
                    REMARK = "DRIVING LICENSE DOC PERCENTAGE IS MORE THAN 70%" 
                    full_pdf_percentage = doc4_percentage
                    return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]
             

                
        elif document_type == "PAN":   
            if row[18] !="nan" and file_type == 't1':
                if re.search(str(row[18]).lower(), text_dict):
                    PAN_no_match = match_words_full(str(row[18]), text_dict)
                    PAN_no = [PAN_no_match[0], 1]
                else:
                    PAN_no = ["Not Found",0]
                DOC_5.update({"PAN_no_match":PAN_no[0]})
                DOC_5_PARAMETRS_percentage.update({ "PAN_match_percentage":PAN_no[1]})
                
        elif document_type == "OTHER":
            if row[33] !="nan":
                if re.search(((str(row[19])).replace("X","")), DOC_1["raw_text"]): ### masked adhar : 33###
                        masked_adhaar_matched = [str(row[19]) , 1]
                else:
                    masked_adhaar_matched = ['nan' , 0]

                
            res_add = address_search_res(row[15], row[14], row[9],row[10],row[11],row[12],row[13],text_dict)
            doc6_percentage = (res_add[0][1]+ res_add[2][1]+res_add[1][1])/3
            
            if row[18] !="nan" and file_type == 't1':    
                if re.search(str(row[18]).lower(), text_dict):
                    PAN_no_match = match_words_full(str(row[18]), text_dict)
                    PAN_no = [PAN_no_match[0], 1]
                else:
                    PAN_no = ["Not Found",0]
                    
                    
            ###paste here------------------->>>>>>>>>>>>   
            if file_type =='t1':       
                DOC_6.update({"Masked_Adhaar_No": masked_adhaar_matched[0], "Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0], "PAN_no_match":PAN_no[0]})
                DOC_6_PARAMETRS_percentage.update({"Masked_Adhaar_No_Percent": masked_adhaar_matched[1],"Ap_Full_Name_percentage":t1_initial_match[0][1],"Ap_DOB_percentage":t1_initial_match[1][1],"Res_Address_Percentage":res_add[0][1], "Res_pin_Percentage":res_add[1][1], "Res_State_Percentage": res_add[2][1], "DOC_6_PERCENTAGE":doc6_percentage})
            
            else:
                 DOC_6.update({"Masked_Adhaar_No": masked_adhaar_matched[0], "Ap_Full_Name":t1_initial_match[0][0],"Ap_DOB":t1_initial_match[1][0], "Res_Address":res_add[0][0], "Res_pin":res_add[1][0], "Res_State": res_add[2][0], "PAN_no_match":0})
    
            if doc6_percentage > config_pan.first_document_threshold:
                REMARK = "OTHER DOC PERCENTAGE IS MORE THAN 70%" 
                full_pdf_percentage = doc6_percentage
                return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK,  DOC_6, DOC_6_PARAMETRS_percentage]
             
            
            
        else:
            if i ==len(images):
                #print("no doc DETECTED!!!")
                REMARK = "VALID ID PROOF NOT FOUND"
                full_pdf_percentage = 0
                return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]

            
    full_pdf_percentage = max(float(DOC_1_PARAMETRS_percentage["DOC_1_PERCENTAGE"]), float(DOC_2_PARAMETRS_percentage["DOC_2_PERCENTAGE"]), float(DOC_3_PARAMETRS_percentage["DOC_3_PERCENTAGE"]), float(DOC_4_PARAMETRS_percentage["DOC_4_PERCENTAGE"]),float(DOC_6_PARAMETRS_percentage ["DOC_6_PERCENTAGE"]))
                      
    return [DOC_1, DOC_1_PARAMETRS_percentage, DOC_2, DOC_2_PARAMETRS_percentage, DOC_3, DOC_3_PARAMETRS_percentage, DOC_4, DOC_4_PARAMETRS_percentage,DOC_5, DOC_5_PARAMETRS_percentage, full_pdf_percentage,REMARK, DOC_6, DOC_6_PARAMETRS_percentage]
                            
                        
                        
  


# In[10]:


def ocrstart(row, table,file_type):
    ack_no = row[5]
    pdf_path = fr"{row[4]}/{ack_no}.pdf"
    
    try:
        start_1 = time.time()
        images = convert_from_path(pdf_path, 500, poppler_path = poppler_path)
    
        end_1 = time.time()
        global P1_time
        P1_time = end_1 - start_1
    
    except Exception as e:
        # if ack no did not match P_PER_MATCHED = 0 ,  P_MATCG_STATUS = NO ACK  ,  P_PROC_FLAG =1  P_LUPD_DATE =now()
        connection = con.connect(host=host,user=user, passwd=passwd,database=database)
        cursor = connection.cursor()
        sql_update_qry = f"""UPDATE {table} SET O_PERCENT_PDF_MATCHED=0, O_MATCH_STATUS= 'PDF NOT FOUND', O_PROC_FLAG=1,  O_LUPD_DATE =now(), O_REMARK = "PDF NOT found"
                             WHERE  
                             P_BATCH_ID='{row[0]}' and P_ACK_NO='{ack_no}' """
        #print(sql_update_qry)
        cursor.execute(sql_update_qry)
        connection.commit()
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed",e)
        return 0
    
    start_2 = time.time()
    opencvImage = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    image_bw = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
    
    #extract ack number from image
    crop_img = image_bw[50:250, 1600:2350]
    #cv2.imwrite(f"crop{ack_no}.jpg",crop_img)
    
    text_dict = pytesseract.image_to_string(crop_img)
    text_dict=text_dict.replace("\n","")
    text_dict=text_dict.replace(" ","")
    #print(text_dict)
    
    #compare ack number
    ack_match = re.search(ack_no, text_dict)
    end_2 = time.time()
    global P2_time
    P2_time = end_2 - start_2
    
    if ack_match:
        documents_info = match_calculate(row, table,file_type,images, False)#True#
        #print(documents_info)
        #print(len(documents_info)," length...")
        
        final_percentage = documents_info[10]

        
        
        #if config_pan.crop_exec_thershold_min <= final_percentage < config_pan.crop_exec_thershold_max : #50#
        #    print(final_percentage,"--- less than 20")
        #    documents_info = match_calculate(row, table,file_type,images, False)
        #    #print(documents_info)
        #    final_percentage = documents_info[10]
        #    print(final_percentage,"--- after image crop and proc ")

       
        if final_percentage > config_pan.valid_invalid_threshold:
            results = "VALID"
        elif final_percentage<=20:
            results = "MANUALLY CHECK"
        else:
            results = "INVALID"
        
        start_8 = time.time()
        
        connection = con.connect(host=host,user=user, passwd=passwd,database=database) 
        cursor = connection.cursor()

        #print("doc_info:---->\n ", documents_info)
        sql_update_qry = f"""UPDATE {table} SET   O_ADHAAR_NO_MATCHED = '{documents_info[1]["Masked_Adhaar_No_Percent"]}' , O_PAN_MATCHED = '{documents_info[9]["PAN_match_percentage"]}' , 
    O_DOC_1="{documents_info[0]["raw_text"]}", O_DOC_2="{documents_info[2]["raw_text"]}", O_DOC_3="{documents_info[4]["raw_text"]}", O_DOC_4="{documents_info[6]["raw_text"]}", O_DOC_5="{documents_info[8]["raw_text"]}",  O_DOC_6="{documents_info[12]["raw_text"]}",
        O_PERCENT_DOC1_MATCHED= '{documents_info[1]["DOC_1_PERCENTAGE"]}' , O_PERCENT_DOC2_MATCHED= '{documents_info[3]["DOC_2_PERCENTAGE"]}' , O_PERCENT_DOC3_MATCHED= '{documents_info[5]["DOC_3_PERCENTAGE"]}', O_PERCENT_DOC4_MATCHED= '{documents_info[7]["DOC_4_PERCENTAGE"]}',  O_PERCENT_DOC6_MATCHED= '{documents_info[13]["DOC_6_PERCENTAGE"]}',
        O_MATCH_STATUS = '{results}', O_PERCENT_PDF_MATCHED ="{final_percentage}",
        
        O_FULL_NAME_MATCHED_DOC1 = '{documents_info[0]["Ap_Full_Name"] + "," + str(documents_info[1]["Ap_Full_Name_percentage"])}', O_FULL_NAME_MATCHED_DOC2 = '{documents_info[2]["Ap_Full_Name"] + "," +  str(documents_info[3]["Ap_Full_Name_percentage"])}', O_FULL_NAME_MATCHED_DOC3 = '{documents_info[4]["Ap_Full_Name"] + "," + str(documents_info[5]["Ap_Full_Name_percentage"])}', O_FULL_NAME_MATCHED_DOC4 = '{documents_info[6]["Ap_Full_Name"]  + "," + str(documents_info[7]["Ap_Full_Name_percentage"])}',  O_FULL_NAME_MATCHED_DOC6 = '{documents_info[12]["Ap_Full_Name"] + "," + str(documents_info[13]["Ap_Full_Name_percentage"])}', 
    
        O_DOB_MATCHED_DOC1 = '{documents_info[0]["Ap_DOB"]  + "," + str(documents_info[1]["Ap_DOB_percentage"])}', O_DOB_MATCHED_DOC2 = '{documents_info[2]["Ap_DOB"] + "," + str(documents_info[3]["Ap_DOB_percentage"])}', O_DOB_MATCHED_DOC3 = '{documents_info[4]["Ap_DOB"]  + "," + str(documents_info[5]["Ap_DOB_percentage"])}', O_DOB_MATCHED_DOC4 = '{documents_info[6]["Ap_DOB"] + "," + str(documents_info[7]["Ap_DOB_percentage"])}',O_DOB_MATCHED_DOC6 = '{documents_info[12]["Ap_DOB"]  + "," + str(documents_info[13]["Ap_DOB_percentage"])}',
         
        O_ADDRESS_MATCHED_DOC1 = '{str(documents_info[0]["Res_Address"]) + "," +  str(documents_info[1]["Res_Address_Percentage"])}', O_ADDRESS_MATCHED_DOC2 = '{str(documents_info[2]["Res_Address"])  + "," +  str(documents_info[3]["Res_Address_Percentage"])}', O_ADDRESS_MATCHED_DOC3 = '{str(documents_info[4]["Res_Address"])  + "," +  str(documents_info[5]["Res_Address_Percentage"])}', O_ADDRESS_MATCHED_DOC4 = '{str(documents_info[6]["Res_Address"])  + "," + str(documents_info[7]["Res_Address_Percentage"])}',O_ADDRESS_MATCHED_DOC6 = '{str(documents_info[12]["Res_Address"]) + "," +  str(documents_info[13]["Res_Address_Percentage"])}', 
        O_STATE_MATCHED_DOC1 = '{str(documents_info[0]["Res_State"]) + "," +  str(documents_info[1]["Res_State_Percentage"])}', O_STATE_MATCHED_DOC2 = '{str(documents_info[2]["Res_State"]) + "," +  str(documents_info[3]["Res_State_Percentage"])}', O_STATE_MATCHED_DOC3 = '{str(documents_info[4]["Res_State"]) + "," +  str(documents_info[5]["Res_State_Percentage"])}', O_STATE_MATCHED_DOC4 = '{str(documents_info[6]["Res_State"]) + "," +  str(documents_info[7]["Res_State_Percentage"])}', O_STATE_MATCHED_DOC6 = '{str(documents_info[12]["Res_State"]) + "," +  str(documents_info[13]["Res_State_Percentage"])}',
        
        O_PINCODE_MATCHED_DOC1 = '{documents_info[0]["Res_pin"] + "," + str(documents_info[1]["Res_pin_Percentage"])}', O_PINCODE_MATCHED_DOC2 = '{documents_info[2]["Res_pin"] + "," +  str(documents_info[3]["Res_pin_Percentage"])}', O_PINCODE_MATCHED_DOC3 = '{documents_info[4]["Res_pin"] + "," +  str(documents_info[5]["Res_pin_Percentage"])}', O_PINCODE_MATCHED_DOC4 = '{documents_info[6]["Res_pin"] + "," + str(documents_info[7]["Res_pin_Percentage"])}', O_PINCODE_MATCHED_DOC6 = '{documents_info[12]["Res_pin"] + "," + str(documents_info[13]["Res_pin_Percentage"])}',
        
       
        O_REMARK='{documents_info[11]}', O_PROC_FLAG=1,  O_LUPD_DATE =now()
                             WHERE  
                             P_BATCH_ID='{row[1]}' and P_ACK_NO='{ack_no}' """
        #print(sql_update_qry)
        cursor.execute(sql_update_qry)
        connection.commit()
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")
        end_8 = time.time()
        P8_time = end_8 - start_8

    else:
        # if ack no did not match P_PER_MATCHED = 0 ,  P_MATCG_STATUS = NO ACK  ,  P_PROC_FLAG =1  P_LUPD_DATE =now()
        connection = con.connect(host=host,user=user, passwd=passwd,database=database)
        cursor = connection.cursor()
        sql_update_qry = f"""UPDATE {table} SET O_PERCENT_PDF_MATCHED = 0, O_MATCH_STATUS= 'NO ACK', O_REMARK= 'NO ACK', O_PROC_FLAG=1,  O_LUPD_DATE =now()
                             WHERE  
                             P_BATCH_ID='{row[1]}' and P_ACK_NO='{ack_no}' """
        #print(sql_update_qry)
        cursor.execute(sql_update_qry)
        connection.commit()
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")


# In[11]:


def start_process_3(u_id,file_type):
    try:
        connection = con.connect(host=host,user=user, passwd=passwd,database=database)
        table = "PAN_CUSTOMER_DATA1"
        sql_select_Query = f"select * from {table} where P_BATCH_ID = '{u_id}'"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")
            
        print("Total number of rows in table: ", cursor.rowcount)
        #print("\nStarting Threading \n")
        
        #threading 
        if len(records)>8:
            var1 = len(records)//8
            #print(var1)
            p_record_t1 = records[:var1]
            #print(p_record_t1)
            p_record_t2 = records[var1:2*(var1)]
            #print(p_record_t2)
            p_record_t3 = records[2*(var1):3*(var1)]
            #print(p_record_t3)
            p_record_t4 = records[3*(var1):4*(var1)]
            #print(p_record_t4)
            p_record_t5 = records[4*(var1):5*(var1)]
            p_record_t6 = records[5*(var1):6*(var1)]
            p_record_t7 = records[6*(var1):7*(var1)]
            p_record_t8 = records[7*(var1):]
            
            thread1 = threading.Thread(target=threading_start,args=(p_record_t1,table,file_type,"Thread 1 Started"))
            thread2 = threading.Thread(target=threading_start,args=(p_record_t2,table,file_type,"Thread 2 Started"))
            thread3 = threading.Thread(target=threading_start,args=(p_record_t3,table,file_type,"Thread 3 Started"))
            thread4 = threading.Thread(target=threading_start,args=(p_record_t4,table,file_type,"Thread 4 Started"))
            thread5 = threading.Thread(target=threading_start,args=(p_record_t5,table,file_type,"Thread 5 Started"))
            thread6 = threading.Thread(target=threading_start,args=(p_record_t6,table,file_type,"Thread 6 Started"))
            thread7 = threading.Thread(target=threading_start,args=(p_record_t7,table,file_type,"Thread 7 Started"))
            thread8 = threading.Thread(target=threading_start,args=(p_record_t8,table,file_type,"Thread 8 Started"))
            
            thread1.start()
            thread2.start()
            thread3.start()
            thread4.start()
            thread5.start()
            thread6.start()
            thread7.start()
            thread8.start()
            
            thread1.join()
            thread2.join()
            thread3.join()
            thread4.join()
            thread5.join()
            thread6.join()
            thread7.join()
            thread8.join()
        else:
            for row in records:
                ocrstart(row,table,file_type)

    except Exception as e:
        print("Exception: ", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")
    


# In[12]:


def start_process_4(u_id,file_type):
    if True:
        connection = con.connect(host=host,user=user, passwd=passwd,database=database)
        table = "PAN_CUSTOMER_DATA1"
        sql_select_Query = f"select * from {table} where P_BATCH_ID = '{u_id}'"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")
            
        print("Total number of rows in table: ", cursor.rowcount)
        #print("\nStarting Threading \n")
        
        #threading 
        if len(records)>8:
            var1 = len(records)//8
            #print(var1)
            p_record_t1 = records[:var1]
            #print(p_record_t1)
            p_record_t2 = records[var1:2*(var1)]
            #print(p_record_t2)
            p_record_t3 = records[2*(var1):3*(var1)]
            #print(p_record_t3)
            p_record_t4 = records[3*(var1):4*(var1)]
            #print(p_record_t4)
            p_record_t5 = records[4*(var1):5*(var1)]
            p_record_t6 = records[5*(var1):6*(var1)]
            p_record_t7 = records[6*(var1):7*(var1)]
            p_record_t8 = records[7*(var1):]
            
            thread1 = threading.Thread(target=threading_start,args=(p_record_t1,table,file_type,"Thread 1 Started"))
            thread2 = threading.Thread(target=threading_start,args=(p_record_t2,table,file_type,"Thread 2 Started"))
            thread3 = threading.Thread(target=threading_start,args=(p_record_t3,table,file_type,"Thread 3 Started"))
            thread4 = threading.Thread(target=threading_start,args=(p_record_t4,table,file_type,"Thread 4 Started"))
            thread5 = threading.Thread(target=threading_start,args=(p_record_t5,table,file_type,"Thread 5 Started"))
            thread6 = threading.Thread(target=threading_start,args=(p_record_t6,table,file_type,"Thread 6 Started"))
            thread7 = threading.Thread(target=threading_start,args=(p_record_t7,table,file_type,"Thread 7 Started"))
            thread8 = threading.Thread(target=threading_start,args=(p_record_t8,table,file_type,"Thread 8 Started"))
            
            thread1.start()
            thread2.start()
            thread3.start()
            thread4.start()
            thread5.start()
            thread6.start()
            thread7.start()
            thread8.start()
            
            thread1.join()
            thread2.join()
            thread3.join()
            thread4.join()
            thread5.join()
            thread6.join()
            thread7.join()
            thread8.join()
            
            ##update processing table
            
        else:
            threading_start(records,table,file_type,"no Threading!!!")
            #for row in records:
             #   ocrstart(row,table,file_type)

    else:
        print("Exception: ")
  
    


# In[13]:


def thread_name_status_update(p_record,msg):
    connection = con.connect(host=host,user=user, passwd=passwd,database=database)
    table = "PAN_CUSTOMER_DATA1"
    cursor = connection.cursor()
    p_record = list(p_record)
    #print(p_record)
    for i in p_record:
        
        sql_update_Query = f"""UPDATE {table} SET THREADING_NAME = '{msg}'
                            WHERE  P_ACK_NO='{i[5]}' """
        
        #print(sql_update_qry)
        cursor.execute(sql_update_Query)
        
    connection.commit()
    if connection.is_connected():
        cursor.close()
        connection.close()
        #print("MySQL connection is closed")     
    
    


# In[14]:


"""
def threading_start(p_record,table,file_type,msg):
    print(msg)
    thread_name_status_update(p_record,msg)
    for row in p_record:
        ocrstart(row,table,file_type)
"""


# In[15]:


def threading_start(p_record,table,file_type,msg):
    count = 1
    #thread_name_status_update(p_record,msg)
    for row in p_record:
        try:
            ocrstart(row,table,file_type)
            #print('Thread Running-',msg,count)
            count+=1
        except Exception as e:
            print("ocr start exception: ",e)
        
        try:
            connection = con.connect(host=host,user=user, passwd=passwd,database=database)
            cursor = connection.cursor()
            sql_insert_qry = f"""INSERT INTO PROCESS_PERFORMANCE_CHK VALUES('{row[5]}','{P1_time}','{P2_time}','{P3_time}','{P4_time}','{P5_time}','{P6_time}','{P7_time}',
            '{P8_time}','{P9_time}') """
            cursor.execute(sql_insert_qry)

            sql_insert_qry = f"""UPDATE PAN_FILE_PROCESSING_STATUS SET P_PROCESSING_PERCENTAGE =(select CONCAT(((select count(*) from  PAN_CUSTOMER_DATA1 where O_PROC_FLAG='1' and P_BATCH_ID='{row[1]}')/(select  count(*)  from PAN_CUSTOMER_DATA1 where P_BATCH_ID='{row[1]}'))*100, ''))  where P_BATCH_ID='{row[1]}'"""
            #print(sql_insert_qry)
            cursor.execute(sql_insert_qry)

            connection.commit()
            if connection.is_connected():
                cursor.close()
                connection.close()
                #print("MySQL connection_performance is closed")
        except Exception as e:
            print("Database insert exception: ",e)

        


# In[16]:







