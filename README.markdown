# ZenPacks.zenoss.CloudStack
Please watch the [Monitoring CloudStack][] video for a quick introduction that
covers most of the details below.

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

 * Zenoss 4.1: [Latest Package for Python 2.7][]
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
_Add CloudStack_. Fill out the _URL_, _API Key_, and _Secret Key_ fields then
click _OK_. The URL should only include the protocol, host and port
(i.e. _http://cloudstack.example.com/_). You can find or create the keys by
logging into the CloudStack web interface and navigate to Accounts and users.

Zenoss will then add the CloudStack device to the system along with all of its
associated zones, pods and clusters. Monitoring will also start after
the discovery is complete.

### Metrics
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

### Events
CloudStack has both alerts and events. Once you've successfully added a
CloudStack cloud to Zenoss you will automatically receive all CloudStack alerts
as events in Zenoss. You will also automatically receive all CloudStack events.
However, the events will go straight into your event history by default.

To avoid overloading CloudStack and Zenoss, only the last two (2) days of
events will be checked. This allows for timezone discrepency between the Zenoss
and CloudStack servers as well as some downtime without missing events. There
is no real-time event collection mechanism with the CloudStack API, so alerts
and events will only be polled once per minute.

## What's Next
The CloudStack management server is Java-based, specifically Tomcat. So there
is a possibility to use JMX to get useful metrics out of the management server
itself to watch its health and capacity.

Simple process and port checks could also be added for the Tomcat application
server.

## Screenshots
![Add CloudStack](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_add.png)
![Graphs 1](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs1.png)
![Graphs 2](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs2.png)
![Graphs 3](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_graphs3.png)
![Zones](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_zones.png)
![Pods](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_pods.png)
![Clusters](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_clusters.png)
![Hosts](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_hosts.png)
![Events](https://github.com/zenoss/ZenPacks.zenoss.CloudStack/raw/master/screenshots/cloudstack_events.png)


[Monitoring CloudStack]: <http://www.youtube.com/watch?v=3hr2H9iMz_o>
[Zenoss]: <http://www.zenoss.com/>
[Latest Package for Python 2.7]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.CloudStack/ZenPacks.zenoss.CloudStack-0.7.4-py2.7.egg>
[Latest Package for Python 2.6]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.CloudStack/ZenPacks.zenoss.CloudStack-0.7.4-py2.6.egg>
