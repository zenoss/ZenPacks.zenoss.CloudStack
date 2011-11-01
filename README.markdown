# ZenPacks.zenoss.CloudStack
Please watch the [Monitoring CloudStack][] video for a quick introduction that
covers most of the details below.

**Important!** This ZenPack is currently a placeholder and the functionality
described below doesn't yet exist. At this point it describes what the ZenPack
will be once the first full version is done.

## About
This project is a [Zenoss][] extension (ZenPack) that allows for monitoring of
CloudStack. An explanation of what CloudStack is can be found at
<http://cloudstack.org/>.

> CloudStack is open source software written in java that is designed to deploy
> and manage large networks of virtual machines, as a highly available,
> scalable cloud computing platform. CloudStack current supports the most
> popular open source hypervisors VMware, Oracle VM, KVM, XenServer and Xen
> Cloud Platform. CloudStack offers three ways to manage cloud computing
> environments: a easy-to-use web interface, command line and a full-featured
> RESTful API.

## Credits
I'd like to thank David Nalley for all of his help with the CloudStack API and
for helping me to understand what in CloudStack would be useful to monitor.

## Requirements & Dependencies
This ZenPack is known to be compatible with Zenoss versions 3.2 through 4.0.

All of the monitoring current supported is performed using the CloudStack API.
It is expected that your CloudStack is running API version 2.2.4 or later, and
that the API and secret keys be that of a full administrative user.

## Installation
You must first have, or install, Zenoss 3.2.0 or later. Core and Enterprise
versions are supported. You can download the free Core version of Zenoss from
<http://community.zenoss.org/community/download>.

### Normal Installation (packaged egg)
Depending on what version of Zenoss you're running you will need a different
package. Download the appropriate package for your Zenoss version from the list
below.

 * Zenoss 3.0 - 4.0: [Latest Package for Python 2.6][]

Then copy it to your Zenoss server and run the following commands as the zenoss
user.

    zenpack --install <package.egg>
    zenoss restart

### Developer Installation (link mode)
If you wish to further develop and possibly contribute back you should clone
the git repository, then install the ZenPack in developer mode using the
following commands.

    git clone git://github.com/zenoss/ZenPacks.zenoss.CloudStack.git
    zenpack --link --install ZenPacks.zenoss.CloudStack
    zenoss restart

## Usage
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
Infrastructure page, click the _+_ menu to add a device and choose
_Add CloudStack_. Fill out the _URL_, API Key_, and _Secret Key_ fields then
click _OK_. You can find or create the keys by logging into the CloudStack web
interface and navigate to Accounts and users.

Zenoss will then add the CloudStack device to the system along with all of its
associated zones, pods and clusters. Monitoring will also start after
the discovery is complete.

### Metrics
Once you've successfully added a CloudStack to Zenoss you will begin to see the
following metrics collected and trended over time for individual clusters and
aggregated up to each pod, zone and to the cloud as a whole.

  * CPU Capacity: used, allocated, free
  * Memory Capacity: used, allocated, free
  * Primary Storage: allocated, consumed
  * Public IP Addresses: used, available
  * VMs: running, stopped, expungable

Additionally the following metrics are available only per zone and aggregated
to the cloud as a whole.

  * Secondary Storage: consumption

## What's Next
The CloudStack management server is Java-based, specifically Tomcat. So there
is a possibility to use JMX to get useful metrics out of the management server
itself to watch its health and capacity.

Simple process and port checks could also be added for the Tomcat application
server.

## Screenshots
![TODO](TODO)


[Monitoring CloudStack]: <TODO>
[Zenoss]: <http://www.zenoss.com/>
[Latest Package for Python 2.6]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.CloudStack/ZenPacks.zenoss.CloudStack-0.7.0-py2.6.egg>
