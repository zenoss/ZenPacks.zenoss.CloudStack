(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('Zone', _t('Zone'), _t('Zones'));
ZC.registerName('Pod', _t('Pod'), _t('Pods'));
ZC.registerName('Cluster', _t('Cluster'), _t('Clusters'));
ZC.registerName('Host', _t('Host'), _t('Hosts'));

Zenoss.types.TYPES.DeviceClass[0] = new RegExp(
    "^/zport/dmd/Devices(/(?!devices)[^/*])*/?$");

Zenoss.types.register({
    'Zone': "^/zport/dmd/Devices/.*/devices/.*/zones/[^/]*/?$",
    'Pod': "^/zport/dmd/Devices/.*/devices/.*/pods/[^/]*/?$",
    'Cluster': "^/zport/dmd/Devices/.*/devices/.*/clusters/[^/]*/?$",
    'Host': "^/zport/dmd/Devices/.*/devices/.*/hosts/[^/]*/?$"
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
                {name: 'zone'},
                {name: 'pod'},
                {name: 'cluster'},
                {name: 'host_device'},
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
                id: 'host_device',
                dataIndex: 'host_device',
                header: _t('Device'),
                renderer: function(obj) {
                    if (obj && obj.uid && obj.name) {
                        return Zenoss.render.link(obj.uid, undefined, obj.name);
                    }
                },
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

})();
