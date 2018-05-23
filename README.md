# Expungealator
Used to determine expungeability for Maryland Criminal Cases
## Updates
I have started to add JRA crimes and search by CJIS code example. It checks a large CSV file for matches but more testing needs to be done.

## Usage
The Expungealator class needs 3 variables. The description, disposition, and the disposition date of each charge in a case. The "Main.py" is an example of how to use the class. Main.py adds
several charges to an expungealator object. It then runs the function checkExpungementRegular() which returns whether the case is eligible or not. Note that you can get the result of each
charge by calling the getAllCharges() function. This has some added benefits like the ExpungementRegularCode which will tell you exactly what category the program put that charge into. This can be useful
for later finding all guilty convictions where we were unsure of whether the amount of marijuana was under 10 grams.
<pre>
samplecharges = '[{"Description":"FUGITIVE FROM JUSTICE -- VA","Disposition":"DISMISSED","DispositionDate":"2005-04-22"},{"Description":"RESISTING ARREST","Disposition":"STET","DispositionDate":"1992-09-02"},{"Description":"MAL DEST PROP\/VALU LESS 300","Disposition":"STET","DispositionDate":"1992-09-02"}]'
chargearray = json.loads(samplecharges)
Expunge = Expungealator()
for charge in chargearray:
    Expunge.addCharge(charge['Description'], charge['Disposition'], charge['DispositionDate'])


result = Expunge.checkExpungementRegular()
</pre>

## Coming Soon
- Shielding
- Justice Reinvestment Act Expungeabilty

## Needed Help
Much of the determination for whether a charge description is a DUI or a marijuana case is done by comparing it to a master list. While we capture lots of possible ways to spell the various ways,
we need some help in checking to make sure we got all of them.

Needs active case missing field error prevention code.