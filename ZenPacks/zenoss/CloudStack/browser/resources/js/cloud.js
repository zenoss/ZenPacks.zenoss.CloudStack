(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('Zone', _t('Zone'), _t('Zones'));
ZC.registerName('Pod', _t('Pod'), _t('Pods'));
ZC.registerName('SystemVM', _t('System VM'), _t('System VMs'));
ZC.registerName('Cluster', _t('Cluster'), _t('Clusters'));
ZC.registerName('Host', _t('Host'), _t('Hosts'));
ZC.registerName('VirtualMachine', _t('VM'), _t('VMs'));

Zenoss.types.TYPES.DeviceClass[0] = new RegExp(
    "^/zport/dmd/Devices(/(?!devices)[^/*])*/?$");

Zenoss.types.register({
    'Zone': "^/zport/dmd/Devices/.*/devices/.*/zones/[^/]*/?$",
    'Pod': "^/zport/dmd/Devices/.*/devices/.*/pods/[^/]*/?$",
    'SystemVM': "^/zport/dmd/Devices/.*/devices/.*/systemvms/[^/]*/?$",
    'Cluster': "^/zport/dmd/Devices/.*/devices/.*/clusters/[^/]*/?$",
    'Host': "^/zport/dmd/Devices/.*/devices/.*/hosts/[^/]*/?$",
    'VirtualMachine': "^/zport/dmd/Devices/.*/devices/.*/vms/[^/]*/?$"
});

Ext.apply(Zenoss.render, {
    entityLinkFromGrid: function(obj) {
        if (obj && obj.uid && obj.name) {
            if ( !this.panel || this.panel.subComponentGridPanel) {
                return String.format(
                    '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\'{0}\', \'{1}\');">{1}</a>',
                    obj.uid, obj.name);
            } else {
                return obj.name;
            }
        }
    },

    checkbox: function(bool) {
        if (bool) {
            return '<input type="checkbox" checked="true" disabled="true">';
        } else {
            return '<input type="checkbox" disabled="true">';
        }
    }
});

ZC.CloudStackComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,
    
    jumpToEntity: function(uid, name) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel,
            sm = tree.getSelectionModel(),
            compsNode = tree.getRootNode().findChildBy(function(n){
                return n.text=='Components';
            });
    
        var compType = Zenoss.types.type(uid);
        var componentCard = Ext.getCmp('component_card');
        componentCard.setContext(compsNode.id, compType);
        componentCard.selectByToken(uid);
        sm.suspendEvents();
        compsNode.findChildBy(function(n){return n.id==compType;}).select();
        sm.resumeEvents();
    }
});

ZC.ZonePanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'Zone',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'pod_count'},
                {name: 'cluster_count'},
                {name: 'host_count'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'pod_count',
                dataIndex: 'pod_count',
                header: _t('# Pods'),
                sortable: true,
                width: 80
            },{
                id: 'cluster_count',
                dataIndex: 'cluster_count',
                header: _t('# Clusters'),
                sortable: true,
                width: 80
            },{
                id: 'host_count',
                dataIndex: 'host_count',
                header: _t('# Hosts'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.ZonePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('ZonePanel', ZC.ZonePanel);

ZC.PodPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'Pod',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'zone'},
                {name: 'cluster_count'},
                {name: 'host_count'},
                {name: 'entity'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'cluster_count',
                dataIndex: 'cluster_count',
                header: _t('# Clusters'),
                sortable: true,
                width: 80
            },{
                id: 'host_count',
                dataIndex: 'host_count',
                header: _t('# Hosts'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.PodPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('PodPanel', ZC.PodPanel);

ZC.SystemVMPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'SystemVM',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'host'},
                {name: 'systemvm_type'},
                {name: 'network_domain'},
                {name: 'public_ip'},
                {name: 'private_ip'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'systemvm_type',
                dataIndex: 'systemvm_type',
                header: _t('Type'),
                sortable: true,
                width: 125
            },{
                id: 'network_domain',
                dataIndex: 'network_domain',
                header: _t('Network Domain'),
                sortable: true,
                width: 115
            },{
                id: 'public_ip',
                dataIndex: 'public_ip',
                header: _t('Public IP'),
                sortable: true,
                width: 85
            },{
                id: 'private_ip',
                dataIndex: 'private_ip',
                header: _t('Private IP'),
                sortable: true,
                width: 85
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.SystemVMPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('SystemVMPanel', ZC.SystemVMPanel);

ZC.ClusterPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'Cluster',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'host_count'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'host_count',
                dataIndex: 'host_count',
                header: _t('# Hosts'),
                sortable: true,
                width: 80
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.ClusterPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('ClusterPanel', ZC.ClusterPanel);

ZC.HostPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'Host',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'managed_device'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'cluster'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this
            },{
                id: 'managed_device',
                dataIndex: 'managed_device',
                header: _t('Managed Device'),
                renderer: function(obj) {
                    if (obj && obj.uid && obj.name) {
                        return Zenoss.render.link(obj.uid, undefined, obj.name);
                    }
                },
                width: 140
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'cluster',
                dataIndex: 'cluster',
                header: _t('Cluster'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.HostPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('HostPanel', ZC.HostPanel);

ZC.VirtualMachinePanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'display_name',
            componentType: 'VirtualMachine',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'display_name'},
                {name: 'account'},
                {name: 'managed_device'},
                {name: 'zone'},
                {name: 'host'},
                {name: 'cpu_number'},
                {name: 'cpu_speed'},
                {name: 'memory'},
                {name: 'state'},
                {name: 'monitor'},
                {name: 'monitored'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.entityLinkFromGrid,
                panel: this,
                width: 140
            },{
                id: 'display_name',
                dataIndex: 'display_name',
                header: _t('Display Name'),
                sortable: true
            },{
                id: 'account',
                dataIndex: 'account',
                header: _t('Account'),
                sortable: true
            },{
                id: 'managed_device',
                dataIndex: 'managed_device',
                header: _t('Managed Device'),
                renderer: function(obj) {
                    if (obj && obj.uid && obj.name) {
                        return Zenoss.render.link(obj.uid, undefined, obj.name);
                    }
                },
                width: 140
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.entityLinkFromGrid,
                width: 140
            },{
                id: 'cpu_total',
                dataIndex: 'cpu_number',
                header: _t('CPU'),
                renderer: function(name, col, record) {
                    var item = record.data;
                    if (item.cpu_number && item.cpu_speed) {
                        return (item.cpu_number * item.cpu_speed) + ' MHz';
                    }

                    return "Unknown";
                },
                sortable: true,
                width: 70
            },{
                id: 'memory',
                dataIndex: 'memory',
                header: _t('Memory'),
                renderer: Zenoss.render.memory,
                sortable: true,
                width: 70
            },{
                id: 'state',
                dataIndex: 'state',
                header: _t('State'),
                sortable: true,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            }]
        });
        ZC.VirtualMachinePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('VirtualMachinePanel', ZC.VirtualMachinePanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pods',
    text: _t('Related Pods'),
    xtype: 'PodPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'Zone') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.PodPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_systemvms',
    text: _t('Related System VMs'),
    xtype: 'SystemVMPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'Zone': return true;
            case 'Pod': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.SystemVMPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_clusters',
    text: _t('Related Clusters'),
    xtype: 'ClusterPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'Zone': return true;
            case 'Pod': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.ClusterPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_hosts',
    text: _t('Related Hosts'),
    xtype: 'HostPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'Zone': return true;
            case 'Pod': return true;
            case 'Cluster': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.HostPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('Related VMs'),
    xtype: 'VirtualMachinePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'Zone') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.VirtualMachinePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

})();
