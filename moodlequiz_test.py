from utiles import clear_workspace
clear_workspace()
import utiles as UT
import moodlequiz as MO
import sympy as S
import numpy as N
S.init_printing()

import xml.etree.ElementTree as ET

#
# -----> pruebas con cloze numericas
# 
tnum0 = MO.cloze_num(1571)
tnum1 = MO.cloze_num([1.7,1,-0.01,'Good!'])
tnum2 = MO.cloze_num([[1.7,1,-0.01,'Good!'],[1.5,0.5,0.01,'Quite good!']])
#
# -----> pruebas con cloze multichoice
# 
tmch0 = MO.cloze_mc(['Madrid','Lisboa','Paris','Roma'])
tmch1 = MO.cloze_mc([['Spanish',1,'Good!'],['French',-0.5,'Wrong'],['German',-0.5,'Wrong']])
#
# -----> pruebas con cloze short answer
# 
tsha0 = MO.cloze_sa('Juan de Austria')
tsha1 = MO.cloze_sa('Madrid',10,'SAC')
tsha2 = MO.cloze_sa([['Toledo',1,'Good!'],['Granada',0.75,'Location of Real Chancilleria'],['Madrid',0,'After Charles the 1st'],['Burgos',0,'Before Charles the 1st']])
#
# -----> pruebas con imagen
# 
timg0 = MO.imagen('img/pepito.img',{'style':"vertical-align:text-bottom; margin: 0 .5em;",'alt':"Explanation"})
#
# -----> pruebas con listas
# 
tlis0 = MO.lista(['Year of Lepanto battle:'+tnum0,'Leader of catholyc army:'+tsha0,'Leader nationality'+tmch1])
#
# -----> pruebas con tablas
# 
ttab0 = MO.tabla([[45,70,1.62],[53,92,1.78]],
                 {'subt':'Candidates','head':['age','weigth','heigth']})

xmlfilename = './_wholequiz.xml'
#
# Verificación del tipo ensayo, vista previa y creacion del fichero xml
#
# essay0 = MO.essay('ensayo01','Some questions about famous battles'+tlis0)
# # essay0xml = essay0.xml()
# # essay0txt = ET.tostring(essay0xml)
# # essay0htm = essay0.html()
# # essay0txt = ET.tostring(essay0htm)
# tmp = essay0.preview()
# # tmp = essay0.preview(nsec=10)
# essay0.write(xmlfilename,order='first')
#
# Verificación del tipo cloze , vista previa y creacion del fichero xml
#
# cloze0 = MO.cloze('cloze01','Some questions about famous battles'+tlis0)
# # cloze0xml = cloze0.xml()
# # cloze0txt = ET.tostring(cloze0xml)
# # cloze0htm = cloze0.html()
# # cloze0txt = ET.tostring(cloze0htm)
# tmp = cloze0.preview()
# cloze0.write(xmlfilename)
#
# Verificación del tipo matching , vista previa y creacion del fichero xml
#
# couples = [['Waterloo',1815],['Lepanto',1571],['Trafalgar',1805],['Gettysburg',1863]]
# match0 = MO.matching('match01','What year did the following battles take place in?',**{'couples':couples})
# # match0xml = match0.xml()
# # match0txt = ET.tostring(match0xml)
# # match0htm = match0.html()
# # match0txt = ET.tostring(match0htm)
# tmp = match0.preview()
# match0.write(xmlfilename)
#
# Verificación del tipo multichoice , vista previa y creacion del fichero xml
#
triplets = [[-33.333,'Waterloo',1815],[100,'Lepanto',1571],[-33.333,'Trafalgar',1805],[-33.333,'Gettysburg',1863]]
mucho0 = MO.multichoice('mucho0','What famous battle take place in XVII century?',**{'triplets':triplets})
# mucho0xml = mucho0.xml()
# mucho0txt = ET.tostring(mucho0xml)
# mucho0htm = mucho0.html()
# mucho0txt = ET.tostring(mucho0htm)
tmp = mucho0.preview()
mucho0.write(xmlfilename,order='first')

triplets = [[33.333,'Waterloo',1815],[33.333,'Lepanto',1571],[33.333,'Trafalgar',1805],[-50,'Gettysburg',1863]]
mucho1 = MO.multichoice('mucho0','What famous battles take place in Europe?',**{'triplets':triplets,'sngl':False})
# mucho1xml = mucho1.xml()
# mucho1txt = ET.tostring(mucho1xml)
# mucho1htm = mucho1.html()
# mucho1txt = ET.tostring(mucho1htm)
tmp = mucho1.preview()
mucho1.write(xmlfilename,order='last')


# MO.tmpfiles_rm()