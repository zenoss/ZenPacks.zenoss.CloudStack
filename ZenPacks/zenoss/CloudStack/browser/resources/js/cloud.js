(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('CloudStackZone', _t('Zone'), _t('Zones'));
ZC.registerName('CloudStackPod', _t('Pod'), _t('Pods'));
ZC.registerName('CloudStackSystemVM', _t('System VM'), _t('System VMs'));
ZC.registerName('CloudStackRouterVM', _t('Router VM'), _t('Router VMs'));
ZC.registerName('CloudStackCluster', _t('Cluster'), _t('Clusters'));
ZC.registerName('CloudStackHost', _t('Host'), _t('Hosts'));
ZC.registerName('CloudStackVirtualMachine', _t('VM'), _t('VMs'));

Ext.apply(Zenoss.render, {
    CloudStack_entityLinkFromGrid: function(obj, col, record) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (this.subComponentGridPanel || this.componentType != obj.meta_type)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid+'\', \''+obj.meta_type+'\');">'+obj.title+'</a>';
        } else {
            return obj.title;
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

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.text == 'Components';
                }

                // Zenoss < 4.2 / ExtJS3
                return n.text == 'Components';
            });

        // Reset context of component card.
        var component_card = Ext.getCmp('component_card');

        if (components_node.data) {
            // Zenoss >= 4.2 / ExtJS4
            component_card.setContext(components_node.data.id, meta_type);
        } else {
            // Zenoss < 4.2 / ExtJS3
            component_card.setContext(components_node.id, meta_type);
        }

        // Select chosen row in component grid.
        component_card.selectByToken(uid);

        // Select chosen component type from tree.
        var component_type_node = components_node.findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.id == meta_type;
                }

                // Zenoss < 4.2 / ExtJS3
                return n.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});

ZC.CloudStackZonePanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackZone',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'pod_count'},
                {name: 'cluster_count'},
                {name: 'host_count'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackZonePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackZonePanel', ZC.CloudStackZonePanel);

ZC.CloudStackPodPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackPod',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'zone'},
                {name: 'cluster_count'},
                {name: 'host_count'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackPodPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackPodPanel', ZC.CloudStackPodPanel);

ZC.CloudStackSystemVMPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackSystemVM',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'host'},
                {name: 'systemvm_type'},
                {name: 'network_domain'},
                {name: 'public_ip'},
                {name: 'private_ip'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackSystemVMPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackSystemVMPanel', ZC.CloudStackSystemVMPanel);

ZC.CloudStackRouterVMPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackRouterVM',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'host'},
                {name: 'network_domain'},
                {name: 'public_ip'},
                {name: 'guest_ip'},
                {name: 'state'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
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
                id: 'guest_ip',
                dataIndex: 'guest_ip',
                header: _t('Guest IP'),
                sortable: true,
                width: 85
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackRouterVMPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackRouterVMPanel', ZC.CloudStackRouterVMPanel);

ZC.CloudStackClusterPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackCluster',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'host_count'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                panel: this
            },{
                id: 'zone',
                dataIndex: 'zone',
                header: _t('Zone'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackClusterPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackClusterPanel', ZC.CloudStackClusterPanel);

ZC.CloudStackHostPanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'CloudStackHost',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
                {name: 'managed_device'},
                {name: 'zone'},
                {name: 'pod'},
                {name: 'cluster'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'pod',
                dataIndex: 'pod',
                header: _t('Pod'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'cluster',
                dataIndex: 'cluster',
                header: _t('Cluster'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackHostPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackHostPanel', ZC.CloudStackHostPanel);

ZC.CloudStackVirtualMachinePanel = Ext.extend(ZC.CloudStackComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'display_name',
            componentType: 'CloudStackVirtualMachine',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'severity'},
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
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
                width: 140
            },{
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
                renderer: Zenoss.render.CloudStack_entityLinkFromGrid,
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
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.CloudStackVirtualMachinePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('CloudStackVirtualMachinePanel', ZC.CloudStackVirtualMachinePanel);

Zenoss.nav.appendTo('Component', [{
    id: 'component_pods',
    text: _t('Related Pods'),
    xtype: 'CloudStackPodPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'CloudStackZone') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.CloudStackPodPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_systemvms',
    text: _t('Related System VMs'),
    xtype: 'CloudStackSystemVMPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'CloudStackZone': return true;
            case 'CloudStackPod': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.CloudStackSystemVMPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_clusters',
    text: _t('Related Clusters'),
    xtype: 'CloudStackClusterPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'CloudStackZone': return true;
            case 'CloudStackPod': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.CloudStackClusterPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_hosts',
    text: _t('Related Hosts'),
    xtype: 'CloudStackHostPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        switch (navpanel.refOwner.componentType) {
            case 'CloudStackZone': return true;
            case 'CloudStackPod': return true;
            case 'CloudStackCluster': return true;
            default: return false;
        }
    },
    setContext: function(uid) {
        ZC.CloudStackHostPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('Related VMs'),
    xtype: 'CloudStackVirtualMachinePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'CloudStackZone') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.CloudStackVirtualMachinePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

})();
