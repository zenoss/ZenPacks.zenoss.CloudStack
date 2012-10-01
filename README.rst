===============================================================================
ZenPacks.zenoss.CloudStack
===============================================================================

Please watch the `Monitoring CloudStack`_ video for a quick introduction that
covers most of the details below. Note that this video was recorded with
version 0.7.0 of the ZenPack. The discovery and monitoring of system, router
and regular VMs has since been added.


About
===============================================================================

This project is a Zenoss_ extension (ZenPack) that allows for monitoring of
CloudStack. An explanation of what CloudStack is can be found at
`<http://cloudstack.org/>`_::

> CloudStack is open source software written in java that is designed to deploy
> and manage large networks of virtual machines, as a highly available,
> scalable cloud computing platform. CloudStack current supports the most
> popular open source hypervisors VMware, Oracle VM, KVM, XenServer and Xen
> Cloud Platform. CloudStack offers three ways to manage cloud computing
> environments: a easy-to-use web interface, command line and a full-featured
> RESTful API.


Features
-------------------------------------------------------------------------------

Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've successfully added a CloudStack cloud to Zenoss you will begin to
see the following metrics available for the entire cloud. These numbers are
aggregated from all zones, pods, clusters and hosts.

* Public IPs: Total and Used
* Private IPs: Total and Used
* Memory: Total (with and without over-provisioning), Allocated and Used
* CPU: Total (with and without over-provisioning), Allocated and Used
* Primary Storage: Total (with and without over-provisioning), Allocated and
  Used
* Secondary Storage: Total and Used
* Network: Read and Write

The same list of metrics are available for each zone. The same metrics with the
exception of public IPs and secondary storage are also available for each pod.

The following metrics are available aggregated to each cluster, and for each
host.

* Memory: Total and Used
* CPU: Total (with and without over-provisioning), Allocated, Used and Cores
* Network: Read and Write


Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudStack has both alerts and events. Once you've successfully added a
CloudStack cloud to Zenoss you will automatically receive all CloudStack alerts
as events in Zenoss. You will also automatically receive all CloudStack events.
However, the events will go straight into your event history by default.

To avoid overloading CloudStack and Zenoss, only the last two (2) days of
events will be checked. This allows for timezone discrepency between the Zenoss
and CloudStack servers as well as some downtime without missing events. There
is no real-time event collection mechanism with the CloudStack API, so alerts
and events will only be polled once per minute.


Prerequisites
-------------------------------------------------------------------------------

======================  ====================================================
Prerequisite            Restriction
======================  ====================================================
Zenoss Platform         3.2 or greater
Zenoss Processes        zenmodeler, zencommand
Installed ZenPacks      ZenPacks.zenoss.CloudStack
Firewall Acccess        Collector server to 80/tcp or 443/tcp of CloudStack
                        API server
CloudStack Versions     2.2.4 and later
CloudStack Credentials  Admin role in ROOT domain
======================  ====================================================


Usage
===============================================================================

Installation
-------------------------------------------------------------------------------

This ZenPack has no special installation considerations. You should install the
most recent version of the ZenPack for the version of Zenoss you're running.

The ZenPack can be downloaded from `<http://zenpacks.zenoss.com/>`_.

To install the ZenPack you must copy the ``.egg`` file to your Zenoss master
server and run the following command as the ``zenoss`` user::

    zenpack --install <filename.egg>

After installing you must restart Zenoss by running the following command as
the ``zenoss`` user on your master Zenoss server::

    zenoss restart

If you have distributed collectors you must also update them after installing
the ZenPack.


Configuring
-------------------------------------------------------------------------------

Installing the ZenPack will add the following items to your Zenoss system.

* Device Classes

  * /CloudStack

* Configuration Properties

  * zCloudStackURL
  * zCloudStackAPIKey
  * zCloudStackSecretKey

* Modeler Plugins

  * zenoss.CloudStack

* Monitoring Templates

  * Cloud
  * Zone
  * Pod
  * Cluster
  * Host

* Event Classes

  * /Status/CloudStack
  * /Perf/CloudStack
  * /App/CloudStack

The easiest way to start monitoring CloudStack is to navigate to the
Infrastructure page, click the *+* menu to add a device and choose
*Add CloudStack*. Fill out the *URL*, *API Key*, and *Secret Key* fields then
click *OK*. The URL should only include the protocol, host and port
(i.e. *http://cloudstack.example.com/*). You can find or create the keys by
logging into the CloudStack web interface and navigate to Accounts and users.

Zenoss will then add the CloudStack device to the system along with all of its
associated zones, pods and clusters. Monitoring will also start after
the discovery is complete.


Removal
-------------------------------------------------------------------------------

To remove this ZenPack you must run the following command as the ``zenoss``
user on your master Zenoss server::

    zenpack --remove ZenPacks.zenoss.CloudStack

You must then restart the master Zenoss server by running the following command
as the ``zenoss`` user::

    zenoss restart


Change Log
===============================================================================

**1.0.6** - 2012-10-01
---------------------

* Fix for "No data retuned for command" events. (`ZEN-3442`_)
* Fix for ZeroDivisionError in zencommand.log (`ZEN-3582`_)
* Fix for de-duplication of alerts and events.


.. _ZEN-3442: http://jira.zenoss.com/jira/browse/ZEN-3442
.. _ZEN-3582: http://jira.zenoss.com/jira/browse/ZEN-3582


**1.0.5** - 2012-08-10
----------------------

* Updated to support Zenoss 4.2.

* Fix event polling to support CloudStack management servers generating up to
  10,000 events per hour. The previous mechanism only supported 208 events per
  hour.


**1.0.4** - 2012-06-29
----------------------

* Updated to support CloudStack 3 (Acton).

* Fix for bug related to hosts that don't report `memoryused`.

* Fix for *No data returned* events.

* Fix for cases where the CloudStack database reports the wrong zone for a VM.


**1.0.2** - 2012-03-15
----------------------

* Updated to support Zenoss 4.1.

* Restrict system VM "touch test" to KVM hosts.


**0.9.5** - 2012-01-21
----------------------

* Added Dynamic View and Impact adapters.

* Various minor bug fixes.


**0.9.0** - 2012-01-20
----------------------

* Added discovery and monitoring of router VMs.

* Added discovery and monitoring of all VMs.


**0.8.0** - 2012-01-19
----------------------

* Removed maximum limit on over-allocatable utilization metrics.

* Added discovery and monitoring of console proxies and other system VMs.

* Add file-touch monitoring of system VMs to catch read-only file systems on
  system VMs.


**0.7.0** - 2011-11-01
-----------------------------------------------------------------------------

* Initial alpha release.


Screenshots
===============================================================================

* *Add CloudStack*

  |Add CloudStack|

* *Graphs 1*

  |Graphs 1|

* *Graphs 2*

  |Graphs 2|

* *Graphs 3*

  |Graphs 3|

* *Zones*

  |Zones|

* *Pods*

  |Pods|

* *Clusters*

  |Clusters|

* *Hosts*

  |Hosts|

* *Events*

  |Events|


.. _`Monitoring CloudStack`: http://www.youtube.com/watch?v=3hr2H9iMz_o
.. _Zenoss: http://www.zenoss.com/

.. |Add CloudStack| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_add.png
.. |Graphs 1| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs1.png
.. |Graphs 2| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs2.png
.. |Graphs 3| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs3.png
.. |Zones| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_zones.png
.. |Pods| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_pods.png
.. |Clusters| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_clusters.png
.. |Hosts| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_hosts.png
.. |Events| image:: https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_events.png
