import sickbeard

Sickbeard = sickbeard.SB()

__tvdbid__ = sys.argv[1]

Sickbeard.ForceSearch(__tvdbid__)
