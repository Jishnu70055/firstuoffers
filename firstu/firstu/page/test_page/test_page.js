frappe.pages['test-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'test page',
		single_column: true
		
	});
	page.set_title('Test Page')
	page.set_title_sub('Subtitle')
	page.set_indicator('Pending', 'orange')
	page.clear_indicator()
	let $btn = page.set_primary_action('New', () => create_new(), 'octicon octicon-plus')
	// page.clear_primary_action()
	// let $btn = page.set_secondary_action('Refresh', () => refresh(), 'octicon octicon-sync')
	// page.clear_secondary_action()
	page.add_menu_item('Send Email', () => open_email_dialog())
	page.add_menu_item('Send Email', () => open_email_dialog(), true)
	page.clear_menu()
	// page.add_action_item('Delete', () => delete_items())
	page.add_inner_button('Update Posts', () => update_posts())
	page.add_inner_button('New Post', () => new_post(), 'Make')
	let field = page.add_field({
		label: 'Status',
		fieldtype: 'Select',
		fieldname: 'status',
		options: [
			'Open',
			'Closed',
			'Cancelled'
		],
		change() {
			console.log(field.get_value());
		}
	});
	
}