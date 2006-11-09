# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
	QWebRails.init
end
class MainController < ApplicationController
	def index
		@msg = []
		f = $qweb.form(@params)
		unless f.is_submitted?
			f[:login].value = "agr"
		end
		if f.is_submitted?
			@msg << "Form was submitted"
			if f[:ok].is_clicked?
				@msg << "Button ok has been clicked"
			end
			if f[:cancel].is_clicked?
				@msg << "Button cancel has been clicked"
			end
			if f.is_valid?
				@msg << "Form is valid !"
			end
		end
		p default_template_name
	end
end
