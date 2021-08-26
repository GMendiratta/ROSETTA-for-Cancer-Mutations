import os
import numpy as np
import pandas as pd
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@version: 0 
@date: Apr 15 2019
@author: MerajAziz

@version: 1
@date: Aug 8 2019
@author: GauravMendiratta 

@version: 2
@date: Mar 3 2020
@author: GauravMendiratta
@updates: Pre-processing other locations and histologies.

@version: 3
@date: Mar 30 2020
@author: GauravMendiratta
@updates: Complete Rewrite of Code. Simplified pre-processing and new histology reassignment method.
"""

#print("This pre-processing component of the file file extracts and orgnises correct mutational count data from input.txt and input.dic files generated by SEERStat. Please run it in the same folder as the input txt and dic files.")

with open("input.txt","r") as txtfile:
    datatxt0=txtfile.read() #import SEER data
    txtfile.close()

datatxt=datatxt0.split("\n")
datatxt1=[row.split("\t") for row in datatxt]
datatxt=datatxt1 # Convert SEER data to a list

# define some functions useful in data manipulation and formatting
def padding(l1):
    """This function inputs a 2D list adds empty elements to rows to convert a list of lists into a rectangular matrix."""
    lengthvec=[len(row) for row in l1]
    maxlen=max(lengthvec)
    padlist=[['' for i in range(maxlen-n)] for n in lengthvec]
    return padlist
def transpose(l1):
    """This function inputs a 2D list which may not be rectangular, adds empty element padding as needed and then returns the transpose."""
    pads=padding(l1)
    l2=[l1[i]+ pads[i] for i in range(len(l1))]
    l3=[[row[i] for row in l2] for i in range(len(l2[0]))]
    return l3
transdat=transpose(datatxt)
if '' in transdat[0]:
    transdat[0].remove('')
with open('input.dic',"r") as dicfile: 
    datadic=dicfile.read() # Import SEER dictionary of histologies corresponding to the data in input.txt
    dicfile.close()

colname="[Format="+datatxt[0][0].replace('"',"")+"]"# The list of columns in dictionary file begin with this keyword
print('Matching Histologies in '+colname+' from input.dic file')
loccol=datadic.find(colname)+len(colname) # location of the colname keyword
loccol2=datadic.find("[",loccol) # This is normally -1 unless additional data was inputed beyond the histologies.
col0data=datadic[loccol+1:].split("\n") # list of relevant lines in the dictionary file
HISTcodedata=['CODE']+[int(elem[elem.find("=")+1:elem.find(":_") if elem.find(":_")>-1 else None]) for elem in col0data[:-2]] # Extract histological codes from each line
HISTnamedata=[(elem[elem.find(":_")+2:] if elem.find(":_")>-1 else 'unknown') for elem in col0data[:-2]] # extract histology name from each line
HISTnamedata=["HISTO NAME"]+HISTnamedata # title of the column in HISTO NAME
# replace first column of the transposed data table with the column with mutation types (from input.dic file)
if (len(transdat[0])-len(HISTnamedata)) == 0:
    transdat[0]=HISTnamedata
    transdat=[HISTcodedata]+transdat
else: print('error in processing dic file.')

# extract rows containing 'count' information
datacounts=[transdat[0],transdat[1]]+[row for row in transdat if row[0].find('Count')>-1] # Extract 'Count' as opposed to rate or population 

# import the Input_Revised locations assigned for the “Incidence- SEER 18 Regs Research Data+ Hurricane Katrina impacted cases, Nov 2017” data set
with open("Input_Revised_locations.txt","r") as locfile:
    revhistnames=locfile.read().split("\t")
    locfile.close()

datacounts2=transpose([revhistnames]+transpose(datacounts))
datacounts2[0][0]='HISTO CODE'
df_SEER=pd.DataFrame(datacounts2[1:],columns=datacounts2[0])
df_SEER=df_SEER.set_index(['HISTO CODE','CODE'])
malignant_cols=[item for item in df_SEER.columns if isinstance(item,int) and ((item-3)%10 == 0)]
df_SEER=df_SEER[malignant_cols]
df_SEER.to_excel('SEER1_raw.xlsx',index=True)

df_SEERedit=pd.DataFrame.copy(df_SEER.drop(index=['CUSTOM SITES'],level=0))
df_SEERedit=df_SEERedit.apply(pd.to_numeric,errors='coerce')
df_SEERedit=df_SEERedit.drop(index=[''],level=0) # This step removes a number of redundant rows in locations. This is by definition a manual task and is defined by the elements left empty in 'Input_Revised_locations.txt'
df_SEERedit.to_excel('SEER2_CleanedLocations.xlsx',index=True)

# PREPROCESS: Smear misc locations
miscvals0=pd.DataFrame.copy(df_SEERedit.loc['Other & Unspecified','"Miscellaneous_Count"']) # values in other and unspecified misc counts
df_SEERnoMisc=pd.DataFrame.copy(df_SEERedit.drop(index=['Other & Unspecified','"Miscellaneous_Count"'],level=1)) # remove the misc column from the SEER matrix
locsums=df_SEERnoMisc.sum() # add over locations excluding misc
coltrue=[it1 for it1 in miscvals0.index if ((miscvals0[it1]>0.) and ((miscvals0[it1]/2)<locsums[it1]))] # columns for which the other misc counts are less than twice the sum of rest of the counts.
miscvals=df_SEERedit[coltrue].loc['Other & Unspecified','"Miscellaneous_Count"']
print([len(miscvals0),len(miscvals),(miscvals0>0.).sum()])
df_SEERnoMisc=df_SEERnoMisc[coltrue] 
df_SEERnoMiscwts=(df_SEERnoMisc/df_SEERnoMisc.sum(axis='rows')).fillna(1./len(df_SEERnoMisc.index)) # create weight matrix by dividing with the total for all locations for each histology
df_SEERnoMiscwtd=df_SEERnoMiscwts.mul(miscvals) # multiply the weight matrix with location 'other' totals to obtain the weighted sample correction for each location and histology combination correction

df_SEERpreprocrows=df_SEERnoMisc+df_SEERnoMiscwtd # Add the location-reweighted SEER matrix
# copy the updated data table into the original SEER matrix.
dfpprows=pd.DataFrame.copy(df_SEERedit)
for items in coltrue:
    miscvals0[items]=0. # update the reassigned elements of the miscellaneous counts vector to 0.
    for rows in df_SEERpreprocrows.index:
        dfpprows.loc[rows,items]=df_SEERpreprocrows.loc[rows,items]
dfpprows.loc['Other & Unspecified','"Miscellaneous_Count"']=miscvals0 # reset the misc count so that re-smeared elements are removed.
# Sum over rows to recode to simplified location definitions
dfpprows=dfpprows.reset_index().groupby('HISTO CODE',sort=False).sum()
dfpprows.to_excel('SEER3_SmearedLocations.xlsx',index=True)
#### LHS is the total columns, RHS counts 1 for histologies which match pre and post location smearing. The two should be equal.
if len(dfpprows.columns)==((df_SEERedit.sum().round().astype('int'))==(dfpprows.apply(pd.to_numeric,errors='coerce').sum().round().astype('int'))).sum(): print('Location Smearing Successful.')

# PREPROCESS: Smear generic Histologies
# Smear All codes below 80053 and output dropped listx
dfpprows.columns=dfpprows.columns.astype('int')
gencodes=dfpprows.columns[dfpprows.columns<=80053] # smear all histologies below 80053.These include malignant histologies- Neoplasm malignant, Tumor cells malignant and Malignant tumor small, giant,spindle, clear cell types.
dfSgen=pd.DataFrame.copy(dfpprows[gencodes.values])# generic codes isolated by Ed for re-smearing
dfSgenVec=dfSgen.sum(axis=1)
dfSsp=pd.DataFrame.copy(dfpprows)
dfSsp[dfSgen.columns]=0.# Remove the  generic code columns.

dfSwts=(dfSsp.div(dfSsp.sum(axis='columns'),axis='rows')).fillna(1./len(dfSsp.columns)) # SEER results matching genomic data weighted by total in each row (location)
dfSspwtd=dfSwts.mul(dfSgenVec,axis='rows') # multiply weights by the summed generic vector to get weighted cases to add by location.
dfStot=dfSsp+dfSspwtd
# The right hand number counts 1 for all values of total in SEER unprocessed which matches the value (rounded, converted to integer) of SEER pre processed with rows.
if len(dfpprows.index)==((dfpprows.sum(axis='columns').round().astype('int'))==(dfStot.sum(axis='columns').round().astype('int'))).sum(): print('Histology Smearing Successful')
# copy the updated data table into the original SEER matrix.
dfpp=pd.DataFrame.copy(dfpprows)
for items in dfStot.columns:
    for rows in dfStot.index:
        dfpp.loc[rows,items]=dfStot.loc[rows,items]
print('Total before and after smearing:',dfpp.sum().sum(),df_SEERedit.sum().sum(),'\n')
dfpp.to_excel('SEER4_SmearedLocAndHist.xlsx',index=True)

### Curated Histological RECODING:
# input recode map as a dataframe
with open('Input_SEER_Histology_Recode_Map.txt',"r") as mapfile: 
    mapdat=mapfile.read() # Import SEER dictionary of histologies corresponding to the data in input.txt
    mapfile.close()
maplist=[elem.split('\t') for elem in mapdat.split(sep='\n')]# Convert the mapping rules to a list
df_Recode=pd.DataFrame(maplist[1:],columns=maplist[0])# convert mapping rules to a dataframe
df_SEERpp1=pd.DataFrame.copy(dfpp) # Copy seer dataframe
# Process ranges of codes, recodes and locations:
newRecodeslist=[int(elem) for elem in df_Recode['Recode'] if (elem not in df_SEERpp1.columns.map(str))&(elem.find('-')<0)] # list new recodes
for col in newRecodeslist:
    df_SEERpp1[col]=0.0 # Create new recodes and set to 0

for iter1 in df_Recode.index: # scan over recode rules sequentially
    iterRecode=df_Recode['Recode'].loc[iter1] # recodes to which the codes are assigned
    if iterRecode.find('-')>0: # convert a range of recodes into a python list
        itcodelist=list(map(int,iterRecode.split('-')))
        iterRecode=df_SEERpp1.columns[(df_SEERpp1.columns>=itcodelist[0])&(df_SEERpp1.columns<=itcodelist[1])].values.tolist()
    else:
        iterRecode=list(map(int,iterRecode.split(','))) # convert a comma separated list of recodes or even a single recode into a python list
    df_Recode['Recode'].loc[iter1]=iterRecode

# Process Codes to convert all ranges into lists dropping all elements coming after a semi-colon
l1=[]
for elem in df_Recode['Codes']:
    if elem.find('-')<0:
        l1=l1+[list(map(int,elem.split(',')))]
    elif elem.find(';')<0:
        rangevals=elem.split('-')
        l1=l1+[df_SEERpp1.columns[(int(rangevals[0])<=df_SEERpp1.columns.map(int))&(df_SEERpp1.columns.map(int)<=int(rangevals[1]))].values.tolist()]
    elif elem.find(';')>0:
        lists2=elem.split(';')
        rangevals=lists2[0].split('-')
        rangevalsrem=list(map(int,lists2[1].split(',')))
        l01=df_SEERpp1.columns[(int(rangevals[0])<=df_SEERpp1.columns.map(int))&(df_SEERpp1.columns.map(int)<=int(rangevals[1]))].values.tolist()
        l1=l1+[[int(elem) for elem in l01 if not(int(elem) in rangevalsrem)]]
    else:
        print('ERROR- unrecognized code: ',elem)
        l1=l1+[elem]
df_Recode['Codes']=l1 # assign the converted list of recodes to recode dataframe.

def Recode_locfn(sumloc):
    """This function generates a list of locations corresponding to the index value of the recode dataframe."""
    if sumloc != 'All':
        return sumloc.split(',')
    else:
        return df_SEERpp1.index.values.tolist()

df_Recode.to_csv('Output_SEER_Histology_Recode_Map.txt',sep='\t') # Output recoding list to cross-check for potential errors.

# IMPLEMENT HISTOLOGICAL RECODES: 
for iter1 in df_Recode.index: # scan over recode rules sequentially
    iterRecode=df_Recode['Recode'].loc[iter1] # recodes to which the codes are assigned
    sumcodes=df_Recode['Codes'].loc[iter1] # The list of codes to be summed over
    sumloc=df_Recode['Location'].loc[iter1] # Locations to sum over
    if (sumloc.lower() == 'all') & (len(iterRecode)==1): # The simplest case to implement
        df_SEERpp1[iterRecode[0]]=df_SEERpp1[sumcodes].sum(axis='columns') # Recode sum over codes
        for icode in sumcodes:
            df_SEERpp1[icode]=0.0 # set the smeared locations and histologies to zero
    else:#Perform Smearing over a list of Recodes, even if it is a single recode
        sumloc=Recode_locfn(sumloc)
        dfSmearCodes=df_SEERpp1[sumcodes].loc[sumloc].sum(axis='columns') # sum over all the codes to be smeared
        dfSp=pd.DataFrame.copy(df_SEERpp1[iterRecode].loc[sumloc]) 
        dfSwts=(dfSp.div(dfSp.sum(axis='columns'),axis='rows')) # SEER results matching smearomic data weighted by total in each row (location)
        dfSwts=dfSwts.fillna(1./len(dfSwts.columns)) # This handles the cases where smearing is needed and all histologies are zero for a given location. Note that we did not do this for the preprocessed smearing. There, if we have a zero vector
        dfSpwtd=dfSwts.mul(dfSmearCodes,axis='rows') # multiply weights by the summed smeareric vector to get weighted cases to add by location.
#         dfStot=dfSp+dfSpwtd
        for iRecode in iterRecode:
            if len(sumloc) == 1:
                df_SEERpp1[iRecode].loc[sumloc]=(df_SEERpp1[iRecode].loc[sumloc]).add(dfSpwtd[iRecode])
            else:
                df_SEERpp1[iRecode].loc[sumloc]=df_SEERpp1[iRecode].loc[sumloc]+dfSpwtd[iRecode].loc[sumloc]
        for icode in sumcodes:
            df_SEERpp1[icode].loc[sumloc]=0.0 # set the smeared locations and histologies to zero
print('Sum over recoded histologies:',sum([df_SEERpp1[df_Recode['Codes'].loc[it1]].loc[Recode_locfn(df_Recode['Location'].loc[it1])].sum().sum() for it1 in df_Recode.index]))
print('Total over all locations and histologies is equal before and after recoding: ',round(df_SEERpp1.sum().sum())==dfpp.sum().sum())


# Prepare final output:
# This is just a documentation row added to the matrix to make viewing in excel easier.
dfrowCUSTOMSITES=df_SEER.loc['CUSTOM SITES']
dfrowCUSTOMSITES.index=['CUSTOM SITES']
dfrowCUSTOMSITES.columns=dfrowCUSTOMSITES.columns.map(int)
for iter1 in df_Recode.index:
    if df_Recode['Recode'].loc[iter1][0] in newRecodeslist:
        dfrowCUSTOMSITES[int(df_Recode['Recode'].loc[iter1][0])]=df_Recode['Recode_Name'].loc[iter1]
df_SEERpp1.columns.values in dfrowCUSTOMSITES.columns.values #Check that all the histologies are covered in the Custom SItes row
df_SEER_Output=pd.concat([dfrowCUSTOMSITES,df_SEERpp1])
df_SEER_Output.index.name='HISTO CODE'
outfilename='Output_SEER.txt'
df_SEER_Output.to_csv(outfilename,sep='\t',index=True,header=True) # Output processed file.