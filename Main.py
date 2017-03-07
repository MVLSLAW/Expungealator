__author__ = 'Matthew Stubenberg'
__copyright__ = "Copyright 2017, Maryland Volunteer Lawyers Service"

from Expungealator import Expungealator
import sys, json
jsontest = '[{"Description":"FUGITIVE FROM JUSTICE -- VA","Disposition":"DISMISSED","DispositionDate":"2005-04-22"},{"Description":"RESISTING ARREST","Disposition":"STET","DispositionDate":"1992-09-02"},{"Description":"MAL DEST PROP\/VALU LESS 300","Disposition":"STET","DispositionDate":"1992-09-02"}]'

chargearray = json.loads(jsontest)
#chargearray = json.loads(sys.argv[1])

Expunge = Expungealator()
for charge in chargearray:
    Expunge.addCharge(charge['Description'], charge['Disposition'], charge['DispositionDate'])


result = Expunge.checkExpungementRegular()
comchargearray = Expunge.getAllCharges()

returndata = {}
returndata['Result'] = result

returndata['Charges'] = []

for comcharge in comchargearray:
    temp = {}
    temp['ERCode'] = comcharge['ExpungementRegularCode']
    temp['Description'] = comcharge['Description']
    temp['Disposition'] = comcharge['Disposition']
    returndata['Charges'].append(temp)

print(json.dumps(returndata))


