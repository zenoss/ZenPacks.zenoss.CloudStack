(function(){

var add_cloudstack = new Zenoss.Action({
    text: _t('Add CloudStack') + '...',
    id: 'addcloudstack-item',
    permission: 'Manage DMD',
    handler: function(btn, e){
        var win = new Zenoss.dialog.CloseDialog({
            width: 300,
            title: _t('Add CloudStack'),
            items: [{
                xtype: 'form',
                buttonAlign: 'left',
                monitorValid: true,
                labelAlign: 'top',
                footerStyle: 'padding-left: 0',
                border: false,
                items: [{
                    xtype: 'textfield',
                    name: 'url',
                    fieldLabel: _t('URL'),
                    id: "cloudstackURLField",
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'api_key',
                    fieldLabel: _t('API Key'),
                    id: "cloudstackAPIKeyField",
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'secret_key',
                    fieldLabel: _t('Secret Key'),
                    id: "cloudstackSecretKeyField",
                    width: 260,
                    allowBlank: false
                }],
                buttons: [{
                    xtype: 'DialogButton',
                    id: 'addCloudStackdevice-submit',
                    text: _t('Add'),
                    formBind: true,
                    handler: function(b) {
                        var form = b.ownerCt.ownerCt.getForm();
                        var opts = form.getFieldValues();
                        
                        Zenoss.remote.CloudStackRouter.add_cloudstack(opts,
                        function(response) {
                            if (response.success) {
                                new Zenoss.dialog.SimpleMessageDialog({
                                    message: _t('Add CloudStack job submitted.'),
                                    buttons: [{
                                        xtype: 'DialogButton',
                                        text: _t('OK')
                                    }, {
                                        xtype: 'button',
                                        text: _t('View Job Log'),
                                        handler: function() {
                                            window.location =
                                                '/zport/dmd/JobManager/jobs/' +
                                                response.jobId + '/viewlog';
                                        }
                                    }]
                                }).show();
                            }
                            else {
                                new Zenoss.dialog.SimpleMessageDialog({
                                    message: response.msg,
                                    buttons: [{
                                        xtype: 'DialogButton',
                                        text: _t('OK')
                                    }]
                                }).show();
                            }
                        });
                    }
                }, Zenoss.dialog.CANCEL]
            }]
        });
        win.show();
    }
});

// Push the addOpenStack action to the adddevice button
Ext.ns('Zenoss.extensions');
Zenoss.extensions.adddevice = Zenoss.extensions.adddevice instanceof Array ?
                              Zenoss.extensions.adddevice : [];
Zenoss.extensions.adddevice.push(add_cloudstack);

}());
