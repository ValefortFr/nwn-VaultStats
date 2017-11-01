# coding: utf-8

import time
import os
from pynwn import BICDirectoryContainer
from pynwn import PlayerCharacter
import matplotlib.pyplot as plt
import numpy as np
from queue import Queue
from threading import Thread
import wx

myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)


class BicFinishedEvent(wx.PyCommandEvent):
    """Event to signal that a bic file has been parsed"""
    def __init__(self, etype, eid, fileName=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.fileName = fileName

    def GetFileName(self):
        """Returns the fileName from the event.
        @return: the fileName of this event

        """
        return self.fileName    

class BicWorker(Thread):
   def __init__(self, parent, queue):
       Thread.__init__(self)
       self.queue = queue
       self.parent = parent

   def run(self):
       while True:
           # Get the work from the queue and expand the tuple
           resref = self.queue.get()
           self.parent.bicParsedDico[resref] = self.parent.ExtractInfo(resref)
           evt = BicFinishedEvent(myEVT_COUNT, -1, resref)
           wx.PostEvent(self.parent.parent, evt)
           self.queue.task_done()
           
class VaultStatsWork():
    def __init__(self, parent, localvaultdir, outputdir, listBaseClasses, dicoSubRaces, dicoClasses, dicoFilter):
        self.parent                  = parent
        self.outputdir               = outputdir
        self.listBaseClasses         = listBaseClasses
        self.dicoSubRaces            = dicoSubRaces
        self.dicoClasses             = dicoClasses
        self.dicoFilter              = dicoFilter
        self.localvaultdir           = localvaultdir
        
        self.timeStart = time.clock()        
        self.bicParsedDico = {}
        
        self.parent.Bind(EVT_COUNT, self.parent.OnBicParsed)

    def Finish(self):
        bicFilesDico = self.Filter()
        
        self.DoBreakdown(bicFilesDico)
        
        # Write to TXT    
        self.WriteToTxt()
        
        #Graphs    
        if self.dicoFilter['cake']:            
            self.PlotAll()
        
        if self.dicoFilter['eachrace']:
            outputdir = self.outputdir
            
            for subrace in self.dicoSubRaces.values():
                self.dicoFilter['subrace'] = subrace
                
                bicFilesDico = self.Filter()
        
                if len(bicFilesDico) > 0:
                    self.outputdir = outputdir+'\\'+subrace
                    if not os.path.exists(self.outputdir):
                        os.makedirs(self.outputdir)
            
                    self.DoBreakdown(bicFilesDico)
                    
                    # Write to TXT    
                    self.WriteToTxt()
                    
                    #Graphs    
                    if self.dicoFilter['cake']:            
                        self.PlotAll()
                    
            
        self.parent.TC_Time.SetValue('Elapsed time : '+str(time.clock()-self.timeStart)+'s.')

    def DoBreakdown(self, bicFilesDico):
        self.prcBreakdownDic         = {}
        self.baseClassesBreakdownDic = {}
        self.subraceBreakdownDic     = {}
        self.subRaceDic              = {}
        self.deityBreakdownDic       = {}
        self.goldList                = []
        self.experienceList          = []
        
        self.alignementDic = {
                              'Good':0,  
                              'NeutralGEAxis':0,
                              'Evil':0,
                              'Chaotic':0,
                              'Lawful':0,
                              'NeutralLawAxis':0,
                              'Chaotic Good':0,  
                              'Chaotic Evil':0,
                              'Chaotic Neutral':0,
                              'Neutral Good':0,  
                              'Neutral Evil':0,
                              'Neutral':0,
                              'Lawful Good':0,  
                              'Lawful Evil':0,
                              'Lawful Neutral':0
                            }
        
        self.dicoGender ={'Male':0, 'Female':1}
        
        for element in self.listBaseClasses:
            self.baseClassesBreakdownDic[self.dicoClasses[element]]=0
        
        for key, value in self.dicoClasses.iteritems():
            self.prcBreakdownDic[value]=0
        
        for key, value in self.dicoSubRaces.iteritems():
            self.subraceBreakdownDic[value]=0
            self.subRaceDic[value]=key

        self.total = len(bicFilesDico)
        
        for bicDic in bicFilesDico.values():
            self.goldList.append(bicDic['gold'])
            self.experienceList.append(bicDic['experience'])
            self.subraceBreakdownDic[self.dicoSubRaces[bicDic['subrace']]]+=1
            deity = bicDic['deity']           
            if self.deityBreakdownDic.has_key(str(deity)):
                self.deityBreakdownDic[str(deity)]+=1
            else:
                self.deityBreakdownDic[str(deity)]=1   
            # class breakdown
            bestbaseClass = 0
            max = 0
            
            for classTuple in bicDic['ClassList']:                    
                if classTuple[0] in self.listBaseClasses and classTuple[1]>max:
                    max = classTuple[1]
                    bestbaseClass = classTuple[0]
                elif classTuple[0] not in self.listBaseClasses:
                    self.prcBreakdownDic[self.dicoClasses[classTuple[0]]] +=1
                    
            self.baseClassesBreakdownDic[self.dicoClasses[bestbaseClass]] +=1
            # alignment breakdown
            good = bicDic['good']
            chaos = bicDic['chaos']
            
            if (good > 69):
                self.alignementDic['Good'] +=1
                if (chaos < 31):
                    self.alignementDic['Chaotic'] +=1
                    self.alignementDic['Chaotic Good'] +=1
                elif (30 < chaos < 71):
                    self.alignementDic['NeutralLawAxis'] +=1
                    self.alignementDic['Neutral Good'] +=1
                else:
                    self.alignementDic['Lawful'] +=1
                    self.alignementDic['Lawful Good'] +=1
            elif ( 30 < good < 70):
                self.alignementDic['NeutralGEAxis'] +=1
                if (chaos < 31):
                    self.alignementDic['Chaotic'] +=1
                    self.alignementDic['Chaotic Neutral'] +=1
                elif (30 < chaos < 71):
                    self.alignementDic['NeutralLawAxis'] +=1
                    self.alignementDic['Neutral'] +=1
                else:
                    self.alignementDic['Lawful'] +=1
                    self.alignementDic['Lawful Neutral'] +=1
            else:
                self.alignementDic['Evil'] +=1
                if (chaos < 31):
                    self.alignementDic['Chaotic'] +=1
                    self.alignementDic['Chaotic Evil'] +=1
                elif (30 < chaos < 71):
                    self.alignementDic['NeutralLawAxis'] +=1
                    self.alignementDic['Neutral Evil'] +=1
                else:
                    self.alignementDic['Lawful'] +=1
                    self.alignementDic['Lawful Evil'] +=1

    def DoStats(self):
        self.localvaultdir = self.localvaultdir.replace("\\",'\\\\')
        self.localvault = BICDirectoryContainer(self.localvaultdir)
        
        self.parent.counter = 0
        self.parent.totalBICFiles = len(self.localvault.filenames)
        
        # Threads
        
        # Create a queue to communicate with the worker threads
        queue = Queue()
        
        worker = BicWorker(self, queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        
        for resref in self.localvault.filenames.iterkeys():
           queue.put(resref)
           
    def ExtractInfo(self, resref):
        bicInfoDic = {}
        try:
            bic = PlayerCharacter(resref, self.localvault)                
            
            bicInfoDic['subrace']    = bic.gff.get_field('Subrace').value
            bicInfoDic['gold']       = bic.gff.get_field('Gold').value
            bicInfoDic['experience'] = bic.gff.get_field('Experience').value
            bicInfoDic['deity']      = bic.gff.get_field('Deity').value
            bicInfoDic['good']       = bic.gff.get_field('GoodEvil').value
            bicInfoDic['chaos']      = bic.gff.get_field('LawfulChaotic').value                
            bicInfoDic['Gender']     = bic.gff.get_field('Gender').value            
            bicInfoDic['ClassList']  = [[x['Class'].value, x['ClassLevel'].value] for x in bic.gff.get_field('ClassList')]                
        except:
            print 'Incorrect file : '+resref
            
        return bicInfoDic 
                    
    def WriteToTxt(self):
        txtReport = os.path.join(self.outputdir, 'stats.txt')
        statFile = open(txtReport, 'w')
        
        statFile.write("self.total PCs for that filter : "+str(self.total)+'\n')
        
        statFile.write('\n')
        statFile.write("Base classes breakdown :"+'\n')
        statFile.write('\n')
        
        for key, value in self.baseClassesBreakdownDic.iteritems():
            statFile.write(key+' : '+str(value)+'.\n')
        
        statFile.write('\n')
        statFile.write("PRC breakdown :"+'\n')
        statFile.write('\n')
        
        for key, value in self.prcBreakdownDic.iteritems():
            statFile.write(key+' : '+str(value)+'.\n')
        
        statFile.write('\n')
        statFile.write("Alignments breakdown :"+'\n')
        statFile.write('\n')
        
        for key, value in self.alignementDic.iteritems():
            statFile.write(key+' : '+str(value)+' PCs are '+key+' aligned.\n')

        statFile.write('\n')
        statFile.write("Races breakdown :"+'\n')
        statFile.write('\n')
        
        for key, value in self.subraceBreakdownDic.iteritems():
            statFile.write(key+' : '+str(value)+'\n')

        statFile.write('\n')
        statFile.write("Deities breakdown :"+'\n')
        statFile.write('\n')
        
        for key, value in self.deityBreakdownDic.iteritems():
            statFile.write(key+' : '+str(value)+'\n') 

    def compare(self, a, b, boole):
        if boole:
            return (a > b)
        else:
            return (a < b)

    def autolabelh(self, rects):
        for rect in rects:
            width = rect.get_width()
            plt.text(width * 1.05, rect.get_y() + rect.get_height() / 2., '%d' % int(width), ha='left', va='center', fontdict={'size': 10})        

    def Filter(self):
        dicToReturn = {}
        for key, value in self.bicParsedDico.iteritems():
            try:
                classlist =  [x[0] for x in value['ClassList']]
                
                pcClasses = []        
                for classIndex in classlist:
                    pcClasses.append(self.dicoClasses[classIndex])
                
                if (    self.compare(value['experience'], int(self.dicoFilter['experience']), self.dicoFilter['experienceSuperior'])
                    and self.compare(value['gold'],       int(self.dicoFilter['gold']),       self.dicoFilter['goldSuperior'])
                    and (('' == self.dicoFilter['deity'])       or (value['deity']   == self.dicoFilter['deity']))
                    and (('All' == self.dicoFilter['gender'])   or (value['Gender']  == self.dicoGender[self.dicoFilter['gender']]))
                    and (('All' == self.dicoFilter['subrace'])  or (value['subrace'] == self.subRaceDic[self.dicoFilter['subrace']]))
                    and (('All' == self.dicoFilter['class'])    or (self.dicoFilter['class'] in pcClasses))):
                    dicToReturn[key] = value
            except:
                print('Extraction incorrect for : '+key)
        return dicToReturn

    def PlotAll(self):
        self.Histogram(self.goldList, "Gold")
        self.Histogram(self.experienceList, "Experience")
        
        self.BarChart(self.baseClassesBreakdownDic, "Base classes distribution")
        self.BarChart(self.prcBreakdownDic,         "Prestige classes distribution")
        self.BarChart(self.deityBreakdownDic,       "Deities distribution")
        
        self.PieCharts()

    def Histogram(self, list, title):
        fig, ax1 = plt.subplots(figsize=(20, 10))
        plt.hist(list, bins='auto')
        plt.title(title)    
        plt.savefig(os.path.join(self.outputdir, title+'distribution.png'))
        plt.close()
        
    def BarChart(self, breakdownDic, title):
        # Bar chart for base classes
        breakdownDic = {k: v for k, v in breakdownDic.iteritems() if v != 0} # remove null values        
        data = []
        
        for key, value in breakdownDic.iteritems():
            data.append((key, value))
        
        dtype = [('name', 'S64'), ('number', int)]        
        a = np.array(data, dtype=dtype)
        sorted_data = np.sort(a, order='number')  
        
        fig, ax1 = plt.subplots(figsize=(12, 15))
        
        pos = range(len(breakdownDic))
        
        for i in range(len(pos)): 
            pos[i] +=10*i
                
        bar = plt.barh(pos, sorted_data['number'],5,align='edge')
        plt.yticks(pos,sorted_data['name'], ha='right', va='bottom', size='small')
        plt.subplots_adjust(left=0.3)
        self.autolabelh(bar)
        
        plt.title(title)
        plt.savefig(os.path.join(self.outputdir, title+'.png'))    
        plt.close()

    def PieCharts(self):
        # Pie chart for races
        self.subraceBreakdownDic = {k: v for k, v in self.subraceBreakdownDic.iteritems() if v != 0} # remove null values
        
        fig, ax1 = plt.subplots(figsize=(10, 10))
        ax1.pie(self.subraceBreakdownDic.values(),labels=self.subraceBreakdownDic.keys(), autopct='%1.1f%%', shadow=False, startangle=0)
        ax1.axis('equal') 
        plt.title("Race distribution", fontsize=30)    
        plt.savefig(os.path.join(self.outputdir, 'RaceDistribution.png'))    
        plt.close()
        
        # Pie charts for alignments
        labels = ['Good', 'Neutral','Evil']
        sizes = [self.alignementDic['Good'], self.alignementDic['NeutralGEAxis'],self.alignementDic['Evil']]
        
        fig, ax1 = plt.subplots()
        ax1.pie(sizes,labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
        ax1.axis('equal')
        plt.title("Good-Evil distribution")  
        plt.savefig(os.path.join(self.outputdir, 'Good-Evildistribution.png'))    
        plt.close()
        
        labels = ['Chaotic', 'Lawful','NeutralLawAxis']
        sizes = [self.alignementDic['Chaotic'], self.alignementDic['Lawful'],self.alignementDic['NeutralLawAxis']]
        
        fig, ax1 = plt.subplots()
        ax1.pie(sizes,labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
        ax1.axis('equal')
        plt.title("Chaos-Law distribution")    
        plt.savefig(os.path.join(self.outputdir, 'Chaos-Lawdistribution.png'))    
        plt.close()
        
        labels = ['Chaotic Good', 'Chaotic Evil','Chaotic Neutral','Neutral Good','Neutral Evil','Neutral','Lawful Good','Lawful Evil','Lawful Neutral']
        sizes = [self.alignementDic['Chaotic Good'], self.alignementDic['Chaotic Evil'],self.alignementDic['Chaotic Neutral'],self.alignementDic['Neutral Good'],self.alignementDic['Neutral Evil'],self.alignementDic['Neutral'],self.alignementDic['Lawful Good'],self.alignementDic['Lawful Evil'],self.alignementDic['Lawful Neutral']]
        
        fig, ax1 = plt.subplots(figsize=(10, 10))
        ax1.pie(sizes,labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
        ax1.axis('equal')
        plt.title("Nine alignments distribution", fontsize=30)    
        plt.savefig(os.path.join(self.outputdir, 'NineAlignmentsDistribution.png'))    
        plt.close()    