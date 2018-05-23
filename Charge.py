__author__ = 'Matthew Stubenberg'
__copyright__ = "Copyright 2017, Maryland Volunteer Lawyers Service"
import csv
from datetime import datetime

class Charge:
    disposition = None
    description = None
    disposition_date = None
    cjis = None
    statute = None

    expungement_status = None
    liability_waiver = None
    expungement_status_code = None

    dispolist = {}

    def __init__(self):
        #Populate dispolist with dispositions CSV File to useable dictionary
        #Not sure if it would be faster to search for each disposition each time.
        reader = csv.DictReader(open('csv files/DispositionsList.csv'))
        for line in reader:
            self.dispolist[line['Raw']] =  line['Converted']

    def setDisposition(self,disposition):
        #Convert Disposition into a Recognized One
        disposition = disposition.upper()
        self.disposition = self.convertDisposition(disposition) #Convert Disposition

    def convertDisposition(self,disposition):
        #Search the disposition dictionary for the disposition it blongs to.
        if disposition in self.dispolist:
            return self.dispolist[disposition]
        else:
            return "UNKNOWN"

    def setDescription(self,description):
        self.description = description.upper()

    def setCJIS(self,cjis):
        self.cjis = cjis

    def setStatute(self,statute):
        self.statute = statute

    def setDispositionDate(self,dispodate):
       self.disposition_date = self.try_parsing_date(dispodate)

    def try_parsing_date(self,text):
        #Converting dates to propert YYYY-MM-DD format
        if text == None:
            return None
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y','%m/%d/%Y'):
            try:
              return datetime.strptime(text, fmt).date()
            except ValueError:
                pass
        return None #Means we couldn't convert the date

    def setExpungementEligability(self,expungementarray):
        #This right now is set by the Expungelator Class
        self.expungement_status = expungementarray['Expungement_Status']
        self.liability_waiver = expungementarray['Liability_Waiver']
        self.expungement_status_code = expungementarray['Expungement_Status_Code']