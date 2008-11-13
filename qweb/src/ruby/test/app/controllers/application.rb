# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
	QWebRails.init
end
class MainController < ApplicationController
	def index
		@companies = [{"IDCOMPANY" => "1", "sCompanyName" => "IBM"}, {"IDCOMPANY" => "2", "sCompanyName" => "Microsoft"}]
		@f = f = $qweb.form(@params)
		unless f.is_submitted?
			f[:login].value = "agr"
		end
		if f.is_submitted?
			if f[:ok].is_clicked?
				# ok clicked
			end
			if f[:cancel].is_clicked?
				# cancel clicked
			end
			if f.is_submitted_but_invalid?
				# submitted but invalid
			end
			if f.is_submitted_and_valid?
				@u = f.data
			end
		end
		p default_template_name
	end
end
