openerp.npg_project = function(instance) {
    instance.npg_project.view_list = instance.web.form.One2ManyList.extend({
    pad_table_to: function (count) {
        if (!this.view.is_action_enabled('create')) {
            this._super(count);
        } else {
            this._super(count > 0 ? count - 1 : 0);
        }

        // magical invocation of wtf does that do
        if (this.view.o2m.get('effective_readonly')) {
            return;
        }

        var self = this;
        var columns = _(this.columns).filter(function (column) {
            return column.invisible !== '1';
        }).length;
        if (this.options.selectable) { columns++; }
        if (this.options.deletable) { columns++; }

        if (!this.view.is_action_enabled('create')) {
            return;
        }

        var $cell = $('<td>', {
            colspan: columns,
            'class': 'oe_form_field_one2many_list_row_add'
        }).append(
            $('<a>', {href: '#'}).text(_t("Add new item"))
                .mousedown(function () {
                    // FIXME: needs to be an official API somehow
                    if (self.view.editor.is_editing()) {
                        self.view.__ignore_blur = true;
                    }
                })
                .click(function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    // FIXME: there should also be an API for that one
                    if (self.view.editor.form.__blur_timeout) {
                        clearTimeout(self.view.editor.form.__blur_timeout);
                        self.view.editor.form.__blur_timeout = false;
                    }
                    self.view.ensure_saved().done(function () {
                        self.view.do_add_record();
                    });
                }));

        var $padding = this.$current.find('tr:not([data-id]):first');
        var $newrow = $('<tr>').append($cell);
        if ($padding.length) {
            $padding.prepend($newrow);
        } else {
            this.$current.prepend($newrow)
        }
    }
});
};
