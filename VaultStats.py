#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Valefort 30/09/2017

# version 1.00

# Main file of the Vault stat generator 

# No arguments are required, the GUI is launched and waits for user input

from GUI import Vault_stats_GUI
from Utils import TwoDATFunctions
from Utils import Stats
import About
from pynwn import BICDirectoryContainer
from pynwn import PlayerCharacter
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
from queue import Queue


import fnmatch
import wx
import os


class VaultStats(Vault_stats_GUI.Vault_stats_GUI):
    # méthode d'intialisation de l'application, on lance la GUI    
    def __init__(self):
    
        # lancement de la GUI
        Vault_stats_GUI.Vault_stats_GUI.__init__(self,None, -1, 'Vault stats generator')

        # menu et init list control        
        self.InitMenu()        
        
        # bind des contrôles        
        self.BindAll()
        
        # initialisation des structures de données        
        self.ClearData()
        
        # Mouais, devrait pas être nécessaire
        self.Layout()
        self.Fit()

    # Méthode de création des menus            
    def InitMenu(self):
        menuBar = wx.MenuBar()
        self.SetMenuBar(menuBar)

        File=wx.Menu()
        File.Append(101, "&Close")
        menuBar.Append(File, "&File")
        
        About=wx.Menu()
        About.Append(201, "&About")
        menuBar.Append(About, "&About")
        
        self.Bind(wx.EVT_MENU, self.OnClose , id=101)        
        self.Bind(wx.EVT_MENU, self.OnAbout , id=201)

    # Méthode de fermeture de l'application
    def OnClose(self,event=None):
        self.Destroy()

    # Méthode d'affichage du About, affichant la version et les informations relatives à l'application            
    def OnAbout(self,event):
        self.aboutFrame=About.About(self)
        self.aboutFrame.Show()                 
        self.aboutFrame.SetFocus()
        self.aboutFrame.CentreOnParent()

    # Méthode regroupant l'ensemble des binds des événements concernant la GUI        
    def BindAll(self):                
        self.BTN_BrowseFolder.Bind(wx.EVT_BUTTON,self.OnBTN_BrowseFolder)        
        
        self.TC_Classes2da.Bind(wx.EVT_TEXT, self.OnTC_Classes2da)
        self.BTN_BrowseClasses.Bind(wx.EVT_BUTTON, self.OnBTN_BrowseClasses)
        
        self.TC_Subraces2da.Bind(wx.EVT_TEXT, self.OnTC_Subraces2da)
        self.BTN_BrowseSubraces.Bind(wx.EVT_BUTTON, self.OnBTN_BrowseSubraces)
        
        self.BTN_Clear.Bind(wx.EVT_BUTTON, self.OnBTN_Clear)
        
        self.BTN_GenerateReport.Bind(wx.EVT_BUTTON, self.OnBTN_GenerateReport)
        
    # Méthode permettant de remettre les données à zéro
    def ClearData(self):
        self.listBaseClasses = []
        self.dicoSubRaces    = {}        
        self.dicoClasses     = {}        
        self.dicoAlignements = {}
        
        # Récupération des données
        self.FetchData()
        
    # Méthode utlisée pour récuperer les données nécessaires au fonctionnement
    def FetchData(self):
        self.listBaseClasses = [0,1,2,3,4,5,6,7,8,9,10,39,55,58,59]
        
        self.dicoClasses = {
                            0:	'Barbarian',
                            1:	'Bard',
                            2:	'Cleric',
                            3:	'Druid',
                            4:	'Fighter',
                            5:	'Monk',
                            6:	'Paladin',
                            7:	'Ranger',
                            8:	'Rogue',
                            9:	'Sorcerer',
                            10:	'Wizard',
                            11:	'Aberration',
                            12:	'Animal',
                            13:	'Construct',
                            14:	'Humanoid',
                            15:	'Monstrous',
                            16:	'Elemental',
                            17:	'Fey',
                            18:	'Dragon',
                            19:	'Undead',
                            20:	'Commoner',
                            21:	'Beast',
                            22:	'Giant',
                            23:	'MagicBeast',
                            24:	'Outsider',
                            25:	'Shapechanger',
                            26:	'Vermin',
                            27:	'Shadowdancer',
                            28:	'Harper',
                            29:	'Arcane_Archer',
                            30:	'Assassin',
                            31:	'Blackguard',
                            32:	'Divine_Champion',
                            33:	'WeaponMaster',
                            34:	'Pale_Master',
                            35:	'Plant',
                            36:	'Dwarven_Defender',
                            37:	'Dragon_Disciple',
                            38:	'Ooze',
                            39:	'Warlock',
                            40:	'Arcane_Trickster',
                            43:	'Frenzied_Berserker',
                            45:	'Sacred_Fist',
                            46:	'Shadow_Thief_of_Amn',
                            47:	'NWNine_Warder',
                            50:	'Duelist',
                            51:	'Warpriest',
                            52:	'Eldritch_Knight',
                            53:	'Red_Wizard',
                            54:	'Arcane_Scholar',
                            55:	'Spirit_Shaman',
                            56:	'Stormlord',
                            57:	'Invisible_Blade',
                            58:	'Favored_Soul',
                            59:	'Swashbuckler',
                            60:	'Doomguide',
                            61:	'HellfireWarlock'                
                           }
        
        self.dicoSubRaces = {
                            0:	'Gold_Dwarf',
                            1:	'Gray_Dwarf_Duergar',
                            2:	'Shield_Dwarf',
                            3:	'Drow',
                            4:	'Moon_Elf',
                            5:	'Sun_Elf',
                            6:	'Wild_Elf',
                            7:	'Wood_Elf',
                            8:	'Deep_Gnome_Svirfneblin',
                            9:	'Rock_Gnome',
                            10:	'Ghostwise_Halfling',
                            11:	'Lightfoot_Halfling',
                            12:	'Strongheart_Halfling',
                            13:	'Aasimar',
                            14:	'Tiefling',
                            15:	'HalfElf',
                            16:	'HalfOrc',
                            17:	'Human',
                            18:	'Air_Genasi',
                            19:	'Earth_Genasi',
                            20:	'Fire_Genasi',
                            21:	'Water_Genasi',
                            22:	'Aberration',
                            23:	'Animal',
                            24:	'Beast',
                            25:	'Construct',
                            26:	'Humanoid_Goblinoid',
                            27:	'Humanoid_Monstrous',
                            28:	'Humanoid_Orc',
                            29:	'Humanoid_Reptilian',
                            30:	'Elemental',
                            31:	'Fey',
                            32:	'Giant',
                            33:	'Outsider',
                            34:	'Shapechanger',
                            35:	'Undead',
                            36:	'Vermin',
                            37:	'Ooze',
                            38:	'Dragon',
                            39:	'Magical_Beast',
                            40:	'Incorporeal',
                            41:	'Githyanki',
                            42:	'Githzerai',
                            43:	'HalfDrow',
                            44:	'Plant',
                            45:	'Hagspawn',
                            46:	'HalfCelestial',
                            47:	'YuantiPureblood',
                            48:	'GrayOrc'
                           }
        
        if self.TC_Classes2da.GetValue() != '':
            self.GetCustomClasses(self.TC_Classes2da.GetValue())

        if self.TC_Subraces2da.GetValue() != '':
            self.GetCustomRaces(self.TC_Subraces2da.GetValue())    
            
        # remplissage des contrôles le nécessitant        
        self.PopulateControls()

    # Fonction chargée de construire un dictionnaire des classes à partir d'un fichier 2da
    def GetCustomClasses(self, file):        
        try:
            dicoClassesFull = TwoDATFunctions.TwoDAToDic(file)
            
            # Où est la colonne PreReqTable ?
            preReqTableIndex = 0        
            for key, value in dicoClassesFull['column'].iteritems():
                if value == 'PreReqTable':
                    preReqTableIndex = key
            
            for key in dicoClassesFull.iterkeys():
                 if dicoClassesFull[key][1]!= '****' and key !='column':
                     self.dicoClasses[key] = dicoClassesFull[key][1]
                     if dicoClassesFull[key][preReqTableIndex] == '****':
                        self.listBaseClasses.append(key)
        
            self.PopulateControls()
        except:
            dlg = wx.MessageDialog(self,"Invalid 2da files or error parsing it.","Error",style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    # Fonction chargée de construire un dictionnaire des races à partir d'un fichier 2da
    def GetCustomRaces(self, file):        
        try:
            dicoSubRacesFull = TwoDATFunctions.TwoDAToDic(file)
            
            for key in dicoSubRacesFull.iterkeys():
                if dicoSubRacesFull[key][1]!= '****' and key !='column':
                    self.dicoSubRaces[key] = dicoSubRacesFull[key][1]

            self.PopulateControls()
        except:
            dlg = wx.MessageDialog(self,"Invalid 2da files or error parsing it.","Error",style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        
    # On nettoie et remplit les combobox
    def PopulateControls(self):
        self.CB_Class.Clear()
        self.CB_Subrace.Clear()
        self.CB_Gender.Clear()
        
        self.Fill_CB_Class()
        self.Fill_CB_Gender()
        self.Fill_CB_Subrace()
        
    # Méthode permettant de remplir la CB_Class      
    def Fill_CB_Class(self):            
        self.CB_Class.Append('All')
        
        for element in self.dicoClasses.values():
            self.CB_Class.Append(element)
            
        self.CB_Class.SetSelection(0)
    
    # Méthode permettant de remplir la CB_Gender      
    def Fill_CB_Gender(self):            
        self.CB_Gender.Append('All')
        self.CB_Gender.Append('Male')
        self.CB_Gender.Append('Female')
            
        self.CB_Gender.SetSelection(0)

    # Méthode permettant de remplir la CB_Subrace            
    def Fill_CB_Subrace(self):        
        self.CB_Subrace.Append('All')
        for element in self.dicoSubRaces.values():
            self.CB_Subrace.Append(element)
            
        self.CB_Subrace.SetSelection(0)
            
    # Méthode répondant à l'utilisation du bouton Clear, permet de nettoyer les champs textes dans la partie input    
    def OnBTN_Clear(self,event):
        self.PopulateControls()
        
        self.TC_Deity.Clear()        
        self.TC_Experience.SetValue('0')
        self.TC_Gold.SetValue('0')
        
        self.RB_ExpSuperior.SetValue(True)
        self.RB_ExpInferior.SetValue(False)
        self.RB_GoldSuperior.SetValue(True)
        self.RB_GoldInferior.SetValue(False)

    def OnBTN_BrowseFolder(self, event):
        dlg = wx.DirDialog (None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.TC_Folder.SetValue(dlg.GetPath())

            time = len(fnmatch.filter(os.listdir(dlg.GetPath()), '*.bic'))*0.0425
            self.TC_Time.SetValue(str(time)+'s. ')
        dlg.Destroy()
        
        try:
            str(self.TC_Folder.GetValue())
        except:
            dlg = wx.MessageDialog(self,"Due to headache encoding issues that I will solve one day please move the BIC files to a folder with old shitty ASCII characters or it won't work. Sorry.","Error",style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.TC_Folder.SetValue('')
            return

    def OnTC_Classes2da(self, event):
        try:
            with open(self.TC_Classes2da.GetValue(), 'r') as file:
                self.GetCustomClasses(file)
        except IOError:
            wx.LogError("Cannot open file '%s'." % file)

    def OnBTN_BrowseClasses(self,event):
        with wx.FileDialog(self, "Select your Classes.2DA file", wildcard="2DA files (*.2DA)|*.2DA", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.TC_Classes2da.SetValue(fileDialog.GetPath())
            fileDialog.Destroy()
        
    def OnTC_Subraces2da(self, event):
        try:
            with open(self.TC_Subraces2da.GetValue(), 'r') as file:
                self.GetCustomRaces(file)
        except IOError:
            wx.LogError("Cannot open file '%s'." % file)
        
    def OnBTN_BrowseSubraces(self, event):
        with wx.FileDialog(self, "Select your racialsubtypes.2DA file", wildcard="2DA files (*.2DA)|*.2DA", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.TC_Subraces2da.SetValue(fileDialog.GetPath())
            fileDialog.Destroy()

    def OnBTN_GenerateReport(self, event):
        # Récupération des filtres
        
        dicoFilter = {}
        
        dicoFilter['class']               = self.CB_Class.GetValue()
        dicoFilter['deity']               = self.TC_Deity.GetValue()
        dicoFilter['experienceSuperior']  = self.RB_ExpSuperior.GetValue()
        dicoFilter['experience']          = self.TC_Experience.GetValue()
        dicoFilter['gender']              = self.CB_Gender.GetValue()
        dicoFilter['goldSuperior']        = self.RB_GoldSuperior.GetValue()
        dicoFilter['gold']                = self.TC_Gold.GetValue()
        dicoFilter['subrace']             = self.CB_Subrace.GetValue()
        dicoFilter['cake']                = self.Check_PieCharts.GetValue()
        dicoFilter['eachrace']            = self.Check_EachRace.GetValue()
        
        try:
            dicoFilter['experience']= int(dicoFilter['experience'])
        except:
            dlg = wx.MessageDialog(self,"Experience points are integers you troll.","Error",style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.TC_Experience.SetValue('0')
            return
        
        try:
            dicoFilter['gold']= int(dicoFilter['gold'])
        except:
            dlg = wx.MessageDialog(self,"Aren't you smart ? Gold amount is an integer, for real.","Error",style = wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.TC_Gold.SetValue('0')
            return
        
        
        dlg = wx.DirDialog (None, "Choose output directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        outputdir = dlg.GetPath()
        dlg.Destroy()
        
        self.vaultStats = Stats.VaultStatsWork(self, str(self.TC_Folder.GetValue()), outputdir, self.listBaseClasses, self.dicoSubRaces, self.dicoClasses, dicoFilter)        
        self.vaultStats.DoStats()

    def OnBicParsed(self, event):
        self.counter +=1        
        self.TC_Time.SetValue(str(100*self.counter/self.totalBICFiles)+'% '+event.GetFileName())
        
        if self.counter >= self.totalBICFiles:
            self.vaultStats.Finish()
        
class MyApp(wx.App):   
    def OnInit(self):
        frame = VaultStats()
        self.SetTopWindow(frame)
        frame.Show()
        return True        
    
if __name__ == "__main__":    
    app = MyApp(False)
    app.MainLoop()  