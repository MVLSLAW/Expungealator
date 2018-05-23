__author__ = 'Matthew Stubenberg'
__copyright__ = "Copyright 2017, Maryland Volunteer Lawyers Service"

from Expungealator import Expungealator
import sys, json
from Charge import Charge
jsontest = '[{"Description":"FUGITIVE FROM JUSTICE -- VA","Disposition":"DISMISSED","DispositionDate":"2005-04-22","CJIS":"1 0233","Statute":"CR.5.601.(a)(1)"},{"Description":"THEFT","Disposition":"GUILTY","DispositionDate":"2017-09-02","CJIS":"1 1415","Statute":"CR.3.203"},{"Description":"MAL DEST PROP\/VALU LESS 300","Disposition":"STET","DispositionDate":"1992-09-02","CJIS":"4 3550","Statute":"CR.6.402"}]'

chargearray = json.loads(jsontest)
#chargearray = json.loads(sys.argv[1])

Expunge = Expungealator()
charges = []
for charge in chargearray:
    charges.append(Charge())
    charges[-1].setDescription(charge['Description'])
    charges[-1].setDisposition(charge['Disposition'])
    charges[-1].setDispositionDate(charge['DispositionDate'])
    charges[-1].setCJIS(charge['CJIS'])
    charges[-1].setStatute(charge['Statute'])


Expunge.setChargeArray(charges)
exstatus = Expunge.checkCaseExpungeability()
chargearray = Expunge.chargearray

for charge in chargearray:
    print(charge.expungement_status + " " + str(charge.expungement_status_code))

print("Over All Expungeability: " + exstatus)