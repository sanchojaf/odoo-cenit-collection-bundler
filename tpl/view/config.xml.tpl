<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>

        <record id="view_cenit_{name}_settings" model="ir.ui.view">
            <field name="name">{summary} settings</field>
            <field name="model">cenit.{name}.settings</field>
            <field name="arch" type="xml">
                <form string="Configure {summary}" class="oe_form_configuration">
                    <header>
                        <button string="Apply" type="object"
                                name="execute" class="oe_highlight"/>
                        or
                        <button string="Cancel" type="object"
                                name="cancel" class="oe_link"/>
                    </header>
                    <div>
                        <group string="{summary} settings">
{view_fields}
                        </group>
                    </div>
                </form>
            </field>
        </record>

        <record id="action_cenit_{name}_settings" model="ir.actions.act_window">
            <field name="name">{summary} settings</field>
            <field name="res_model">cenit.{name}.settings</field>
            <field name="view_mode">form</field>
            <field name="target">inline</field>
            <field name="view_id" ref="view_cenit_{name}_settings"/>
        </record>

        <menuitem id="menu_cenit_{name}_settings"
            parent="cenit_base.menu_cenit_integrations_settings"
            sequence="1" action="action_cenit_{name}_settings"/>

        <menuitem id="menu_cenit_{name}_settings_alt"
            parent="cenit_base.menu_cenit_integrations_settings_alt"
            sequence="1" action="action_cenit_{name}_settings"/>

    </data>
</openerp>
