=======================
collective.gamoderation
=======================

.. contents:: Table of Contents

Introduction
------------

This package provides a way to moderate results obtained from Google Analytics.
It allows to setup different channels to obtain data and configure filtering.
It also provides a portlet that will display a list of URL's returned by one of your configured channels.
This product depends and uses `collective.googleanalytics`_

Installation
------------

To install collective.gamoderation, add it to the eggs section of your buildout. Then re-run buildout, restart Zope and install it from the Plone control panel or from the quickinstaller.

Usage
-----

As a first step, you need to go to the "Google Analytics" configlet and authorize your account. Then, go to the "Reports" tab and choose a profile from the drop down. There is no need to tick any report.

Once you have your account setup, you can go to the "Google Analytics (Moderation)" configlet to start configuring your channels.

From here you can see several widgets:
"Moderated channels" lets you add, remove and select channels. To add a new one, put the name and click "add".

If you add several channels, you can switch between them by choosing it from the drop down, and clicking "Select".

When you are in one of these channels, you can choose to use a Google Analytics Report, which is a very flexible way to query google analytics. In order to learn more about reports and how to configure or add them, read `Using Reports`_ section of the googleanalytics package.

If you don't want to use reports to get the data, you can specify a script id in the "custom query" field, which will be used to get results. Bear in mind that if you have a report selected, it will try to use it over the script, so for the script to work, you have to select None from the reports drop-down.

The system expects the returned value is as Google Analytics returns it, ie. a list of dictionaries, and, at the moment, it must contain at least the 'ga:pagePath' dimension to work properly.

example of a valid output from the query script: [{'ga:pagePath': '/folder/page'},{'ga:pagePath': '/folder/another-page'}]

Next, it is the "results filter" field, which will be used to filter the results obtained either from the report or from the "custom query" script. This script should return the list in the same format as the previous one and should only include the items that should pass through (ie. it should not return the items that don't want to be displayed)

The next 2 fields, allow you to specify hosts to identify in the results.

"ga:pagePath includes host"

Mark this checkbox if the ga:pagePath for the given report is including a host (That is, an initial part in the form of www.something.com or similar).
In the "Block results" field below, you should see a preview of items returned by Google Analytics. If the elements include a host, you need to mark this checkbox.

"Site hosts"

Along with the previous field, you need to list here all the different hosts that point to this site. You will need to list 1 element per line. So, for example, if "www.something.com" and "something.com" point to the site, you will then need to enter here:

www.something.com
something.com

Finally, there is the "Block results" field, which will get the report output or "custom query" output, and show it, so you can manually block entries.
Entries that do not match the "results filter" (ie. entries that are not going to be included in the final list) are colored red.

There's also a portlet included, that will allow you to choose between the list of channels to render. The portlet creates the full URL and gets the page's title, based on a reconstruction done from the path that Google Analytics returns, assuming is a relative path from site root, and if it doesn't find an entry, it will just ignore it.

Reading the filtered data
-------------------------

The package provides a helper view, that will return the filtered results for a given channel, as JSON. The view is called "@@filtered-results".
This view returns Cache headers for 30 minutes.

Internal cache
--------------

The results are cached internally, for 1 hour. If you don't see changes in your portlet this is why.
To refresh the cache, you can call a "@@update-results" view, that will just return nothing, but it will refresh the saved data.
Restarting the instance makes it to loose all cached results.

TODO
----

  * Provide a way to specify users for each channel, that are allowed to modify it.
  * Provide a controlpanel-like tool for those users to make changes.
  * Automated testing.

.. _`collective.googleanalytics`: https://pypi.python.org/pypi/collective.googleanalytics
.. _`Using Reports`: https://pypi.python.org/pypi/collective.googleanalytics#using-reports