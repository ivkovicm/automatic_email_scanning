import oletools.oleid

oid = oletools.oleid.OleID("../samples/0dbdef9174ac0c1e1667bcc6f207f7ff14f35889028e266a579745c5d6790e60.xlsx")
indicators = oid.check()
test = oid.check_encrypted()
for i in indicators:
    print(i.id + "\t" + i.name + "\t" + i.type + "\t" + i.value)