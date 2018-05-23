__author__ = 'Matthew Stubenberg'
__copyright__ = "Copyright 2017, Maryland Volunteer Lawyers Service"
import csv
from datetime import datetime
from Charge import Charge

class Expungealator:

    chargearray = None
    dispolist = {}
    gooddispos = ['NP','NG','ACQUITTAL','JUVENILE','DISMISSED']
    case_expungeability_regular = 'UNKNOWN'

    def __init__(self):
        #Populate dispolist with dispositions CSV File to useable dictionary
        #Not sure if it would be faster to search for each disposition each time.
        reader = csv.DictReader(open('csv files/DispositionsList.csv'))
        for line in reader:
            self.dispolist[line['Raw']] =  line['Converted']

    def setChargeArray(self,chargearray):
        self.chargearray = chargearray

    def checkCaseExpungeability(self):
        #Check charge specific eligability and save the expungeability status in the temp expungement array.
        #We then check this array to see if there are any unit rule violations.

        temp_expungement_array = []
        for charge in self.chargearray:
            charge.setExpungementEligability(self.checkChargeExpungeability(charge))
            temp_expungement_array.append(charge.expungement_status)

        #Search that array to find dooming results
        if('NOT EXPUNGEABLE' in temp_expungement_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE"
        elif('UNKNOWN' in temp_expungement_array):
            self.case_expungeability_regular = "UNKNOWN"
        elif ('NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE' in temp_expungement_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE"
        elif ('NOT EXPUNGEABLE YET' in temp_expungement_array):
            self.case_expungeability_regular = "NOT EXPUNGEABLE YET"
        elif ('MAYBE EXPUNGEABLE' in temp_expungement_array):
            self.case_expungeability_regular = "MAYBE EXPUNGEABLE"
        elif ('EXPUNGEABLE' in temp_expungement_array):
            self.case_expungeability_regular = "EXPUNGEABLE"
        else:
            self.case_expungeability_regular = "UNKNOWN" #Catch all
        return self.case_expungeability_regular

    def checkChargeExpungeability(self,charge):
        #Set up Variables
        er = "NOT CHECKED"
        excode = 999
        expungement_values = {} #This is what's returned
        '''
        print(charge.disposition_date)
        print(charge.description)
        print(charge.cjis)
        print(charge.disposition)
        '''
        #Check if Disposition Date is NONE
        if charge.disposition_date == None:
            expungement_values['Expungement_Status'] = "UNKNOWN"
            expungement_values['Liability_Waiver'] = False
            expungement_values['Expungement_Status_Code'] = 112
            return expungement_values

        #Liability Waiver
        if self.days_between(charge.disposition_date) < 1095:
            libwaive = True
        else:
            libwaive = False

        # NP-NG-Acquittal
        if charge.disposition in self.gooddispos:
            er = "EXPUNGEABLE"
            excode = 100
        #PBJ
        elif charge.disposition == 'PBJ':
            #Check for DUI/DWI
            if self.itemInCSV('dui',charge.description) == True:
                er = "NOT EXPUNGEABLE"
                excode = 101
            elif self.itemInCSV('marijuana_less_than',charge.description) == True:
                er = "EXPUNGEABLE"
                excode = 113
            elif self.itemInCSV('marijuana_regular',charge.description) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 114
            elif self.itemInCSV('cds_generic',charge.description) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 115
            elif self.days_between(charge.disposition_date) < 1095:
                er = "NOT EXPUNGEABLE YET/MAYBE EXPUNGEABLE"
                excode = 102
            else:
                er = "MAYBE EXPUNGEABLE"
                excode = 103
        #STET
        elif charge.disposition == 'STET':
            if self.days_between(charge.disposition_date) < 1095:
                er = "NOT EXPUNGEABLE YET"
                excode = 104
            else:
                er = "EXPUNGEABLE"
                excode = 105
        #GUILTY
        elif charge.disposition == 'GUILTY':
            #Check Nuisance Crime
            if self.determineNuisance(charge.description) == True:
                if self.days_between(charge.disposition_date) < 1095:
                    er = "NOT EXPUNGEABLE YET"
                    excode = 106
                else:
                    er = "EXPUNGEABLE"
                    excode = 107
            # Check Marijuana < 10
            elif self.itemInCSV('marijuana_less_than',charge.description) == True:
                er = "EXPUNGEABLE"
                excode = 108
            #Check Marijuana Reg
            elif self.itemInCSV('marijuana_regular',charge.description) == True and self.days_between(charge.disposition_date) < 1460:
                er = "NOT EXPUNGEABLE YET"
                excode = 109
            elif self.itemInCSV('marijuana_regular',charge.description) == True and self.days_between(charge.disposition_date) >= 1460:
                er = "EXPUNGEABLE"
                excode = 113
            #Check CDS Possession Generic (maybe marijuana)
            elif self.itemInCSV('cds_generic', charge.description) == True:
                er = "MAYBE EXPUNGEABLE"
                excode = 110
            #JRA 10 Years
            elif charge.cjis != None and self.itemInCSV('jra_10',charge.cjis, "CJIS"):
                #FOUND JRA CJIS Code
                if self.days_between(charge.disposition_date) > 3650:
                    #More than 10 years
                    er = "MAYBE EXPUNGEABLE"
                    excode = 114
                else:
                    #Less than 10 years
                    er = "NOT EXPUNGEABLE YET"
                    excode = 115
            #JRA 15 Years
            elif self.itemInCSV('jra_15',charge.cjis,"CJIS"):
                #FOUND JRA CJIS Code
                if self.days_between(charge.disposition_date) > 5475:
                    #More than 15 years
                    er = "MAYBE EXPUNGEABLE"
                    excode = 116
                else:
                    #Less than 15 years
                    er = "NOT EXPUNGEABLE YET"
                    excode = 117
            #Regular Guilty
            else:
                er = "NOT EXPUNGEABLE"
                excode = 111
        #Unknown Disposition
        else:
            er = 'UNKNOWN'
            excode = 112

        #Return the results which will be added to the charge in the chargearray
        expungement_values['Expungement_Status'] = er
        expungement_values['Liability_Waiver'] = libwaive
        expungement_values['Expungement_Status_Code'] = excode
        return expungement_values

    def getAllCharges(self):
        return self.chargearray
    def days_between(self,d1):
        #Primarily used for determining if 3 years have passed
        d2 = datetime.now().date()
        return abs((d2 - d1).days)

    def itemInCSV(self,csvname,item,column = 'Description'):
        #Check a single column csv for an item
        reader = csv.DictReader(open('csv files/' + csvname + '.csv'))
        for line in reader:
            if(item.upper() == line[column].upper()):
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
