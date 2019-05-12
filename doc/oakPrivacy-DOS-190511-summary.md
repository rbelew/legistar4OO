### OpenOakland Day of Service - OaklandPrivacy project

* 11 May 2019

Project [repo is here](https://github.com/rbelew/legistar4OO).  The
main script is
[legistar4OO.py](https://github.com/rbelew/legistar4OO/blob/master/src/legistar4OO.py),
~400 lines of Python.  There are is some test/preliminary data in the
[data subdirectory](https://github.com/rbelew/legistar4OO/tree/master/data).

The project began from an ask from
[OaklandPrivacy.org](https://oaklandprivacy.org/), to capture
municipalities' meeting information, as required by
[California's Brown Act](https://en.wikipedia.org/wiki/Brown_Act).
They have special interest in agendas across many Bay Area cities.
Not surprisingly, we dug into the situation in Oakland most deeply.
One of the happiest messages of our day was that *similar tricks can
be applied to four other municipalities!*

Tracy of OaklandPrivacy provided a list of 25 city and county
"municipalities" of interest to OaklandPrivacy.  Pretty quickly our
group was able to identify the public-facing URLs for all cities'
calendars.  (This was the best part of the day:  all of us adding 
information to various cells, towards a shared data resource!)
We have captured municipalities' URLs and whether they are
Legistar clients (see below) in this
[spreadsheet of other cities' data](https://github.com/rbelew/legistar4OO/blob/master/data/otherCities.csv).

Oakland uses a system called
[Legistar](https://support.granicus.com/s/article/Legistar), sold by
Granicus.  Happily, four other municipalities also use Legistar.  The
current version works only on municipalities using
[Legistar](https://support.granicus.com/s/article/Legistar) software.
As an example, for Oakland the
[public-facing calendar](https://oakland.legistar.com/Calendar.aspx)
has a matching
[API interface](http://webapi.legistar.com/v1/oakland/Bodies).  

Using these starting points for Oakland and the 4 other
municipalities, we were able to successfully query all of them for
information about each of their "bodies" (councils, committees,
sub-committees, offices, ...); the result is
[this (sqlite) database](https://github.com/rbelew/legistar4OO/blob/master/data/legistar_cityBodies.db),
and
[snapshot of the `Body` relation in this CSV file](https://github.com/rbelew/legistar4OO/blob/master/data/bodies.csv).

## Next steps, 

* There is active work on
  [two branches](https://github.com/rbelew/legistar4OO/tree/email/,
  https://github.com/rbelew/legistar4OO/tree/emailDB/) attempting to
  take the resulting meeting data and emailing it to interested
  parties.  This might be combined with
  [work in OO's CouncilMatic project that Tweet's meeting information](https://github.com/openoakland/councilmatic/blob/develop/Tweeter.py)
  it gets (from scraping the public facing Oakland Legistar calendar).
  
* All our work has assumed the Legistar API.  "Scraping" and/or other
  API access to non-Legistar municipalities, other sites, perhaps as
  OO's [CouncilMatic](http://councilmatic.aws.openoakland.org/pc/)
  project is currently doing.

