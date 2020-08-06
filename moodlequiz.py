# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 09:16:42 2020

@author: cesarm
based on https://github.com/mrcinv/moodle-questions

This package help to generate a xml file with Moodel questions.
All questions are making as xml tree class, but the whole file is not a xml-tree
because it could be too much memory demanding. So each question is make and
write to file.
"""

import sys
import os
import tempfile as TMP
import time as T
import numpy as np
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import webbrowser
import glob
# from selenium import webdriver

'''
Utilities to make Moodle questionarie and preview it
General class: question
    specific modules:
        preview: show html version of question in a web breowser
        write: write question in xml moodle format
Question types classes: essay, cloze, multichoice, matching
    specific modules:
        xml: create a xml string from question class
        html: create html string from question class
Utilities:
    cloze_num: generate code to numerical answer into a cloze question.
    cloze_mc:  idem to multichoice answer
    cloze_sa:  idem to short answer
    lista:     generate code for list to use in any kind of question
    tabla:     idem for a table
    imagen:    idem for a image
    tmpfiles_rm: remove temporary files used by web browser
'''

@dataclass (init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class question():
    '''
    Parent class of all kind of quiestions, including common fields
    '''
    name: str # question name
    qsTx: str # question statement
    fback: str='' # general feedback
    grade: int=1 # default grade (unless clooze questions)
    pnlty: float=0 # penalty factor
    hiddn: int=0 # hidden
    qstn: str='' # type of question

    def __init__(self,name,qsTx,fback='to review the theoretical concepts',grade=1,pnlty=0,hiddn=0,qstn=''):
        self.name = name
        self.qsTx = qsTx
        self.fbcak = fback
        self.grade = grade
        self.pnlty = pnlty
        self.hiddn = hiddn
        self.qstn  = qstn

    # def preview(self,browserpath='',nsec=10):
    def preview(self,browserpath=''):
        '''
        Show questions on browser 
        
        Parameters
        ----------
        browserpath : TYPE, optional
            DESCRIPTION. Select browser to be used. Values ['' | 'all' | path to browser]
            At this moment it isn't work except with '' (default broowser).
            Choosing 'all', browsers and paths should be given into
            ... elif browserpath.lower()=='all':

        Raises
        ------
        ValueError
            DESCRIPTION. Error owing to open html file on webbrowser

        Returns
        -------
        tmpfile : TYPE
            DESCRIPTION. html file (temporal) using by browser.
            I test to use Temporary file or html code to overcome that file must 
            be remove later, but it don't work too. So a new file is create each 
            time that function is called and remove later. 

        '''
        secons = T.time_ns() % 1000000
        tmpfilename = './_tmp-mo{}.html'.format(int(secons))
        #      
        headcode = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'\
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
        #
        data2htm = self.html()
        code = ET.tostring(data2htm,encoding="unicode", method="xml")
        # There are problems with tag "string" that must be solved manually
        code = code.replace('/><link','></script><link')
        code = code.replace('&lt;','<')
        code = code.replace('&gt;','>')
        print('Writing temporal html file {} for question (kind={})'.format(tmpfilename,self.qstn))
        try:
            with open(tmpfilename,mode="w+",encoding="utf-8") as tmpfile:
                tmpfile.writelines([headcode+'\n',code])
        except (OSError,EOFError) as err:
            raise ValueError("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])
        finally:
            print('   file created successfully')
        #
        fullname = 'file://' + os.path.realpath(tmpfilename)
        if browserpath=='':
            webbrowser.open(fullname,new=1,autoraise=True)
        elif browserpath.lower()=='all':
            browsers = ['netscape','chrome']
            browpath = [r'C:/bin/Mozilla Firefox/firefox.exe',r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', None]
            for idx in range(len(browsers)+1):
                try:
                    if idx<len(browsers):
                        # tmp = webbrowser.get(browpath[idx])
                        webbrowser.register(browsers[idx],None,browpath[idx])
                        # webbrowser.get(browsers[idx]).open(fullname, new=1,autoraise=True)
                        webbrowser.get(browsers[idx])
                        webbrowser.open(fullname, new=1,autoraise=True)
                    else:
                        webbrowser.open(fullname,new=1,autoraise=True)
                    # webbrowser.close()
                except webbrowser.Error:
                    if browsers[idx] is None:
                        print("No hay navegador registrado.")
                    else:
                        print("No se ha encontrado {}".format(browsers[idx]))
                else:
                    if browsers[idx] is None:
                        print("Navegador por defecto.")
                    else:
                        print("Navegador {}".format(browsers[idx]))
        else:
            webbrowser.register('custom',None,browserpath)
            webbrowser.get('custom')
            webbrowser.open(fullname, new=1,autoraise=True)
        # T.sleep(nsec)
        return tmpfile
        
    def write(self,xmlfile,order=0,filetest=False):
        '''
        translate "question" class to xml code and write it to file "xmlfile"
        
        Parameters
        ----------
        xmlfile : TYPE, needed
            DESCRIPTION. File to store xml code for that question.
            In order to minimize code, basic item isn't quiz but question, because 
            a quiz could be made by a lot of questions and demand too much memory
            storage.
        order : 'first' (1), 'last' (-1), 'unique' (2) or 'between' (0). Order of that question.
        filetest : test if file exist or not before write it.

        Raises
        ------
        ValueError
            DESCRIPTION. Error owing to open xml file

        Returns
        -------
        None

        '''
        if order in (1,2) or (isinstance(order, (str)) and order.lower()[0] in ('f','u')): # file open to write, overwriting other data
            mode = 'w'
            print('Writing first question to file {} (kind={})'.format(xmlfile,self.qstn))
            if filetest and os.path.isfile(xmlfile):
                overwrite = input('File {} exist and its content will be removed. Are you sure y/[n]?'.format(xmlfile))
                if overwrite.lower()[0] == 'y' or overwrite.lower()[0] == 's':
                    pass
                else:
                    raise OSError('File {} will not be overwriting'.format(xmlfile))
        else:
            mode = 'a'
            if order in (-1,2) or (isinstance(order, (str)) and order.lower()[0] in ('l','u')): # file open to write, overwriting other data
                print('Writing last question to file {} (kind={})'.format(xmlfile,self.qstn))
            else:
                print('Writing another question to file {} (kind={})'.format(xmlfile,self.qstn))
            if filetest:
                if os.path.isfile(xmlfile):
                    pass
                else:
                    print('WARNING: {} file do not exist'.format(xmlfile))
                    overwrite = input('would you continue anyway (file could not be imported to moodle) y/[n]?')
                    if overwrite.lower()[0] == 'y' or overwrite.lower()[0] == 's':
                        pass
                    else:
                        raise ValueError('Process stopping')

        try:
            fullname = os.path.realpath(xmlfile)
            with open(fullname,mode=mode,encoding="utf-8") as file:
                if order in (1,2) or (isinstance(order, (str)) and order.lower()[0] in ('f','u')): # first question in quiz
                    txt = [r'<?xml version="1.0" encoding="UTF-8"?>','\n']
                    file.writelines(txt)
                    txt = [r'<quiz>','\n']
                    file.writelines(txt)
                
                data2xml = self.xml()
                xml2str = ET.tostring(data2xml,encoding="unicode", method="xml")
                # There are problems with tag "string" that must be solved manually
                code = xml2str.replace('&lt;','<')
                code = code.replace('&gt;','>')
                txt = ['\n',code,'\n']
                file.writelines(txt)

                if order in (-1,2) or (isinstance(order, (str)) and order.lower()[0] in ('l','u')): # last question in quiz
                    txt = ['\n',r'</quiz>']
                    file.writelines(txt)
                
        except (OSError) as e:     # input/output exception
            print("I/O Error {} accesing to file {} to write question\n".format(e,xmlfile))
        except (EOFError) as e:     # EOF exception
            print("EOF Error {} accesing to file {} to write question\n".format(e,xmlfile))
        finally:
            print('   question appended successfully')
        return None
     
class cloze(question):
    # dictionary with especific options: None
    def __init__(self,name,qsTx,fback='',grade=1,pnlty=0,hiddn=0,**kwargs):
        question.__init__(self,name,qsTx,fback,grade,pnlty,hiddn)
        self.qstn = 'cloze'

    def xml(self):
        '''
        Conversion from cloze class to xml code
        '''
        question = ET.Element('question',attrib={'type':self.qstn})
        qname = ET.SubElement(question,'name')
        qnmTx = ET.SubElement(qname,'text')
        qnmTx.text = self.name
        qsttm = ET.SubElement(question,'questiontext')
        qsttm.set('format','html')
        qstTx = ET.SubElement(qsttm,'text')
        qstTx.text = '<![CDATA['+self.qsTx+']]>'
        #
        qfdbk = ET.SubElement(question,'generalfeedback')
        qfdbk.set('format','html')
        qfbTx = ET.SubElement(qfdbk,'text')
        qfbTx.text = '<![CDATA[{}]]>'.format(self.fback)
        #
        tmp = ET.SubElement(question,'penalty')
        tmp.text = '{}'.format(self.pnlty)
        #
        tmp = ET.SubElement(question,'hidden')
        tmp.text = '{}'.format(self.hiddn)
        #
        return question
    
    def html(self):
        '''
        Conversion from cloze class to html code
        '''
        main = ET.Element('html',attrib={'xmlns':'"http://www.w3.org/1999/xhtml"'})
        head = ET.SubElement(main,'head')
        tmp = ET.SubElement(head,'meta',attrib={'http-equiv':'content-type','content':'text/html; charset=UTF-8'})
        tmp = ET.SubElement(head,'title')
        tmp.text = 'Python export to Moodle Quiz XHTML'+self.qstn
        tmp = ET.SubElement(head,'script',
                            attrib={'type':'text/javascript','charset':'UTF-8',
                                    'src':'https://me.kis.v2.scr.kaspersky-labs.com/FD126C42-EBFA'\
                                    '-4E12-B309-BB3FDD723AC1/main.js?attr=tW-CFu4NE4_z0UkozluzOeS'\
                                    'AQ8QUlm3h1AVdRSp2T7mE1Xk0L7INUcLHTr4d5uiY5E5ANid-2sJBONxku9Guepk'\
                                    '-GRpGzX_CEtnwc6-CMQ8n00MG53E9rvpA3A2K5YtiOjpvb-v7L4w8v9767ngg7K-'\
                                    'RWR_17o5jeQUOF3yPD3gljzcoq8I0GJey33uCq5zGxBvvppIx5Je5QvtJawL8jY0oR'\
                                    '_umy1CxyRP_XaLnfirpO9TklIxa5D2ub-PjjrH-rLgI1ggsBtHyERDR6StIb911d7'\
                                    'ctz7o9xtXaJZoGq9uV_tSkOrittGMSK7DZdKCA'})
        tmp = ET.SubElement(head,'link',
                            attrib={'rel':'stylesheet','crossorigin':'anonymous',
                                    'href':'https://me.kis.v2.scr.kaspersky-labs.com/E3E8934C-235A'\
                                    '-4B0E-825A-35A08381A191/abn/main.css?attr=aHR0cHM6Ly93d3cuY2F'\
                                    'tcHVzdmlydHVhbC51bmlvdmkuZXMvcGx1Z2luZmlsZS5waHAvMzcwNTYvcXVl'\
                                    'c3Rpb24vZXhwb3J0LzQ5MTcxL3hodG1sL3dpdGhjYXRlZ29yaWVzL3dpdGhjb'\
                                    '250ZXh0cy9wcmVndW50YXMtVF9TJTJjQV8lMjhHTUFURU0wMS0xLTAwOCUyYz'\
                                    'JHRklNQTAxLTEtMDA4JTI5LVBydWViYXMtMjAyMDA2MjYtMTY0NC5odG1sP2Z'\
                                    'vcmNlZG93bmxvYWQ9MQ'})
        tmp = ET.SubElement(head,'style',attrib={'type':'text/css'})
        tmp.text = 'body {font-family: Verdana, Helvetica, Sans-Serif;background-color: #fff;color: #000;}\n '\
        '.question {border: 1px solid #ddd;margin: 5px;padding: 3px;}\n '\
        '.question h3 {font-weight: normal;font-size: 125%;}\n '\
        '.question ul {list-style-type: none; }'
        body = ET.SubElement(main,'body')
        form = ET.SubElement(body,'form',attrib={'action':'...REPLACE ME...','method':'post'})
        #
        div  = ET.SubElement(form, 'div',attrib={'class':'question'})
        h3   = ET.SubElement(div,'h3')
        h3.text = '{} ({})'.format(self.name,'cloze')
        pfo1 = ET.SubElement(div,'p',attrib={'class':'questiontext'})
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = '{}'.format(self.qsTx)
        return main
    
class essay(question):
    '''
        moodle essay kind of question
        Specific options are stored as dictionary.
        Next lines show fiels names and matching xml code 
        
    <responseformat>editorfilepicker</responseformat>
    reqrd: <responserequired>1</responserequired>
    lines: <responsefieldlines>15</responsefieldlines>
    atch: <attachments>2</attachments>
    atreq: <attachmentsrequired>0</attachmentsrequired>
    ginf: <graderinfo format="html"><text><![CDATA[<p>??????</p>]]></text></graderinfo>
    rtem: <responsetemplate format="html"><text><![CDATA[<p>????</p>]]></text></responsetemplate>
    '''
    sopt: dict
       
    def __init__(self,name,qsTx,fback='',grade=1,pnlty=0,hiddn=0,**kwargs):
        question.__init__(self,name,qsTx,fback,grade,pnlty,hiddn)
        self.qstn = 'essay'
        self.sopt = {'reqrd':1,'lines':15,'atch':3,'atreq':0,'ginf':'','rtem':''}
        for clave, valor in kwargs.items():
            if clave.lower() in self.sopt.keys():
                self.sopt[clave] = valor
            else:
                print('key "{}" is not a valid options'.format(clave))

    def xml(self):
        '''
        Conversion from essay class to xml code
        '''
        question = ET.Element('question',attrib={'type':self.qstn})
        qname = ET.SubElement(question,'name')
        qnmTx = ET.SubElement(qname,'text')
        qnmTx.text = self.name
        qsttm = ET.SubElement(question,'questiontext')
        qsttm.set('format','html')
        qstTx = ET.SubElement(qsttm,'text')
        qstTx.text = '<![CDATA['+self.qsTx+']]>'
        #
        qfdbk = ET.SubElement(question,'generalfeedback')
        qfdbk.set('format','html')
        qfbTx = ET.SubElement(qfdbk,'text')
        qfbTx.text = '<![CDATA[{}]]>'.format(self.fback)
        #
        tmp = ET.SubElement(question,'defaultgrade')
        tmp.text = '{}'.format(self.grade)
        #
        tmp = ET.SubElement(question,'penalty')
        tmp.text = '{}'.format(self.pnlty)
        #
        tmp = ET.SubElement(question,'hidden')
        tmp.text = '{}'.format(self.hiddn)
        #
        tmp = ET.SubElement(question,'responseformat')
        tmp.text = 'editorfilepicker'
        #
        tmp = ET.SubElement(question,'responserequiredt')
        tmp.text = '{}'.format(self.sopt['reqrd'])
        #
        tmp = ET.SubElement(question,'responsefieldlines')
        tmp.text = '{}'.format(self.sopt['lines'])
        #
        tmp = ET.SubElement(question,'attachments')
        tmp.text = '{}'.format(self.sopt['atch'])
        #
        tmp = ET.SubElement(question,'attachmentsrequired')
        tmp.text = '{}'.format(self.sopt['atreq'])
        #
        tmpq = ET.SubElement(question,'graderinfo',attrib={'format':'html'})
        tmp  = ET.SubElement(tmpq,'text')
        tmp.text = '<![CDATA['+'{}'.format(self.sopt['ginf'])+']]>'
        #
        tmpq = ET.SubElement(question,'responsetemplate',attrib={'format':'html'})
        tmp  = ET.SubElement(tmpq,'text')
        tmp.text = '<![CDATA['+'{}'.format(self.sopt['rtem'])+']]>'
        #
        return question
    
    def html(self):
        '''
        Conversion from essay class to html code
        '''
        main = ET.Element('html',attrib={'xmlns':'"http://www.w3.org/1999/xhtml"'})
        head = ET.SubElement(main,'head')
        tmp = ET.SubElement(head,'meta',attrib={'http-equiv':'content-type','content':'text/html; charset=UTF-8'})
        tmp = ET.SubElement(head,'title')
        tmp.text = 'Python export to Moodle Quiz XHTML:'+self.qstn
        tmp = ET.SubElement(head,'script',
                            attrib={'type':'text/javascript','charset':'UTF-8',
                                    'src':'https://me.kis.v2.scr.kaspersky-labs.com/FD126C42-EBFA'\
                                    '-4E12-B309-BB3FDD723AC1/main.js?attr=tW-CFu4NE4_z0UkozluzOeS'\
                                    'AQ8QUlm3h1AVdRSp2T7mE1Xk0L7INUcLHTr4d5uiY5E5ANid-2sJBONxku9Guepk'\
                                    '-GRpGzX_CEtnwc6-CMQ8n00MG53E9rvpA3A2K5YtiOjpvb-v7L4w8v9767ngg7K-'\
                                    'RWR_17o5jeQUOF3yPD3gljzcoq8I0GJey33uCq5zGxBvvppIx5Je5QvtJawL8jY0oR'\
                                    '_umy1CxyRP_XaLnfirpO9TklIxa5D2ub-PjjrH-rLgI1ggsBtHyERDR6StIb911d7'\
                                    'ctz7o9xtXaJZoGq9uV_tSkOrittGMSK7DZdKCA'})
        tmp = ET.SubElement(head,'link',
                            attrib={'rel':'stylesheet','crossorigin':'anonymous',
                                    'href':'https://me.kis.v2.scr.kaspersky-labs.com/E3E8934C-235A'\
                                    '-4B0E-825A-35A08381A191/abn/main.css?attr=aHR0cHM6Ly93d3cuY2F'\
                                    'tcHVzdmlydHVhbC51bmlvdmkuZXMvcGx1Z2luZmlsZS5waHAvMzcwNTYvcXVl'\
                                    'c3Rpb24vZXhwb3J0LzQ5MTcxL3hodG1sL3dpdGhjYXRlZ29yaWVzL3dpdGhjb'\
                                    '250ZXh0cy9wcmVndW50YXMtVF9TJTJjQV8lMjhHTUFURU0wMS0xLTAwOCUyYz'\
                                    'JHRklNQTAxLTEtMDA4JTI5LVBydWViYXMtMjAyMDA2MjYtMTY0NC5odG1sP2Z'\
                                    'vcmNlZG93bmxvYWQ9MQ'})
        tmp = ET.SubElement(head,'style',attrib={'type':'text/css'})
        tmp.text = 'body {font-family: Verdana, Helvetica, Sans-Serif;background-color: #fff;color: #000;}\n '\
        '.question {border: 1px solid #ddd;margin: 5px;padding: 3px;}\n '\
        '.question h3 {font-weight: normal;font-size: 125%;}\n '\
        '.question ul {list-style-type: none; }'
        body = ET.SubElement(main,'body')
        form = ET.SubElement(body,'form',attrib={'action':'...REPLACE ME...','method':'post'})
        #
        div  = ET.SubElement(form, 'div',attrib={'class':'question'})
        h3   = ET.SubElement(div,'h3')
        h3.text = self.name+' (Essay, score:{})'.format(self.grade)
        pfo1 = ET.SubElement(div,'p',attrib={'class':'questiontext'})
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = self.qsTx
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = 'Response required: {}'.format(self.sopt['reqrd'])
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = 'Max. number of files:{}'.format(self.sopt['atch'])
        return main

class matching(question):
    # dictionary with especific options: None
    def __init__(self,name,qsTx,fback='',grade=1,pnlty=0,hiddn=0,**kwargs):
        question.__init__(self,name,qsTx,fback,grade,pnlty,hiddn)
        self.qstn = 'matching'
        # fbans: feedback for answers, (good, quite good, bad)
        # self.sopt = {'fbans':['Rigth answer','Answer is partially rigth','Bad answer'],'couples':[['option 1','answer 1'],['option 2','answer 2']]}
        self.sopt = {'fbans':['Correcto','Parcialmente correcto','Incorrecto'],'couples':[['opcion 1','respuesta 1'],['opcion 2','respuesta 2']]}
        for clave, valor in kwargs.items():
            clave = clave.lower()
            if clave in self.sopt.keys():
                if clave == 'fbans':
                    if isinstance(valor,(list,tuple,np.ndarray)):
                        for i in range(min(3,len(valor))):
                            self.sopt[clave][i] = valor[i]
                    elif isinstance(valor,str):
                        self.sopt[clave][0] = valor
                    else:
                        raise ValueError('key "{}" has not valid values:\n {}'.format(clave,valor))
                else: # clave = 'couples':
                    if isinstance(valor,(list,tuple,np.ndarray)):
                        if len(valor) < 2:
                            raise ValueError('key "{}" has not enough values:\n {}'.format(clave,valor))
                        else:
                            for i in range(len(valor)):
                                if isinstance(valor[i],(list,tuple,np.ndarray)) and len(valor[i])==2:
                                    pass
                                else:
                                    raise ValueError('key "{}", item {} is not a couple:\n {}'.format(clave,i,valor[i]))
                            self.sopt[clave] = valor
                    else:
                        raise ValueError('key "{}" has not valid values:\n {}'.format(clave,valor))
            else:
                print('key "{}" is not a valid options'.format(clave))

    def xml(self):
        '''
        Conversion from matching class to xml code
        '''
        question = ET.Element('question',attrib={'type':self.qstn})
        qname = ET.SubElement(question,'name')
        qnmTx = ET.SubElement(qname,'text')
        qnmTx.text = self.name
        qsttm = ET.SubElement(question,'questiontext')
        qsttm.set('format','html')
        qstTx = ET.SubElement(qsttm,'text')
        qstTx.text = '<![CDATA['+self.qsTx+']]>'
        #
        qfdbk = ET.SubElement(question,'generalfeedback')
        qfdbk.set('format','html')
        qfbTx = ET.SubElement(qfdbk,'text')
        qfbTx.text = '<![CDATA[{}]]>'.format(self.fback)
        #
        tmp = ET.SubElement(question,'defaultgrade')
        tmp.text = '{}'.format(self.grade)
        #
        tmp = ET.SubElement(question,'penalty')
        tmp.text = '{}'.format(self.pnlty)
        #
        tmp = ET.SubElement(question,'hidden')
        tmp.text = '{}'.format(self.hiddn)
        #
        tmp = ET.SubElement(question,'shuffleanswers')
        tmp.text = '{}'.format('true')
        #
        tmp = ET.SubElement(question,'correctfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][0])
        tmp = ET.SubElement(question,'partiallycorrectfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][1])
        tmp = ET.SubElement(question,'incorrectfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][2])
        #
        tmp = ET.SubElement(question,'shownumcorrect')
        #
        for iq in range(len(self.sopt['couples'])):
            tmp = ET.SubElement(question,'subquestion',attrib={'format':'html'})
            tmp2 = ET.SubElement(tmp,'text')
            tmp2.text = '<![CDATA[<p>{}</p>]]>'.format(self.sopt['couples'][iq][0])
            tmp2 = ET.SubElement(tmp,'answer')
            tmp3 = ET.SubElement(tmp2,'text')
            tmp3.text = '{}'.format(self.sopt['couples'][iq][1])
        #    
        return question
    
    def html(self):
        '''
        Conversion from matching class to html code
        '''
        main = ET.Element('html',attrib={'xmlns':'"http://www.w3.org/1999/xhtml"'})
        head = ET.SubElement(main,'head')
        tmp = ET.SubElement(head,'meta',attrib={'http-equiv':'content-type','content':'text/html; charset=UTF-8'})
        tmp = ET.SubElement(head,'title')
        tmp.text = 'Python export to Moodle Quiz XHTML'+self.qstn
        tmp = ET.SubElement(head,'script',
                            attrib={'type':'text/javascript','charset':'UTF-8',
                                    'src':'https://me.kis.v2.scr.kaspersky-labs.com/FD126C42-EBFA'\
                                    '-4E12-B309-BB3FDD723AC1/main.js?attr=tW-CFu4NE4_z0UkozluzOeS'\
                                    'AQ8QUlm3h1AVdRSp2T7mE1Xk0L7INUcLHTr4d5uiY5E5ANid-2sJBONxku9Guepk'\
                                    '-GRpGzX_CEtnwc6-CMQ8n00MG53E9rvpA3A2K5YtiOjpvb-v7L4w8v9767ngg7K-'\
                                    'RWR_17o5jeQUOF3yPD3gljzcoq8I0GJey33uCq5zGxBvvppIx5Je5QvtJawL8jY0oR'\
                                    '_umy1CxyRP_XaLnfirpO9TklIxa5D2ub-PjjrH-rLgI1ggsBtHyERDR6StIb911d7'\
                                    'ctz7o9xtXaJZoGq9uV_tSkOrittGMSK7DZdKCA'})
        tmp = ET.SubElement(head,'link',
                            attrib={'rel':'stylesheet','crossorigin':'anonymous',
                                    'href':'https://me.kis.v2.scr.kaspersky-labs.com/E3E8934C-235A'\
                                    '-4B0E-825A-35A08381A191/abn/main.css?attr=aHR0cHM6Ly93d3cuY2F'\
                                    'tcHVzdmlydHVhbC51bmlvdmkuZXMvcGx1Z2luZmlsZS5waHAvMzcwNTYvcXVl'\
                                    'c3Rpb24vZXhwb3J0LzQ5MTcxL3hodG1sL3dpdGhjYXRlZ29yaWVzL3dpdGhjb'\
                                    '250ZXh0cy9wcmVndW50YXMtVF9TJTJjQV8lMjhHTUFURU0wMS0xLTAwOCUyYz'\
                                    'JHRklNQTAxLTEtMDA4JTI5LVBydWViYXMtMjAyMDA2MjYtMTY0NC5odG1sP2Z'\
                                    'vcmNlZG93bmxvYWQ9MQ'})
        tmp = ET.SubElement(head,'style',attrib={'type':'text/css'})
        tmp.text = 'body {font-family: Verdana, Helvetica, Sans-Serif;background-color: #fff;color: #000;}\n '\
        '.question {border: 1px solid #ddd;margin: 5px;padding: 3px;}\n '\
        '.question h3 {font-weight: normal;font-size: 125%;}\n '\
        '.question ul {list-style-type: none; }'
        body = ET.SubElement(main,'body')
        form = ET.SubElement(body,'form',attrib={'action':'...REPLACE ME...','method':'post'})
        
        div  = ET.SubElement(form, 'div',attrib={'class':'question'})
        h3   = ET.SubElement(div,'h3')
        h3.text = '{} ({})'.format(self.name,'matching')
        pfo1 = ET.SubElement(div,'p',attrib={'class':'questiontext'})
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = '{}'.format(self.qsTx)
        #
        lista   = ET.SubElement(div,'ul',attrib={'class':'match'})
        ansnum = len(self.sopt['couples'])
        txtime = int(T.mktime(T.localtime()))
        for iq in range(ansnum):
            tmp = ET.SubElement(lista,'li')
            tmp2 = ET.SubElement(tmp,'p')
            tmp2.text = '{}'.format(self.sopt['couples'][iq][0])
            #
            ida = 'ans{}-{}'.format(txtime,iq)
            idm = 'men{}-{}'.format(txtime,iq)
            tmp = ET.SubElement(lista,'label',attrib={'class':'accesshide','for':ida})
            tmp.text = 'Answer {}: '.format(iq+1)
            #
            tmp = ET.SubElement(lista,'select',attrib={'id':ida,'class':'select {}'.format(idm),'name':ida})
            for ia in range(ansnum):
                tmp2 = ET.SubElement(tmp,'option',attrib={'value':'{}'.format(self.sopt['couples'][ia][1])})
                tmp2.text = '{}'.format(self.sopt['couples'][ia][1])
        #
        return main
        
class multichoice(question):
    # dictionary with especific options: None
    def __init__(self,name,qsTx,fback='',grade=1,pnlty=0,hiddn=0,**kwargs):
        question.__init__(self,name,qsTx,fback,grade,pnlty,hiddn)
        self.qstn = 'multichoice'
        self.sopt = {'sngl':True,'shfle':True,'nbing':'abc','fbans':['Correcto','Parcialmente correcto','Incorrecto'],
                     'triplets':[[1,'opcion 1','respuesta 1'],[0,'opcion 2','respuesta 2']]}
        if 'sngl' in kwargs:
            self.sopt['sngl'] = kwargs['sngl']
            kwargs.pop('sngl')
        for clave, valor in kwargs.items():
            if clave.lower() in self.sopt.keys():
                if clave == 'fbans':
                    if isinstance(valor,(list,tuple,np.ndarray)):
                        for i in range(min(3,len(valor))):
                            self.sopt[clave][i] = valor[i]
                    elif isinstance(valor,str):
                        pass
                    else:
                        raise ValueError('key "{}" has not valid values:\n {}'.format(clave,valor))
                    self.sopt[clave][0] = valor                
                elif clave == 'triplets':
                    if isinstance(valor,(list,tuple,np.ndarray)):
                        num3 = len(valor)
                        if num3 < 3:
                            raise ValueError('key "{}" has not enough values:\n {}'.format(clave,valor))
                        else:
                            weigth = np.zeros(num3) 
                            for i in range(num3):
                                if isinstance(valor[i],(list,tuple,np.ndarray)) \
                                and len(valor[i])==3 \
                                and isinstance(valor[i][0],(int,float)):
                                    weigth[i] = valor[i][0]
                                else:
                                    raise ValueError('key "{}", item {} is not a triplet:\n {}'.format(clave,i,valor[i]))
                            if self.sopt['sngl']: # Only one valid solution
                                if round(max(weigth),2) == 100:
                                    pass
                                else:
                                    raise ValueError('rigth item score  is not 100')
                            else:
                                if round(sum(num for num in weigth if num >= 0),2) == 100:
                                    pass
                                else:
                                    raise ValueError('sum of all rigth items are not 100')
                    else:
                        raise ValueError('key "{}" has not valid values:\n {}'.format(clave,valor))
                    self.sopt[clave] = valor
                else:
                    self.sopt[clave] = valor
            else:
                print('key "{}" is not a valid options'.format(clave))

    def xml(self):
        '''
        Conversion from multichoice class to xml code
        '''
        question = ET.Element('question',attrib={'type':self.qstn})
        qname = ET.SubElement(question,'name')
        qnmTx = ET.SubElement(qname,'text')
        qnmTx.text = self.name
        qsttm = ET.SubElement(question,'questiontext')
        qsttm.set('format','html')
        qstTx = ET.SubElement(qsttm,'text')
        qstTx.text = '<![CDATA['+self.qsTx+']]>'
        #
        qfdbk = ET.SubElement(question,'generalfeedback')
        qfdbk.set('format','html')
        qfbTx = ET.SubElement(qfdbk,'text')
        qfbTx.text = '<![CDATA[{}]]>'.format(self.fback)
        #
        tmp = ET.SubElement(question,'penalty')
        tmp.text = '{}'.format(self.pnlty)
        #
        tmp = ET.SubElement(question,'hidden')
        tmp.text = '{}'.format(self.hiddn)
        #
        # specific options
        tmp = ET.SubElement(question,'single')
        if self.sopt['sngl']:
            tmp.text = '{}'.format('true')
        else:
            tmp.text = '{}'.format('false')
        # 
        tmp = ET.SubElement(question,'answernumbering')
        tmp.text = '{}'.format('abc')
        #
        tmp = ET.SubElement(question,'shuffleanswers')
        if self.sopt['shfle']:
            tmp.text = '{}'.format('true')
        else:
            tmp.text = '{}'.format('false')
        #
        tmp = ET.SubElement(question,'correctfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][0])
        tmp = ET.SubElement(question,'partiallycorrectfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][1])
        tmp = ET.SubElement(question,'incorrectfeedback',attrib={'format':'html'})
        tmp2 = ET.SubElement(tmp,'text')
        tmp2.text = '{}'.format(self.sopt['fbans'][2])
        #
        tmp = ET.SubElement(question,'shownumcorrect')
        #
        for iq in range(len(self.sopt['triplets'])):
            tmp = ET.SubElement(question,'answer',attrib={'fraction':str(self.sopt['triplets'][iq][0]),'format':'html'})
            tmp2 = ET.SubElement(tmp,'text')
            tmp2.text = '<![CDATA[<p>{}</p>]]>'.format(self.sopt['triplets'][iq][1])
            tmp2 = ET.SubElement(tmp,'feedback',attrib={'format':'html'})
            tmp3 = ET.SubElement(tmp2,'text')
            tmp3.text = '<![CDATA[<p>{}</p>]]>'.format(self.sopt['triplets'][iq][2])
        #      
        return question
    
    def html(self):
        '''
        Conversion from multichoice class to html code
        '''
        main = ET.Element('html',attrib={'xmlns':'"http://www.w3.org/1999/xhtml"'})
        head = ET.SubElement(main,'head')
        tmp = ET.SubElement(head,'meta',attrib={'http-equiv':'content-type','content':'text/html; charset=UTF-8'})
        tmp = ET.SubElement(head,'title')
        tmp.text = 'Python export to Moodle Quiz XHTML'+self.qstn
        tmp = ET.SubElement(head,'script',
                            attrib={'type':'text/javascript','charset':'UTF-8',
                                    'src':'https://me.kis.v2.scr.kaspersky-labs.com/FD126C42-EBFA'\
                                    '-4E12-B309-BB3FDD723AC1/main.js?attr=tW-CFu4NE4_z0UkozluzOeS'\
                                    'AQ8QUlm3h1AVdRSp2T7mE1Xk0L7INUcLHTr4d5uiY5E5ANid-2sJBONxku9Guepk'\
                                    '-GRpGzX_CEtnwc6-CMQ8n00MG53E9rvpA3A2K5YtiOjpvb-v7L4w8v9767ngg7K-'\
                                    'RWR_17o5jeQUOF3yPD3gljzcoq8I0GJey33uCq5zGxBvvppIx5Je5QvtJawL8jY0oR'\
                                    '_umy1CxyRP_XaLnfirpO9TklIxa5D2ub-PjjrH-rLgI1ggsBtHyERDR6StIb911d7'\
                                    'ctz7o9xtXaJZoGq9uV_tSkOrittGMSK7DZdKCA'})
        tmp = ET.SubElement(head,'link',
                            attrib={'rel':'stylesheet','crossorigin':'anonymous',
                                    'href':'https://me.kis.v2.scr.kaspersky-labs.com/E3E8934C-235A'\
                                    '-4B0E-825A-35A08381A191/abn/main.css?attr=aHR0cHM6Ly93d3cuY2F'\
                                    'tcHVzdmlydHVhbC51bmlvdmkuZXMvcGx1Z2luZmlsZS5waHAvMzcwNTYvcXVl'\
                                    'c3Rpb24vZXhwb3J0LzQ5MTcxL3hodG1sL3dpdGhjYXRlZ29yaWVzL3dpdGhjb'\
                                    '250ZXh0cy9wcmVndW50YXMtVF9TJTJjQV8lMjhHTUFURU0wMS0xLTAwOCUyYz'\
                                    'JHRklNQTAxLTEtMDA4JTI5LVBydWViYXMtMjAyMDA2MjYtMTY0NC5odG1sP2Z'\
                                    'vcmNlZG93bmxvYWQ9MQ'})
        tmp = ET.SubElement(head,'style',attrib={'type':'text/css'})
        tmp.text = 'body {font-family: Verdana, Helvetica, Sans-Serif;background-color: #fff;color: #000;}\n '\
        '.question {border: 1px solid #ddd;margin: 5px;padding: 3px;}\n '\
        '.question h3 {font-weight: normal;font-size: 125%;}\n '\
        '.question ul {list-style-type: none; }'
        body = ET.SubElement(main,'body')
        form = ET.SubElement(body,'form',attrib={'action':'...REPLACE ME...','method':'post'})
        
        div  = ET.SubElement(form, 'div',attrib={'class':'question'})
        h3   = ET.SubElement(div,'h3')
        h3.text = '{} ({})'.format(self.name,'multichoice')
        pfo1 = ET.SubElement(div,'p',attrib={'class':'questiontext'})
        tmp = ET.SubElement(pfo1,'p')
        tmp.text = '{}'.format(self.qsTx)
        #
        lista   = ET.SubElement(div,'ul',attrib={'class':'multichoice'})
        ansnum = len(self.sopt['triplets'])
        txtime = int(T.mktime(T.localtime()))
        if self.sopt['sngl']:
            for iq in range(ansnum):
                tmp = ET.SubElement(lista,'li')
                data = self.sopt['triplets'][iq]
                tmp2 = ET.SubElement(tmp,'input',attrib={'name':'qst_{}'.format(txtime),
                                     'type':'radio',
                                     'value':'{} ({})'.format(data[0],data[2])})
                tmp2 = ET.SubElement(tmp,'p')
                tmp2.text = '{}'.format(data[1])
        else:
            for iq in range(ansnum):
                tmp = ET.SubElement(lista,'li')
                data = self.sopt['triplets'][iq]
                tmp2 = ET.SubElement(tmp,'input',attrib={'name':'qst_{}'.format(txtime),
                                     'type':'checkbox',
                                     'value':'{} ({})'.format(data[0],data[2])})
                tmp2 = ET.SubElement(tmp,'p')
                tmp2.text = '{}'.format(data[1])
# 
        return main   
     
     

def cloze_num(data,score=1):

    """
    Return formatted string for cloze numerical question
    Sintaxis:
        cloze_num(data,score=1)
    
    data: list or tuple with sublists {a,w,p,r}
        a: answer
        w: weigth for this answer (at least one must be one)
        p: absolute or relative precission depending of positive or negative sign
        r: informative text
    score:     score of this question (positive integer)
    
    Samples:
        cloze_num(3.0)
        cloze_num([1.7,1,-0.01,'Good!'])
        cloze_num([[1.7,1,-0.01,'Good!'],[1.5,0.5,0.01,'Quite good!']])
        
    """
    if (int(score)!= score) or (score<=0):
        raise ValueError('Question score must be a positive integer')

    if isinstance(data, (int,float)): #only one numeric answer
        a = data
        p = 0
        txt = "{"+"{}:NUMERICAL:={}:{}#Answer={}".format(score,a,p,a)+"}"
    elif isinstance(data,(list,tuple)):
        if np.ndim(data) == 1:
            data = [data]
        numanswers = len(data)
        trueanswer = False
        txt = "{"+"{}:NUMERICAL:".format(score)
        for i in range(numanswers):
            answer = data[i]
            lena = len(answer)
            if lena==1: # only solution
                a,w,p,r = {answer,1,0,"Answer={}".format(answer)}
            elif lena==2:
                a,w,p,r = {answer,0,answer[0]}.flatten
            elif lena==3:
                a,w,p,r = {answer,answer[0]}.flatten
            elif lena ==4:
                a,w,p,r = answer[0:lena]
            else:
                raise ValueError('too much items in answer {}'.format(i+1))
            
            if abs(w)>1:
                raise ValueError('weigth of answer {} is out of range'.format(i+1))
            if w == 1:
                trueanswer = True
            if p<0: # relative tolerance
                p = -p*10**(np.log10(np.abs(a)))
            txt+= "~%{}%{}:{}#{}".format(int(w*100),a,p,r)
        if not trueanswer:
            raise ValueError("at least one answer weigth must be one")
        txt += "}" 
    else:
        raise ValueError("invalid type of object")
    return txt

def cloze_mc(data,score=1,kind='MC'):
    """
    Return formatted string for multichoice question
    Sintaxis:
        cloze_mc(data,score=1,kind='MC')
    
    data: list or tuple with sublists {a,w,r}
        a: answer
        w: weigth for this answer (at least one must be one)
        r: informative text
    score:  score of this question (positive integer)
    kind:   type of multichoice
        (see https://docs.moodle.org/XX/en/Embedded_Answers_(Cloze)_question_type )
        where XX is moodle version (39 just now)    
    Samples:
        cloze_mc(['Madrid','Lisboa','Paris','Roma'])
        cloze_mc([['Madrid',1,'Good!'],['Lisboa',-0.5,'Wrong'],['Paris',-0.5,'Wrong']])
        
    """
    if (int(score)!= score) or (score<=0):
        raise ValueError('Question score must be a positive integer')

    kind = kind.upper()
    if kind in {'MC','MCH','MCV','MCS','MCHS','MCVS'}:
        if isinstance(data,(list,tuple)):
            numanswers = len(data)
            if numanswers<2:
                raise ValueError('Multichoice question with only one choice')
            code = "{"+"{}:{}:".format(score,kind)
            if np.ndim(data) == 1:
                trueanswer = True
                code+= "~%{}%{}#{}".format(100,data[0],data[0])
                w = -100/(numanswers-1)
                for i in range(1,numanswers):
                    code+= "~%{}%{}#{}".format(w,data[i],data[i])
            else:
            # if hasattr(data[0],"__iter__"):
                trueanswer = False
                for i in range(numanswers):
                    answer = data[i]
                    lena = len(answer)
                    if lena==1: # only solution
                        a,w,r = {answer,1,answer}
                    elif lena==2:
                        a,w,r = {answer,answer[0]}.flatten
                    elif lena==3:
                        a,w,r = answer
                    else:
                        raise ValueError('too much items in answer {}'.format(i+1))
                    
                    if abs(w)>1:
                        raise ValueError('weigth of answer {} is out of range'.format(i+1))
                    if w == 1:
                        trueanswer = True
                    code+= "~%{}%{}#{}".format(int(w*100),a,r)
                if not trueanswer:
                    raise ValueError("at least one answer weigth must be one")
            code += "}" 
        else:
            raise ValueError("invalid type of object")
    else:
        raise ValueError("invalid kind of multichoice question")
    return code


def cloze_sa(data,score=1,kind='SA'):
    """
    Return formatted string for short answer question
    Sintaxis:
        cloze_sa(data,score=1,kind='SA')
    
    data: list or tuple with sublists {a,w,r}
        a: answer
        w: weigth for this answer (at least one must be one)
        r: informative text
    score:  score of this question (positive integer)
    kind:   type of multichoice
        (see https://docs.moodle.org/XX/en/Embedded_Answers_(Cloze)_question_type )
        where XX is moodle version (39 just now)    
    Samples:
        cloze_sa('Madrid')
        cloze_sa([['Toledo',1,'Good!'],
                  ['Granada',0.75,'Location of Real Chancilleria'],
                  ['Madrid',0,'After Charles the 1st'],
                  ['Burgos',0,'Before Charles the 1st']])
        
    """
    if (int(score)!= score) or (score<=0):
        raise ValueError('Question score must be a positive integer')

    kind = kind.upper()
    if kind in {'SA','MW','SAC','MWC'}:
        code = "{"+"{}:{}:".format(score,kind)
        if isinstance(data,(int,float,str)):
                code += '=' + data + '}'
        elif isinstance(data,(list,tuple)):
            numanswers = len(data)
            if numanswers<2:
                raise ValueError('Multichoice question with only one choice')
            code = "{"+"{}:{}:".format(score,kind)
            if np.ndim(data) == 1:
                trueanswer = True
                code+= "~%{}%{}#{}".format(100,data[0],data[0])
                w = -100/(numanswers-1)
                for i in range(1,numanswers):
                    code+= "~%{}%{}#{}".format(w,data[i],data[i])
            else:
            # if hasattr(data[0],"__iter__"):
                trueanswer = False
                for i in range(numanswers):
                    answer = data[i]
                    lena = len(answer)
                    if lena==1: # only solution
                        a,w,r = {answer,1,answer}
                    elif lena==2:
                        a,w,r = {answer,answer[0]}.flatten
                    elif lena==3:
                        a,w,r = answer
                    else:
                        raise ValueError('too much items in answer {}'.format(i+1))
                    
                    if abs(w)>1:
                        raise ValueError('weigth of answer {} is out of range'.format(i+1))
                    if w == 1:
                        trueanswer = True
                    code+= "~%{}%{}#{}".format(int(w*100),a,r)
                if not trueanswer:
                    raise ValueError("at least one answer weigth must be one")
            code += "}" 
        else:
            raise ValueError("invalid type of object")
    else:
        raise ValueError("invalid kind of multichoice question")
    return code

def lista(data,numbered=True):
    """
    Return formatted string for numbered list
    Sintaxis:
        lista(data,numbered=True)
    
    data: list of str; each str is one separated item. The list would be
        numbered or with marks.
        
    Samples:
        lista_nume({'Madrid','Lisboa','Paris','Roma'})
        lista_nume({'Year of Lepanto battle'+cloze_num({1571}',
                    'Leaer of catholyc army'+cloze_sa('Juan de Austria')})
        
    """
    if numbered:
        code = '<ol>'
        # code = '&lt;ol&gt;'
        for ilist in range(len(data)):
            code += '<li>'+data[ilist]+'</li>'
            # code += '&lt;li&gt;'+data[ilist]+'&lt;/li&gt;'
        code += '</ol>'
        # code += '&lt;/ol&gt;'
    else:
        code = '<ul>'
        # code = '&lt;ul&gt;'
        for ilist in range(len(data)):
            code += '<li>'+data[ilist]+'</li>'
            # code += '&lt;li&gt;'+data[ilist]+'&lt;/li&gt;'
        code += '</ul>'
        # code = '&lt;ul&gt;'
    return code

def tabla(data,leyenda={}):
    """
    Return formatted string for a table
    Sintaxis:
        lista(data,numbered=True)
    
    data: list of str; each str is one separated item. The list would be
        numbered or with marks.
        
    Samples:
        tabla([[1,2,3],[4,5,6]])
        tabla([45,70,1.62],[53,92,1.78]],{'subt':'Candidates',
                'head':['age','weigth','heigth'])
        
    """
    # code = '<table>'
    code = '&lt;table&gt;'
    if isinstance(leyenda, (dict)):
        if 'subt' in leyenda.keys():
            # code+= '<caption style="caption-side: top">'+leyenda['subt']+'</caption>'
            code+= '&lt;caption style="caption-side: top"&gt;'+leyenda['subt']+'&lt;/caption&gt;'
        elif 'head' in leyenda.keys():
            if hasattr(leyenda,'__iter__'):
                code+='<thead><tr>'
                # code+='&lt;thead&gt;&lt;tr&gt;'
                for tmp in leyenda:
                    code+= '<th scope"col">'+tmp+'</th>'
                    # code+= '&lt;th scope"col"&gt;'+tmp+'&lt;/th&gt;'
                code+='</tr></thead>'
                # code+='&lt;/tr&gt;&lt;/thead&gt;'
    if isinstance(data,(list,tuple,np.ndarray)):
        code+='<tbody>'
        # code+='&lt;tbody&gt;'
        for fila in data:
            if isinstance(fila,(list,tuple,np.ndarray)):
                code+='<tr>'
                # code+='&lt;tr&gt;'
                for colu in fila:
                    code+='<td>'+'{}'.format(colu)+'</td>'
                    # code+='&lt;td&gt;'+'{}'.format(colu)+'&lt;/td&gt;'
                code+='</tr>'
                # code+='&lt;/tr&gt;'
        code+='</tbody>'
        # code+='&lt;/tbody&gt;'
    code+='</table>'
    # code+='&lt;/table&gt;'
    return code

def imagen(imgfile,sopt={}):
    """
    Return formatted string for a image
    Sintaxis:
        imagen(imgfile,soptions={})
    
    imgfile: file with image.
    sopt: dictionary with image options
        width, height, class, role, style, alt
        
    Samples:
        imagen('Img/figura.png,{'width':"800",'height'="498",'class'="img-responsive"\
               'role'="presentation",'style'="vertical-align:text-bottom; margin: 0 .5em;" alt="Explanation")
        
    """
    code = '<img '
    # code = '&lt;img '
    if isinstance(sopt, (dict)):
        for llave, valor in sopt.items():
            if llave in ('width', 'height', 'class', 'role', 'style', 'alt'):
                code += '{}="{}" '.format(llave,valor)
            else:
                print('key {} is not valid, ignoring...')

        code+= 'src="{}"'.format(imgfile)
    else:
       raise ValueError('"sopt" must be a dictionary')
    code+= '>'
    # code+= '&gt;'
    return code

def tmpfiles_rm(file='',sopt={}):
    """
    delete temporary preview files
    Sintaxis:
        delete(htmlfile,soptions={})
    
    htmlfile: temporary file use with openwrobser to preview
    sopt: dictionary with image options
        width, height, class, role, style, alt
        
    Samples:
        delete('Img/figura.html')
        
    """
    if file=='':
        secons = T.time_ns()
        tmpfilename = './_tmp-mo{}.html'.format(int(secons))
        tmpfilename = tmpfilename[:12]+'*.html'
        rmfiles = glob.iglob(tmpfilename)
    else:
        rmfiles = [file].flatten
    try:
        for file in rmfiles:
            os.remove(file)
    except (OSError,EOFError) as err:
        print("OS error {} removing file {}".format(err,file))
        raise
    except:
        print("Unexpected error{} removing file {}".format(sys.exc_info()[0],file))
        raise
    return None  