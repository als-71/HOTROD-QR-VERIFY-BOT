from DiscordLib import MassDM


token = 'OTcyMjU2NTk3NzEzNzYwMzY2.GXRdXi.Z9GlEOXIYLAXbQoVpCIk3xigOvspM4PKDyPvzg'
thing = MassDM(token)

while True:
    thing.message_channel('977688906524921936')
    
thing.message_dms()