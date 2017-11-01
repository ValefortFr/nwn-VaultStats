#!/usr/bin/env python
# -*- coding: utf-8 -*-

def TwoDAToDic(original):
    tidy_dic ={}

    for line in original:
        line = line.replace('\t',' ')  #replace tabulations by 1 space
        
        #remove trailing whitespaces
        line = line.strip()
        # some people are annoying and use labels with spaces contained in quotations
        
        listquotations = [pos for pos, char in enumerate(line) if char =='"']
        
        if len(listquotations) ==2:
            line = line[0:listquotations[0]]+line[(listquotations[0]+1):listquotations[1]].replace(' ','')+line[(listquotations[1]+1):]
         
        # turn it into a list, we still have the whitespaces inside the string
        step1 = line.split(' ')
        
        # Get rid of those
        
        step2 = [x for x in step1 if x]
       
        if len(step2) == 0:
            # yes i'm a sinner
			pass
        else:
            if step2[0] == "2DA":
                pass
            else:
                # if it's actually a line then its first element will be an integer
                try:
                    step2[0] = int(step2[0])
                    # time to make an entry in the dictionary	
                    tidy_dic[step2[0]] = {}
                    
                    for i in range(len(step2)):
                        tidy_dic[step2[0]][i] = step2[i]
                except:
                    # names of the columns
                    tidy_dic['column']={}
                    tidy_dic['column'][0]= ''
                    for i in range(len(step2)):
                        tidy_dic['column'][i+1] = step2[i]
                        
    return tidy_dic
