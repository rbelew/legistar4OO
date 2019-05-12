### OpenOakland Day of Service - OaklandPrivacy project

* 11 May 2019

Project [repo is here](https://github.com/rbelew/legistar4OO).  The
main script is
[legistar4OO.py](https://github.com/rbelew/legistar4OO/blob/master/src/legistar4OO.py),
~400 lines of Python.  There are is some test/preliminary data in the
[data subdirectory](https://github.com/rbelew/legistar4OO/tree/master/data).

The project began from an ask from
[OaklandPrivacy.org](https://oaklandprivacy.org/), to capture
municipalities' meeting information as, I required by
[California's Brown Act](https://en.wikipedia.org/wiki/Brown_Act).
They have special interest in agendas across many Bay Area cities.
Not Surprisingly, we dug into the situation in Oakland most deeply.
One of the happiest messages of our day was that *similar tricks can
be applied to four other municipalities!*

Tracy of OaklandPrivacy provided a list of 25 city and county
"municipalities" of interest to OaklandPrivacy.  Pretty quickly our
group was able to identify the public-facing URLs for all cities'
calendars.  We have captured municipalities' URLs and whether they are
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
