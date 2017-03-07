__author__ = 'Matthew Stubenberg'
__copyright__ = "Copyright 2017, Maryland Volunteer Lawyers Service"
import csv
from datetime import datetime


class Expungealator:

    chargearray = []
    dispolist = {}
    gooddispos = ['NP','NG','ACQUITTAL','JUVENILE','DISMISSED']
    case_expungeability_regular = 'UNKNOWN'

    def __init__(self):
        #Populate dispolist with dispositions CSV File to useable dictionary
        #Not sure if it would be faster to search for each disposition each time.
        reader = csv.DictReader(open('csv files/DispositionsList.csv'))
        for line in reader:
            self.dispolist[line['Raw']] =  line['Converted']
    def addCharge(self,description,disposition,dispodate):
        #Add charge to chargearray

        #Convert Disposition into a Recognized One
        disposition = disposition.upper()
        description = description.upper()
        tempdispo = self.convertDisposition(disposition) #Convert Disposition
        if(tempdispo == False or disposition == None or disposition == ''):
            tempdispo = 'UNKNOWN'

        #Convert Date to date object
        tempdate = self.try_parsing_date(dispodate)
        if(tempdate == False):
            #No Date Found
            tempdate = None

        #Add charge to Charge array
        tempcharge = {"Description":description,"Disposition":tempdispo,"DispositionDate":tempdate}
        self.chargearray.append(tempcharge)

    def convertDisposition(self,disposition):
        #Search the disposition dictionary for the disposition it blongs to.
        if disposition in self.dispolist:
            return self.dispolist[disposition]
        else:
            return False
    def checkExpungementRegular(self):
        #For checking normal expungement
        x=0
        #Run through each charge and check it
        for charge in self.chargearray:
            return_charge = self.checkERCharge(charge)
            self.chargearray[x] = return_charge #should overwrite the old value with the new charge var
            x=x+1

        #Add all charge expungeability results to an array
        temp_er_array = []
        for charge in self.chargearray:
            temp_er_array.append(charge['ExpungementRegular'])

        #Search that array to find dooming results
        if('NOT EXPUNGEABLE' in temp_er_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE"
        elif('UNKNOWN' in temp_er_array):
            self.case_expungeability_regular = "UNKNOWN"
        elif ('NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE' in temp_er_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE"
        elif ('NOT EXPUNGEABLE YET' in temp_er_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE YET"
        elif ('MAYBE EXPUNGEABLE' in temp_er_array):
            self.case_expungeability_regular = "MAYBE EXPUNGEABLE"
        elif ('EXPUNGEABLE' in temp_er_array):
            self.case_expungeability_regular = "EXPUNGEABLE"
        else:
            self.case_expungeability_regular = "UNKNOWN" #Catch all
        return self.case_expungeability_regular
    def checkERCharge(self,charge):
        #Set up Variables
        er = "NOT CHECKED"
        excode = 0

        #Check if Disposition Date is NONE
        if charge['DispositionDate'] == None:
            charge['ExpungementRegular'] = "UNKNOWN"
            charge['LiabilityWaiver'] = False
            charge['ExpungementRegularCode'] = 112
            return charge

        #Liability Waiver
        if self.days_between(charge['DispositionDate']) < 1095:
            libwaive = True
        else:
            libwaive = False

        # NP-NG-Acquittal
        if charge['Disposition'] in self.gooddispos:
            er = "EXPUNGEABLE"
            excode = 100
        #PBJ
        elif charge['Disposition'] == 'PBJ':
            #Check for DUI/DWI
            if self.itemInCSV('dui',charge['Description']) == True:
                er = "NOT EXPUNGEABLE"
                excode = 101
            elif self.itemInCSV('marijuana_less_than',charge['Description']) == True:
                er = "EXPUNGEABLE"
                excode = 113
            elif self.itemInCSV('marijuana_regular',charge['Description']) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 114
            elif self.itemInCSV('cds_generic',charge['Description']) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 115
            elif self.days_between(charge['DispositionDate']) < 1095:
                er = "NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE"
                excode = 102
            else:
                er = "MAYBE EXPUNGEABLE"
                excode = 103
        #STET
        elif charge['Disposition'] == 'STET':
            if self.days_between(charge['DispositionDate']) < 1095:
                er = "NOT EXPUNGEABLE YET"
                excode = 104
            else:
                er = "EXPUNGEABLE"
                excode = 105
        #GUILTY
        elif charge['Disposition'] == 'GUILTY':
            #Check Nuisance Crime
            if self.determineNuisance(charge['Description']) == True:
                if self.days_between(charge['DispositionDate']) < 1095:
                    er = "NOT EXPUNGEABLE YET"
                    excode = 106
                else:
                    er = "EXPUNGEABLE"
                    excode = 107
            # Check Marijuana < 10
            elif self.itemInCSV('marijuana_less_than',charge['Description']) == True:
                er = "EXPUNGEABLE"
                excode = 108
            #Check Marijuana Reg
            elif self.itemInCSV('marijuana_regular',charge['Description']) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 109
            #Check CDS Possession Generic (maybe marijuana)
            elif self.itemInCSV('cds_generic', charge['Description']) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 110
            #Regular Guilty
            else:
                er = "NOT EXPUNGEABLE"
                excode = 111
        #Unknown Disposition
        else:
            er = 'UNKNOWN'
            excode = 112

        #Return the results which will be added to the charge in the chargearray
        charge['ExpungementRegular'] = er
        charge['LiabilityWaiver'] = libwaive
        charge['ExpungementRegularCode'] = excode
        return charge
    def getChargeInfo(self,chargenum,item):
        return self.chargearray[chargenum]
    def getAllCharges(self):
        return self.chargearray
    def days_between(self,d1):
        #Primarily used for determining if 3 years have passed
        d2 = datetime.now().date()
        return abs((d2 - d1).days)
    def try_parsing_date(self,text):
        #Converting dates to propert YYYY-MM-DD format
        if text == None:
            return False
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y','%m/%d/%Y'):
            try:
              return datetime.strptime(text, fmt).date()
            except ValueError:
                pass
        return False #Means we couldn't convert the date
    def itemInCSV(self,csvname,item):
        #Check a single column csv for an item
        reader = csv.DictReader(open('csv files/' + csvname + '.csv'))
        for line in reader:
            if(item.upper() == line['Description'].upper()):
                return True
        return False #Item was not in array
    def determineNuisance(self,description):
        #There are too many possible descrpitions so this is the best way for now.
        #Urination in public
        if "URINA" in description.upper():
            return True
        #Panhandling
        elif "PANH" in description.upper():
            return True
        #Drinking Alcohol in Public
        elif "ALC" in description.upper() and "PUB" in description.upper():
            return True
        #Obstruction Free Pass
        elif "FREE" in description.upper() and "OBSTR" in description.upper():
            return True
        #Sleeping in Park
        elif "SLEEP" in description.upper():
            return True
        #Loitering
        elif "LOITER" in description.upper():
            return True
        #Vagrancy
        elif "Vagran" in description.upper():
            return True
        #Proof of Payment
        elif "fail" in description.upper() and "fare" in description.upper():
            return True
        else:
            return False
