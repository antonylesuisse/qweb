# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
	QWebRails.include self
end
class MainController < ApplicationController
	def index
		f = $qweb.form("main/index", {}, @request)
		p default_template_name
	end
end
